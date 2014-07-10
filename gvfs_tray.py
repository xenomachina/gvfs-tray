#!/usr/bin/env python3
# coding=utf-8

"""
Creates status icons for mounted removable volumes.

Looks for removable volumes and creates a status icon for each one. These
usually appear in the tray, depending on your desktop environment.
"""

import argparse
import sys

from gi.repository import Gio
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Notify

from pprint import pprint

__author__  = 'Laurence Gonsalves <laurence@xenomachina.com>'

def dump_to_stdout(*args, **kwargs):
    pprint({"Args": args})
    pprint({"KWArgs": kwargs})

def print_volume_identifiers(volume):
    for identifier in volume.enumerate_identifiers():
        print("    %s: %r" % (identifier, volume.get_identifier(identifier)))

def dump_event(event, mount):
    mount_path = mount.get_root().get_path()
    print("%s %s" % (mount_path, event))

def on_mount_added(volume_monitor, mount, *user_args):
    dump_event("added", mount)

def on_mount_changed(volume_monitor, mount, *user_args):
    dump_event("changed", mount)

def on_mount_pre_unmount(volume_monitor, mount, *user_args):
    dump_event("pre-unmount", mount)

def on_mount_removed(volume_monitor, mount, *user_args):
    dump_event("removed", mount)

def on_volume_mounted(volume, async_result, mount_op):
    if volume.mount_finish(async_result):
        print("MOUNTED VOLUME")
        print_volume_identifiers(volume)

        label = volume.get_identifier('label')
        label = "Unlabeled volume" if label is None else repr(label)
        mount_path = volume.get_mount().get_root().get_path()

        notification = Notify.Notification.new(
                "Volume mounted",
                "%s mounted at %s" % (label, mount_path),
                "dialog-information")
        #notification.add_action("action_open", "Open", dump_to_stdout)
        notification.connect("closed", on_notification_closed, None)

        # TODO: get icon from volume?
        # TODO: is it possible to respond to clicks on notification?
        notification.show()

def create_icon(mount):
    icon = Gtk.StatusIcon.new_from_icon_name('drive-removable-media')
    icon.set_visible(True)
    icon.set_name("Foo")

class UserError(Exception):
    def __init__(self, message):
        self.message = message

def create_parser():
    description, epilog = __doc__.strip().split('\n', 1)
    parser = argparse.ArgumentParser(description=description, epilog=epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter)
    return parser

def main(args):
    vm = Gio.VolumeMonitor.get()
    connections = []
    connections.append(vm.connect("mount-added", on_mount_added, None))
    connections.append(vm.connect("mount-changed", on_mount_changed, None))
    connections.append(vm.connect("mount-pre-unmount", on_mount_pre_unmount, None))
    connections.append(vm.connect("mount-removed", on_mount_removed, None))
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
