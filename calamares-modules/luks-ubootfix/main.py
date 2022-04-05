#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   SPDX-FileCopyrightText: 2022 Arjen Balfoort <arjenbalfoort@hotmail.com>
#   SPDX-License-Identifier: GPL-3.0-or-later
#

import os
import re
import subprocess
import libcalamares

def run():
    root_mount_point = libcalamares.globalstorage.value("rootMountPoint")
    if root_mount_point:
        partitions = libcalamares.globalstorage.value("partitions")
        crypttab_path = os.path.join(root_mount_point, "etc", "crypttab")
        key_file = os.path.join(root_mount_point, "crypto_keyfile.bin")
        unencrypted_boot = False
        root_luksUuid = None
        enc_devices = []

        # Check if /boot is unencrypted and / is encrypted
        for partition in partitions:
            has_luks = "luksMapperName" in partition
            if partition["mountPoint"] == "/boot" and not has_luks:
                unencrypted_boot = True
            elif partition["mountPoint"] == "/" and has_luks:
                root_luksUuid = partition["luksUuid"]
            elif has_luks:
                # Save encrypted devices and passphrases
                enc_devices.append((partition["device"], partition["luksPassphrase"]))

        if unencrypted_boot and root_luksUuid and os.path.exists(crypttab_path):
            libcalamares.utils.debug("Set password to none for / partition {!s} in {!s}".format(root_luksUuid, crypttab_path))
            # Fix crypttab: set password to none for / partition
            with open(crypttab_path, 'r+') as f:
                txt = f.read()
                txt = re.sub("UUID={!s}.*".format(root_luksUuid),
                             "UUID={!s}     none".format(root_luksUuid),
                             txt)
                f.seek(0)
                f.write(txt)
                f.truncate()

            with open(crypttab_path, "r") as f:
                libcalamares.utils.debug(f.read())

            if not os.path.exists(key_file) and len(enc_devices) > 0:
                libcalamares.utils.debug("Create key file: {!s}".format(key_file))
                # Create /crypto_keyfile.bin
                p = subprocess.run(["dd",
                                    "if=/dev/urandom",
                                    "of={!s}".format(key_file),
                                    "bs=512",
                                    "count=8",
                                    "iflag=fullblock"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                if p.returncode != 0:
                    libcalamares.utils.warning("Unable to create {!s}: {!s}".format(key_file, p.stderr))
                else:
                    # Remove permissions on key file
                    subprocess.run(["chmod", "000", key_file])

                    # Add key for each encrypted device (except / partition)
                    for enc_device in enc_devices:
                        libcalamares.utils.debug("Add key for {!s} in {!s}".format(enc_device[0], key_file))
                        p = subprocess.run(["cryptsetup",
                                            "luksAddKey",
                                            enc_device[0],
                                            key_file],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            input=enc_device[1].encode())
                        if p.returncode != 0:
                            libcalamares.utils.warning("Unable to add key for {!s} in {!s}: {!s}".format(enc_device[0], key_file, p.stderr))
