#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   SPDX-FileCopyrightText: 2020 Arjen Balfoort <arjenbalfoort@hotmail.com>
#   SPDX-License-Identifier: GPL-3.0-or-later
#

import libcalamares
import apt
import re

def install_locale_package(package, lang):
    # Install the localized packages for package
    lang = lang.replace('_', '-')
    pattern = "^(%s)((?!-[a-z]{2}-).)*-%s$" % (package, lang)
    for pck in cache.keys():
        if re.match(pattern, pck):
            if not cache[pck].is_installed:
                libcalamares.utils.debug("Install localized package: {}".format(pck))
                libcalamares.utils.target_env_call(["apt-get", "-q", "-y", "install", pck])
                return True
    return False

def run():
    # Create global variable for apt cache
    global cache
    cache = apt.Cache()

    # Only continue when having an internet connection
    skip_this = libcalamares.job.configuration.get("skip_if_no_internet", False)
    if skip_this and not libcalamares.globalstorage.value("hasInternet"):
        libcalamares.utils.warning( "Package installation has been skipped: no internet" )
        return None

    # Get user selected language
    lang = libcalamares.globalstorage.value("localeConf")["LANG"].lower().split(".")[0]
    if not lang or lang == "en_us":
        return None

    # List configured applications
    localize = libcalamares.job.configuration.get('localize', [])
    if lang and localize:
        for pck in localize:
            # Libreoffice can be partially installed without the libreoffice package
            if pck == 'libreoffice':
                is_installed = cache[pck + '-writer'].is_installed
            else:
                is_installed = cache[pck].is_installed
            if is_installed:
                # Install localized packages in this order:
                # 1. package.*-en-gb
                if not install_locale_package(pck, lang):
                    # 2. package.*-en
                    install_locale_package(pck, lang[:2])

    # Check and install additional packages for lang
    additional = libcalamares.job.configuration.get("additional", [])
    for lang_dict in additional:
        try:
            # Install packages separately in case one is not available
            for pck in lang_dict[lang].split():
                if not cache[pck].is_installed:
                    libcalamares.utils.debug("Install additional packages for language {}: {}".format(lang, pck))
                    libcalamares.utils.check_target_env_call(["apt-get", "-q", "-y", "install", pck])
        except:
            pass

    return None
