# Adds window swallowing to qtile
# A modified version of https://github.com/qtile/qtile/issues/1771

import psutil
from libqtile import hook

terminals = [
    #"Alacritty",
    "St",
]

noswallow = [
    "Chromium",
    "firefox",
    "Dragon-drop",
    "Pinentry-gtk-2",
    "St"
]

@hook.subscribe.client_new
def _swallow(window):
    if window.window.get_wm_class()[1] in noswallow:
        return;
    pid = window.window.get_net_wm_pid()
    ppid = psutil.Process(pid).ppid()
    cpids = {
        c.window.get_net_wm_pid(): wid
        for wid, c in window.qtile.windows_map.items()
    }
    for _ in range(5):
        if not ppid:
            return
        if ppid in cpids:
            parent = window.qtile.windows_map.get(cpids[ppid])
            if parent.window.get_wm_class()[1] not in terminals:
                return
            layout = window.qtile.current_layout
            if hasattr(layout, "new_client_position"):
                layout.new_client_position_old = layout.new_client_position
                layout.new_client_position = "before_current" if layout.focused == 0 else "after_current"
            parent.minimized = True
            window.parent = parent
            return
        ppid = psutil.Process(ppid).ppid()

@hook.subscribe.client_managed
def _swallow_post(window):
    layout = window.qtile.current_layout
    if hasattr(layout, "new_client_position_old"):
        layout.new_client_position = layout.new_client_position_old
        delattr(layout, "new_client_position_old")
    # Move the minimized parent window to the last group and if the last group
    # is ScratchPad, the parent window is then completely hidden.
    if hasattr(window, 'parent') and hasattr(window.parent, 'minimized'):
        window.parent.togroup(window.qtile.groups[-1].name)

@hook.subscribe.client_focus
def _client_focus(window):
    layout = window.qtile.current_layout
    if hasattr(layout, "new_client_position"):
        window.last_position = layout.focused

@hook.subscribe.client_killed
def _unswallow(window):
    if hasattr(window, 'parent') and hasattr(window.parent, 'minimized'):
        layout = window.qtile.current_layout
        if hasattr(layout, "new_client_position"):
            focused = layout.focused + 1
            if focused == 1 and hasattr(window, 'last_position'):
                focused = window.last_position
            new_client_position_old = layout.new_client_position
            layout.new_client_position = "before_current" if focused == 0 else "after_current"
        if window.parent.group != window.group:
            window.parent.togroup(window.group.name)
        window.parent.minimized = False
        window.group.focus(window.parent)
        if hasattr(layout, "new_client_position"):
            layout.new_client_position = new_client_position_old
