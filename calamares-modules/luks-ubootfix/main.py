#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   SPDX-FileCopyrightText: 2022 Arjen Balfoort <arjenbalfoort@hotmail.com>
#   SPDX-License-Identifier: GPL-3.0-or-later
#

import libcalamares
import subprocess
from os.path import exists, join


def run():
    root_mount_point = libcalamares.globalstorage.value("rootMountPoint")
    if root_mount_point:
        crypttab_path = join(root_mount_point, "etc", "crypttab")
        key_file = join(root_mount_point, "crypto_keyfile.bin")
        partitions = libcalamares.globalstorage.value("partitions")
        unencrypted_separate_boot = None
        encrypted_root = None
        enc_devices = []
        
        for partition in partitions:
            #{'claimed': True, 'device': '/dev/sda3', 'features': {}, 'fs': 'ext4', 'fsName': 'luks', 'luksMapperName': 'luks-a493dc53-ae65-417f-b072-e4944131e5df', 'luksPassphrase': 'solydxk', 'luksUuid': 'a493dc53-ae65-417f-b072-e4944131e5df', 'mountPoint': '/', 'partattrs': 0, 'partlabel': '', 'parttype': '', 'partuuid': '1684749C-B3AB-DE4A-8D20-DA5EE8581D36', 'uuid': 'a493dc53-ae65-417f-b072-e4944131e5df'}
            has_luks = "luksMapperName" in partition
            if partition["mountPoint"] == "/boot" and not has_luks:
                unencrypted_separate_boot = partition
            elif partition["mountPoint"] == "/" and has_luks:
                encrypted_root = partition
            elif has_luks:
                # Save encrypted devices and passphrases in dict (enc_devs["/dev/sda4"] = "passphrase")
                enc_devices.append((partition["device"], partition["luksPassphrase"]))
        
        if unencrypted_separate_boot and encrypted_root and exists(crypttab_path):
            libcalamares.utils.debug("Unencrypted /boot and encrypted / partition - fix crypttab:")
            # Fix crypttab: set password to none
            sed_command = "sed -i 's#UUID={!s}.*#UUID={!s}     none#' {!s}".format(encrypted_root["luksUuid"], encrypted_root["luksUuid"], crypttab_path)
            #print((sed_command))
            subprocess.call(sed_command, shell=True)
            with open(crypttab_path, "r") as f: libcalamares.utils.debug(f.read())
            
            if not exists(key_file) and len(enc_devices) > 0:
                libcalamares.utils.debug("Create key file: {!s}".format(key_file))
                # Create /crypto_keyfile.bin
                subprocess.call("dd if=/dev/urandom of={!s} bs=512 count=8 iflag=fullblock".format(key_file), shell=True)
                subprocess.call("chmod 000 {!s}".format(key_file), shell=True)
                for enc_device in enc_devices:
                    # Add key for device
                    libcalamares.utils.debug("Add key to key file for {!s}".format(enc_device[0]))
                    key_command = "printf \"{!s}\" | cryptsetup luksAddKey {!s} {!s}".format(enc_device[1], enc_device[0], key_file)
                    #print((key_command))
                    subprocess.call(key_command, shell=True)
