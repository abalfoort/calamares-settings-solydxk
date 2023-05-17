#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   SPDX-FileCopyrightText: 2020 Arjen Balfoort <arjenbalfoort@hotmail.com>
#   SPDX-License-Identifier: GPL-3.0-or-later
#

import sys
import subprocess
import apt
import libcalamares

CACHE = apt.Cache()

def install_regional(lang):
    """Install regional packages

    Args:
        lang (string): language code
    """
    additional = libcalamares.job.configuration.get("additional", [])
    for lang_dict in additional:
        # Install packages separately in case one is not available
        if lang in lang_dict:
            for pck in lang_dict[lang].split():
                if not CACHE[pck].is_installed:
                    try:
                        libcalamares.utils.debug(f"Install additional package "
                                                 f"for language {lang}: {pck}")
                        libcalamares.utils.check_target_env_call(
                            ["apt-get", "-q", "-y", "install", pck])
                    finally:
                        libcalamares.utils.debug(
                            f"Install additional package finished: {pck}")
            break

def remove_virtguest():
    """
    Remove VirtualBox and Qemu Guest packages when not in VirtualBox
    """
    virt = (subprocess.run('systemd-detect-virt',
                           check=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
            .stdout.decode(sys.getfilesystemencoding()).strip())

    if 'oracle' not in virt:
        # Remove VirtualBox Guest packages
        libcalamares.utils.check_target_env_call(
            ["apt-get", "--purge", "-q", "-y", "remove", "virtualbox-guest*"])

    if 'kvm' not in virt:
        # Remove Qemu Guest packages
        libcalamares.utils.check_target_env_call(
            ["apt-get", "--purge", "-q", "-y", "remove", "qemu-guest*"])
        libcalamares.utils.check_target_env_call(
            ["apt-get", "--purge", "-q", "-y", "remove", "spice-vdagent*"])

def run():
    """Install localized packages

    Returns:
        object: None on finished
    """

    # Only continue when having an internet connection
    skip_this = libcalamares.job.configuration.get(
        "skip_if_no_internet", False)
    if skip_this and not libcalamares.globalstorage.value("hasInternet"):
        libcalamares.utils.warning("Package installation has been skipped: "
                                   "no internet")
        return None

    # Get user selected language
    lang = (libcalamares.globalstorage.value("localeConf")["LANG"].
            lower().split(".")[0])
    if not lang or lang == "en_us":
        return None

    # Install regional packages for lang
    install_regional(lang)

    # Remove VB Guest when not in VB
    remove_virtguest()

    return None
