#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   SPDX-FileCopyrightText: 2020 Arjen Balfoort <arjenbalfoort@hotmail.com>
#   SPDX-License-Identifier: GPL-3.0-or-later
#

import os
import re
import subprocess
import libcalamares

def is_ssd_disk(disk_name):
    """ Checks if given disk is actually a ssd disk.

    :param disk_name:
    :return:
    """
    filename = os.path.join("/sys/block", disk_name, "queue/rotational")

    if not os.path.exists(filename):
        # Should not happen unless sysfs changes, but better safe than sorry
        return False

    with open(filename) as sysfile:
        return sysfile.read() == "0\n"


def disk_name_for_partition(partition):
    """ Returns disk name for each found partition.

    :param partition:
    :return:
    """
    name = os.path.basename(partition["device"])

    if name.startswith("mmcblk") or name.startswith("nvme"):
        return re.sub("p[0-9]+$", "", name)

    return re.sub("[0-9]+$", "", name)

def run():
    # Find root partition
    partition = ''
    partitions = libcalamares.globalstorage.value("partitions")
    for p in partitions:
        if p["mountPoint"] == '/':
            partition = p
            break

    if not partition:
        return None

    # Check if partition is on ssd
    install_path = libcalamares.globalstorage.value("rootMountPoint")
    disk_name = disk_name_for_partition(partition)
    if is_ssd_disk(disk_name):
        # Write additional ram disks to /etc/fstab
        # Note that /tmp is already configured in the calamares fstab module
        ram = "\n# Additional RAM disks\n" \
        "#tmpfs   /var/cache/apt/archives tmpfs   defaults,noexec,nosuid,nodev,mode=0755 0       0\n" \
        "tmpfs   /var/tmp                tmpfs   defaults,noatime                        0       0\n" \
        "tmpfs   /var/backups            tmpfs   defaults,noatime                        0       0\n" \
        "# Disable /var/log/* tmpfs dirs when enabling tmpfs on /var/log\n" \
        "#tmpfs   /var/log                tmpfs   defaults,noatime                        0       0\n" \
        "#tmpfs   /var/log/apt            tmpfs   defaults,noatime,mode=0755              0       0\n" \
        "#tmpfs   /var/log/lightdm        tmpfs   defaults,noatime,mode=0755              0       0\n" \
        "#tmpfs   /var/log/samba          tmpfs   defaults,noatime,mode=0755              0       0\n" \
        "tmpfs   /var/log/cups           tmpfs   defaults,noatime,mode=0755               0       0\n" \
        "tmpfs   /var/log/ConsoleKit     tmpfs   defaults,noatime,mode=0755               0       0\n" \
        "#tmpfs   /var/log/clamav         tmpfs   defaults,noatime,mode=0755,uid=clamav,gid=clamav 0       0\n"
        
        fstab_path = os.path.join(install_path, 'etc/fstab')
        with open(fstab_path, "a") as fstab:
            fstab.write(ram)

        # Configure fstrim
        if os.path.exists(os.path.join(install_path, 'lib/systemd/system/fstrim.timer')):
            libcalamares.utils.check_target_env_call(['systemctl', 'enable', 'fstrim.timer'])
        else:
            fstrim_path = os.path.join(install_path, 'etc/cron.weekly/fstrim_job')
            fstrim_cont = "#!/bin/sh\n" \
                          "for fs in $(lsblk -o MOUNTPOINT,DISC-MAX,FSTYPE | grep -E '^/.* [1-9]+.* ' | awk '{print $1}'); do\n" \
                          "  fstrim \"$fs\"\n" \
                          "done\n"
            with open(fstrim_path, "w") as fstrim:
                fstrim.write(fstrim_cont)
            libcalamares.utils.check_target_env_call(['chmod', '+x', fstrim_path])

        # Configure swappiness
        swappiness_path = os.path.join(install_path, 'etc/sysctl.d/sysctl.conf')
        swappiness_cont = "vm.swappiness=1\n" \
                          "vm.vfs_cache_pressure=25\n" \
                          "vm.dirty_ratio=50\n" \
                          "vm.dirty_background_ratio=3\n"
        with open(swappiness_path, "w") as swappiness:
            swappiness.write(swappiness_cont)

        # Configure sysfs
        sysfs_path = os.path.join(install_path, 'etc/sysfs.conf')
        sysfs_cont = "block/{!s}/queue/scheduler=deadline\n".format(disk_name)
        with open(sysfs_path, "w") as sysfs:
            sysfs.write(sysfs_cont)

    return None
