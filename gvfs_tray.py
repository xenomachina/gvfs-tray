#!/usr/bin/env python3
# coding=utf-8

"""
Creates status icons for mounted removable volumes.

Looks for removable volumes and creates a status icon for each one. These
usually appear in the tray, depending on your desktop environment.
"""

import argparse
import subprocess
import sys

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from gi.repository import Gio
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Notify

from cgi import escape as htmlEscape
from pprint import pprint

__author__  = 'Laurence Gonsalves <laurence@xenomachina.com>'

def dump_to_stdout(*args, **kwargs):
    pprint({"Args": args})
    pprint({"KWArgs": kwargs})

def mk_on_debug(event):
    """
    Create a debugging event handler.
    """
    def on_debug(*args):
        print()
        print(event)
        pprint(*args, indent=2)
    return on_debug

def print_volume_identifiers(volume):
    for identifier in volume.enumerate_identifiers():
        print("    %s: %r" % (identifier, volume.get_identifier(identifier)))

def dump_event(event, mount):
    mount_path = mount.get_root().get_path()
    print("%s %s" % (mount_path, event))

class IconManager:
    def __init__(self):
        self.icons = {}

    def menu_items(self, mount):
        result = [
                ('Open',        ('xdg-open',)),
                ('Terminal',    ('sensible-terminal-in-dir',)),
            ]
        if (mount.can_eject()):
            result.append(('Eject', ('gvfs-mount', '--eject')))
        elif (mount.can_unmount()):
            result.append(('Unmount', ('gvfs-mount', '--unmount')))
        return tuple(result)

    def on_mount_added(self, volume_monitor, mount, *user_args):
        dump_event("added", mount)
        self.create_icon(mount)

    def on_mount_changed(self, volume_monitor, mount, *user_args):
        dump_event("changed", mount)
        # TODO: rebuild icon?

    def on_mount_pre_unmount(self, volume_monitor, mount, *user_args):
        dump_event("pre-unmount", mount)

    def on_mount_removed(self, volume_monitor, mount, *user_args):
        dump_event("removed", mount)
        # TODO: delete menu if it's for this mount?
        del self.icons[mount.get_root().get_path()]

    def create_icon(self, mount):
        label = mount.get_name()

        volume = mount.get_volume()
        drive = volume.get_drive()
        print(f'create icon: {label} [can_eject={mount.can_eject()}'
              f' can_unmount={mount.can_unmount()}'
              f' is_floating={volume.is_floating()}'
              f' is_removable={drive.is_removable()}'
              f' is_media_removable={drive.is_media_removable()}'
              f' path={mount.get_root().get_path()}'
          )

        #pprint(dir(drive))

        if mount.can_eject() or mount.get_volume().get_drive().is_removable():
            path = mount.get_root().get_path()
            got = mount.get_icon()
            icon = Gtk.StatusIcon.new_from_gicon(got)
            icon.set_tooltip_markup("%s\n<tt>%s</tt>"
                    % tuple(map(htmlEscape, (label, path))))
            icon.set_visible(True)

            icon.connect("activate", self.on_activate, mount)
            icon.connect("popup-menu", self.on_popup_menu, mount)

            self.icons[path] = icon
        print()

    def on_popup_menu(self, status_icon, button, activate_time, mount):
        menu = self.menu = Gtk.Menu()
        for label, command in self.menu_items(mount):
            item = Gtk.MenuItem()
            item.set_label(label)
            item.connect("activate", self.on_menu_item_activated, command,
                    mount)
            menu.append(item)
        menu.connect("deactivate", self.on_menu_deactivate)
        menu.show_all()

        pos = Gtk.StatusIcon.position_menu
        menu.popup(None, None, pos, status_icon, button, activate_time)

    def on_menu_deactivate(self, *args):
        del self.menu

    def on_menu_item_activated(self, menu_item, command, mount):
        self.call_command(command, mount)

    def call_command(self, command, mount):
        path = mount.get_root().get_path()
        full_command = command + (path,)
        print("+ %r" % (full_command,))
        subprocess.Popen(full_command)

    def on_activate(self, status_icon, mount):
        label, command = self.menu_items(mount)[0]
        self.call_command(command, mount)

class UserError(Exception):
    def __init__(self, message):
        self.message = message

def create_parser():
    description, epilog = __doc__.strip().split('\n', 1)
    parser = argparse.ArgumentParser(description=description, epilog=epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter)
    return parser

def main(args):
    tray = IconManager()
    vm = Gio.VolumeMonitor.get()
    connections = []
    connections.append(vm.connect("mount-added", tray.on_mount_added, 1))
    connections.append(vm.connect("mount-changed", tray.on_mount_changed, 1))
    connections.append(vm.connect("mount-pre-unmount", tray.on_mount_pre_unmount, 1))
    connections.append(vm.connect("mount-removed", tray.on_mount_removed, 1))

    # Synthesize mount-added events for pre-existing mounts
    for mount in vm.get_mounts():
        tray.on_mount_added(vm, mount, 0)

    GObject.MainLoop().run()

if __name__ == '__main__':
    error = None
    parser = create_parser()
    try:
        args = parser.parse_args()
        main(args)
    except FileExistsError as exc:
        error = '%s: %r' % (exc.strerror, exc.filename)
    except UserError as exc:
        error = exc.message

    if error is not None:
        print(('%s: error: %s' % (parser.prog, error)), file=sys.stderr)
        sys.exit(1)
