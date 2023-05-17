#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   SPDX-FileCopyrightText: 2023 Arjen Balfoort <arjenbalfoort@hotmail.com>
#   SPDX-License-Identifier: GPL-3.0-or-later
#

import sys
import subprocess
import libcalamares

# Partition object example:
# {'claimed': True,
# 'device': '/dev/sda2',
# 'features': {},
# 'fs': 'ext4',
# 'fsName': 'luks',
# 'luksMapperName': 'luks-eec6e236-eee1-4aed-a299-f2aed8a1e029',
# 'luksPassphrase': 'solydxk',
# 'luksUuid': 'eec6e236-eee1-4aed-a299-f2aed8a1e029',
# 'mountPoint': '/',
# 'partattrs': 0,
# 'partlabel': 'SOLYDXK',
# 'parttype': '',
# 'partuuid': '4E472123-1053-644A-948F-8162C2217FDD',
# 'uuid': 'eec6e236-eee1-4aed-a299-f2aed8a1e029'}

def shell_exec(command):
    """Execute command in shell"""
    libcalamares.utils.debug(f"Executing: {command}")
    try:
        return subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as exc:
        libcalamares.utils.debug(str(exc))
        return exc.returncode

def get_output(command):
    """Get output from command."""
    libcalamares.utils.debug(f"Get output from: {command}")
    try:
        return (subprocess.check_output(command, shell=True)
                .decode(sys.getfilesystemencoding()).replace('\n', ' ').strip())
    except subprocess.CalledProcessError as exc:
        libcalamares.utils.debug(str(exc))
        return None

def run():
    """Convert LUKS1 to LUKS2 with argon2id"""
    partitions = libcalamares.globalstorage.value("partitions")
    # Check for boot partition
    search_list = [_p for _p in partitions if _p["mountPoint"] == "/boot"]
    boot_partition = search_list[0] if search_list else None
    if boot_partition:
        libcalamares.utils.debug(f"Boot partition found: {boot_partition['device']}")

    for partition in partitions:
        # Skip the following partitions:
        # - Non-LUKS1
        # - Boot partition (Grub2 won't handle it)
        # - Root partition if there is no boot partition
        if (partition['fsName'] != 'luks' or
            partition == boot_partition or
            (partition['mountPoint'] == '/' and not boot_partition)):
            if partition['device'] and partition['mountPoint']:
                libcalamares.utils.debug(f"Skip partition: {partition['device']} - "
                                         f"{partition['mountPoint']}")
            continue

        # Check if luks version is 1
        luks1 = get_output(command=f"cryptsetup luksDump {partition['device']} |"
                                    "egrep 'Version:[[:space:]]*1'")
        if luks1:
            libcalamares.utils.debug(f"Convert {partition['device']} to LUKS2")

            # Make sure the device is not in use
            mount_point = get_output(command="findmnt -no TARGET "
                                            f"/dev/mapper/{partition['luksMapperName']}")
            if mount_point:
                shell_exec(command=f"umount -f {mount_point}")
            shell_exec(command=f"cryptsetup close {partition['luksMapperName']}")

            # Convert to LUKS2
            ret = shell_exec(command="echo YES | "
                                    f"cryptsetup convert {partition['device']} --type luks2")
            if ret == 0:
                # Use argon2id
                shell_exec(command=f"echo {partition['luksPassphrase']} | "
                                   f"cryptsetup luksConvertKey {partition['device']}"
                                    " --pbkdf argon2id")

            # Mount the device again
            shell_exec(command=f"printf \"{partition['luksPassphrase']}\" | "
                               f"cryptsetup open {partition['device']} "
                               f"{partition['luksMapperName']}")
            if mount_point:
                shell_exec(command=f"mount /dev/mapper/{partition['luksMapperName']} {mount_point}")
