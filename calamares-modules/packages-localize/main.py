#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   SPDX-FileCopyrightText: 2020 Arjen Balfoort <arjenbalfoort@hotmail.com>
#   SPDX-License-Identifier: GPL-3.0-or-later
#

import libcalamares
import apt
import re

def run():
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
        for pck in localize[:]:
            cache = apt.Cache()
            try:
                # Check if package is installed
                if cache[pck].is_installed:
                    # Install localized packages in this order:
                    # 1. package.*-en-gb
                    # 2. package.*-en
                    pck_name = '{}.*-{}$'.format(pck, lang.replace('_', '-'))
                    libcalamares.utils.debug("Try to install locale package {}".format(pck_name))
                    err_code = libcalamares.utils.target_env_call(["apt-get", "-q", "-y", "install", pck_name])
                    if err_code > 0:
                        # Match thunderbird-help-nl but not thunderbird-help-fy-nl
                        pattern = "^(%s)((?!-[a-z]{2}-).)*-%s$" % (pck, lang[:2])
                        libcalamares.utils.debug("Match package name with pattern={}".format(pattern))
                        for p in cache.keys():
                            if re.match(pattern, p):
                                libcalamares.utils.debug("Try to install locale package {}".format(p))
                                libcalamares.utils.target_env_call(["apt-get", "-q", "-y", "install", p])
            except NameError as error:
                libcalamares.utils.debug("Package not available: {}".format(pck))
            except Exception as exception:
                libcalamares.utils.debug(exception)
                
            
    # Check and install additional packages for lang
    additional = libcalamares.job.configuration.get("additional", [])
    for lang_dict in additional:
        try:
            # Install packages separately in case one is not available
            for pck in lang_dict[lang].split():
                libcalamares.utils.debug("Install additional packages for language {}: {}".format(lang, pck))
                libcalamares.utils.check_target_env_call(["apt-get", "-q", "-y", "install", pck])
        except:
            pass

    return None
