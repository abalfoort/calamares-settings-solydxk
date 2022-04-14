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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# i18n: http://docs.python.org/3/library/gettext.html
import gettext
_ = gettext.translation('calamares-settings-solydxk', fallback=True).gettext


class ErrorDialog(Gtk.MessageDialog):
    """
    Shows error dialog.
    Args: message string
    """
    def __init__(self, message):
        message += '\n\n{!s}'.format(_("Calamares will continue despite this error."))
        parent = next((w for w in Gtk.Window.list_toplevels() if w.get_title()), None)
        super().__init__(title=_("Error"), transient_for=parent, modal=True, destroy_with_parent=True)
        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.set_markup(message)

    def show(self):
        self.run()
        self.destroy()

class PassphraseDialog(Gtk.MessageDialog):
    """
    Dialog to ask the user for a passphrase.
    Args: device (/dev/sdXN)
    Returns: passphrase string or None
    """
    def __init__(self, device):
        parent = next((w for w in Gtk.Window.list_toplevels() if w.get_title()), None)
        super().__init__(title=_("Passphrase"), transient_for=parent, modal=True, destroy_with_parent=True)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)
        self.set_response_sensitive(Gtk.ResponseType.OK, False)
        self.set_markup(_("Previously encrypted partition found: {!s}.\n"
                        "Please, provide an existing passphrase to unlock.").format(device))
        # Add entry fields
        box = self.get_content_area()
        box.set_property('margin-left', 10)
        box.set_property('margin-right', 10)
        entry1 = Gtk.Entry()
        entry1.set_visibility(False)
        box.pack_start(entry1, True, True, 0)
        self.entry1 = entry1
        self.entry1.connect('changed', self.on_entry_changed)
        entry2 = Gtk.Entry()
        entry2.set_visibility(False)
        entry2.set_activates_default(True)
        box.pack_start(entry2, True, True, 0)
        self.entry2 = entry2
        self.entry2.connect('changed', self.on_entry_changed)
        self.show_all()

    def on_entry_changed(self, widget):
        value1 = self.entry1.get_text().strip()
        value2 = self.entry2.get_text().strip()
        button_sensitive = len(value1) > 0 and value1 == value2
        self.set_response_sensitive(Gtk.ResponseType.OK, button_sensitive)

    def show(self):
        try:
            if self.run() == Gtk.ResponseType.OK:
                return self.entry1.get_text().strip()
            else:
                return None
        finally:
            self.destroy()

def create_keyfile(key_file):
    """
    Create a key file.
    Args: key file path
    """
    libcalamares.utils.debug("Create key file: {!s}".format(key_file))
    p = subprocess.run(['dd',
                        'if=/dev/urandom',
                        'of={!s}'.format(key_file),
                        'bs=512',
                        'count=8',
                        'iflag=fullblock'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
    if p.returncode != 0:
        message = _("Unable to create {!s}: {!s}").format(key_file, p.stderr.decode())
        libcalamares.utils.warning(message)
        ErrorDialog(message).show()
    else:
        # Remove permissions on key file
        libcalamares.utils.debug("Remove permissions from key file: {!s}".format(key_file))
        subprocess.run(['chmod', '000', key_file])

def add_luks_key(device, passphrase, key_file):
    """
    Add a key to a luks key.
    Args: device (/dev/sdXN), luks passphrase for device
    """
    
    # Sometimes this error is thrown: "All key slots full"
    # luksAddKey will fail. So, remove the first slot to make room
    luks_dump = ''
    try:
        luks_dump = subprocess.check_output(['cryptsetup', 'luksDump', device]).decode()
    except Exception as e:
        # We shouldn't get here
        libcalamares.utils.warning("luksDump error: {!s}".format(e))
        
    pattern = re.compile(r'(\d+):\s*enabled', re.IGNORECASE)
    slots = re.findall(pattern, luks_dump)
    if len(slots) > 7:
        libcalamares.utils.debug("Key slots full - remove slot: 1")
        subprocess.run(['cryptsetup',
                        'luksKillSlot',
                        device,
                        '1'],
                        input=passphrase.encode())

    libcalamares.utils.debug("Add key for {!s} in {!s}".format(device, key_file))
    p = subprocess.run(['cryptsetup',
                        'luksAddKey',
                        device,
                        key_file],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        input=passphrase.encode())

    if p.returncode != 0:
        # Error codes are: 1 wrong parameters, 2 no permission (bad passphrase), 3 out of memory, 4 wrong device specified, 5  device already exists or device is busy.
        message = _("Unable to add key for {!s} in {!s}: {!s}").format(device, key_file, p.stderr.decode())
        libcalamares.utils.warning(message)
        ErrorDialog(message).show()

def get_fstype(device, uuid, passphrase):
    """
    Get the fs type of a luks partition
    Args: device (/dev/sdXN), device uuid, luks passphrase
    Returns: fs type string
    """
    fstype = ''
    if os.path.exists(device):
        mapped_name = 'luks-{!s}'.format(uuid)
        mapped_device = os.path.join('/dev/mapper', mapped_name)
        close_device = False

        if not os.path.exists(mapped_device):
            libcalamares.utils.debug("Open luks device: {!s}".format(device))
            # Open the luks device
            p = subprocess.run(['cryptsetup',
                                'open',
                                '--type',
                                'luks',
                                device,
                                mapped_name],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                input=passphrase.encode())
            if p.returncode != 0:
                message = "Unable to open luks device {!s}: {!s}".format(device, p.stderr.decode())
                libcalamares.utils.warning(message)
            else:
                close_device = True

        if os.path.exists(mapped_device):
            # Get file system
            # psutil only lists loop devices in a live session
            # Use lsblk instead
            fstype = subprocess.check_output(['lsblk', '-no', 'FSTYPE', mapped_device]).decode().strip()
            libcalamares.utils.debug("fstype of luks device {!s}: {!s}".format(mapped_device, fstype))

            # Close the luks device
            if close_device:
                libcalamares.utils.debug("Close luks device: {!s}".format(mapped_device))
                subprocess.run(['umount', '-f', mapped_device])
                p = subprocess.run(['cryptsetup',
                                    'close',
                                    mapped_name],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                if p.returncode != 0:
                    message = "Unable to close luks device {!s}: {!s}".format(mapped_device, p.stderr.decode())
                    libcalamares.utils.warning(message)

    return fstype

def replace_in_file(file_path, pattern, replace_string):
    """
    Replace a pattern with a string in a file.
    Args: regular expression pattern to replace, string to replace pattern with
    """
    if os.path.exists(file_path):
        with open(file_path, 'r+') as f:
            txt = f.read()
            txt = re.sub(pattern, replace_string, txt)
            f.seek(0)
            f.write(txt)
            f.truncate()

def run():
    root_mount_point = libcalamares.globalstorage.value('rootMountPoint')
    partitions = libcalamares.globalstorage.value('partitions')

    if not root_mount_point:
        libcalamares.utils.warning("rootMountPoint is empty, {!s}"
                                   .format(root_mount_point))
        return None

    if not partitions:
        libcalamares.utils.warning("partitions is empty, {!s}"
                                   .format(partitions))
        return None

    crypttab_path = os.path.join(root_mount_point, 'etc', 'crypttab')
    fstab_path = os.path.join(root_mount_point, 'etc', 'fstab')
    key_file = os.path.join(root_mount_point, 'crypto_keyfile.bin')
    unencrypted_boot = False
    root_partition_uuid = None
    encrypted_partitions = []

    # Check if /boot is unencrypted and / is encrypted
    for partition in partitions:
        has_luks = 'luksMapperName' in partition
        if partition['mountPoint'] == '/boot' and not has_luks:
            unencrypted_boot = True
        elif partition['mountPoint'] == '/' and has_luks and partition['luksPassphrase']:
            root_partition_uuid = partition['uuid']                    
        elif (partition['mountPoint'] or partition['fs'] == 'linuxswap') and has_luks:
            # Save encrypted devices and passphrases
            encrypted_partitions.append(partition)

    if root_partition_uuid and os.path.exists(crypttab_path) and os.path.exists(fstab_path):
        if unencrypted_boot:
            libcalamares.utils.debug("Set password to none for / partition {!s} in {!s}"
                                     .format(root_partition_uuid, crypttab_path))

            # Fix crypttab: set password to none for / partition
            pattern = 'UUID={!s}.*'.format(root_partition_uuid)
            repl_string = 'UUID={!s}     none'.format(root_partition_uuid)
            replace_in_file(crypttab_path, pattern, repl_string)

            with open(crypttab_path, 'r') as f:
                if not repl_string in f.read():
                    libcalamares.utils.warning("Unable to adapt {!s}. Line should be: ...{!s}"
                                               .format(crypttab_path, repl_string))

        if not os.path.exists(key_file) and len(encrypted_partitions) > 0:
            # Create /crypto_keyfile.bin
            create_keyfile(key_file)

        if os.path.exists(key_file) and len(encrypted_partitions) > 0:
            # Add key for each encrypted partition (except / partition)
            for partition in encrypted_partitions:
                if partition['luksPassphrase']:
                    # Add key to the key file
                    add_luks_key(partition['device'], partition['luksPassphrase'], key_file)
                else:
                    # This partition is a previously encrypted partition and has no passphrase - ask user for passphrase
                    fstype = ''
                    while not fstype:
                        passphrase = PassphraseDialog(partition['device']).show()
                        if passphrase is None:
                            # User hit the Cancel button
                            message = _("Unable to determine the file system type of {!s}.\n"
                                        "You need to configure this device manually.".format(partition['device']))
                            libcalamares.utils.warning(message)
                            ErrorDialog(message).show()
                            break
                        
                        if passphrase:
                            # Get real fs type
                            fstype = get_fstype(partition['device'],
                                                partition['uuid'],
                                                passphrase)

                    if fstype:
                        # Fix fstab:
                        pattern = '.*\s{!s}\s.*'.format(partition['mountPoint'])
                        repl_string = '/dev/mapper/luks-{!s} {!s} {!s} defaults,noatime 0 2'.format(partition['uuid'], 
                                                                                                    partition['mountPoint'],
                                                                                                    fstype)
                        libcalamares.utils.debug("FSTAB: {!s}".format(repl_string))
                        replace_in_file(fstab_path, pattern, repl_string)

                        with open(fstab_path, 'r') as f:
                            if not repl_string in f.read():
                                libcalamares.utils.warning("Unable to adapt {!s}. Line should be: ...{!s}"
                                                           .format(fstab_path, repl_string))

                        # Fix crypttab
                        crypttab_cont = ''
                        with open(crypttab_path, 'r') as f:
                            crypttab_cont = f.read()
                        if not partition['uuid'] in crypttab_cont:
                            # UUID not found - append partition to crypttab
                            crypttab_line = 'luks-{uuid} UUID={uuid} /crypto_keyfile.bin luks,keyscript=/bin/cat\n'.format(uuid=partition['uuid'])
                            libcalamares.utils.debug("CRYPTTAB: {!s}".format(crypttab_line))
                            with open(crypttab_path, 'a') as f:
                                f.write(crypttab_line)
                            # Add the key to the key file
                            add_luks_key(partition['device'], passphrase, key_file)

    return None
