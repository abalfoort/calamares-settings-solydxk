#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   SPDX-FileCopyrightText: 2020 Arjen Balfoort <arjenbalfoort@hotmial.com>
#   SPDX-License-Identifier: GPL-3.0-or-later
#

import subprocess
from libcalamares.utils import check_target_env_call

def run():
    virt = ''
    try:
        virt = subprocess.check_output('systemd-detect-virt').decode('utf-8').strip()
    except:
        # Best effort
        pass

    if not 'oracle' in virt:
        # Remove VirtualBox Guest packages
        check_target_env_call(["apt-get", "--purge", "-q", "-y", "remove", "virtualbox-guest*"])

    return None
