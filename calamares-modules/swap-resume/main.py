#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   SPDX-FileCopyrightText: 2020 Arjen Balfoort <arjenbalfoort@hotmail.com>
#   SPDX-License-Identifier: GPL-3.0-or-later
#

import os
import libcalamares


def run():
    """ Remove resume file if no swap has been defined """
    resume_path = os.path.join(libcalamares.globalstorage.value(
        "rootMountPoint"), "etc/initramfs-tools/conf.d/resume")
    partitions = libcalamares.globalstorage.value("partitions")

    # Find swap partition
    resume_line = "RESUME=none"
    for partition in partitions:
        if partition["fs"] == "linuxswap":
            resume_line = "RESUME=auto"
            break

    with open(file=resume_path, mode='w', encoding='utf-8') as resume_fle:
        resume_fle.write(resume_line)
