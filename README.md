gvfs_tray.py
==


Overview
--

Creates status icons for mounted removable volumes.


Looks for removable volumes and creates a status icon for each one. These
usually appear in the tray, depending on your desktop environment.

Each icon has a context menu to do useful operations like:

- Open: opens the volume in a file browser.
- Terminal: Opens the volume in a terminal.
- Eject: Unmounts (and ejects, if possible) the volume.

Additionally, "activating" (by clicking, in most DEs) the icon is equivalent to
the "Open" action.

Screenshots
--

The two rightmost icons here are for a USB thumb drive and an optical disc:

![Icons](/screenshots/basic.png?raw=true)

Hovering over an icon gives some basic info about the volume:

![Tooltip screenshot](/screenshots/tooltip.png?raw=true)

The context menu:

![Context menu screenshot](/screenshots/menu.png?raw=true)


Usage
--

It's a good idea to pipe stdout to a file or to `/dev/null`, as Python tends to
freak out if stdout gets closed. From something like an .xsession file you'd
want to do something like:

    ~/bin/gvfs_tray.py >/dev/null &

If you use i3, like I do, you can add something like this to your `.i3/config`
instead:

    exec --no-startup-id ~/bin/gvfs_tray.py >/dev/null

(These both assume you've put the script in ~/bin -- adjust the path
accordingly.)

You will also need sensible-terminal-in-dir in your path. I just add a symlink
in ~/bin:

    ln -sv $PWD/sensible-terminal-in-dir ~/bin/
