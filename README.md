gvfs_tray.py
==


Overview
--

Creates status icons for mounted removable volumes.

Looks for removable volumes and creates a status icon for each one. These
usually appear in the tray, depending on your desktop environment.


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
