from libqtile import hook
from libqtile.lazy import lazy
import subprocess

@hook.subscribe.client_managed
def show_window(window):
    window.group.cmd_toscreen()

@lazy.function
def prev_group(qtile):
    qtile.current_screen.set_group(qtile.current_screen.previous_group)

@lazy.function
def float_to_front(qtile):
    for group in qtile.groups:
        for window in group.windows:
            if window.floating:
                window.cmd_bring_to_front()

def next_window(qtile):
    group = qtile.current_group
    group.cmd_next_window()
    if group.current_window and group.current_window.floating:
        group.current_window.cmd_bring_to_front()

def prev_window(qtile):
    group = qtile.current_group
    group.cmd_prev_window()
    if group.current_window and group.current_window.floating:
        group.current_window.cmd_bring_to_front()

@lazy.function
def left_or_main(qtile):
    group = qtile.current_group
    layout = qtile.current_layout
    clients = layout.clients
    if group.current_window and group.current_window.floating:
        return
    elif layout.name == "max":
        prev_window(qtile)
    elif layout.name == "monaddeck":
        if len(clients) > 1 and clients.current_index > 0:
            group.focus(layout.clients[0])
    elif layout.name == "monadtall":
        if len(clients) > 1 and clients.current_index > 0:
            group = qtile.current_group
            for win in reversed(group.focus_history):
                if not win.floating and win in clients and clients.index(win) < 1:
                    group.focus(win)
                    return
    elif layout.name == "tile":
        if clients.current_index >= layout.master_length:
            group = qtile.current_group
            for win in reversed(group.focus_history):
                if not win.floating and win in clients and clients.index(win) < layout.master_length:
                    group.focus(win)
                    return
    else:
        layout.cmd_left()

@lazy.function
def right_or_stack(qtile):
    group = qtile.current_group
    layout = qtile.current_layout
    clients = layout.clients
    if group.current_window and group.current_window.floating:
        return
    elif layout.name == "max":
        next_window(qtile)
    elif layout.name == "monaddeck":
        if len(clients) > 1 and clients.current_index < 1:
            group.focus(layout.clients[layout.current_shared])
    elif layout.name == "monadtall":
        if len(clients) > 1 and clients.current_index < 1:
            group = qtile.current_group
            for win in reversed(group.focus_history):
                if not win.floating and win in clients and clients.index(win) > 0:
                    group.focus(win)
                    return
    elif layout.name == "tile":
        if len(clients) > layout.master_length and clients.current_index < layout.master_length:
            group = qtile.current_group
            for win in reversed(group.focus_history):
                if not win.floating and win in clients and clients.index(win) >= layout.master_length:
                    group.focus(win)
                    return
    else:
        layout.cmd_right()

@lazy.function
def rotate_all(qtile, dir):
    layout = qtile.current_layout
    if (layout.name not in ["monadtall", "monadwide", "monadthreecol", "monaddeck", "tile"]
        or len(layout.clients) < 2 or qtile.current_window.floating):
        return
    if dir < 0:
        layout.clients.rotate_up(maintain_index=False)
    else:
        layout.clients.rotate_down(maintain_index=False)
    group = qtile.current_group
    group.layout_all()
    group.focus(layout.clients[layout.clients.current_index])

@lazy.function
def rotate_column(qtile, dir):
    layout = qtile.current_layout
    if (layout.name not in ["monadtall", "monadwide", "monadthreecol", "monaddeck", "tile"]
        or len(layout.clients) < 2 or qtile.current_window.floating):
        return
    clients = layout.clients.clients
    master_length = 1 if layout.name != "tile" else layout.master_length
    if master_length == 1 or layout.clients.current_index >= master_length:
        first, last = master_length, len(clients)-1
    else:
        first, last = 0, master_length-1
    if dir < 0:
        clients.insert(last, clients.pop(first))
    else:
        clients.insert(first, clients.pop(last))
    group = qtile.current_group
    group.layout_all()
    group.focus(layout.clients[layout.clients.current_index])

@lazy.function
def swap_main(qtile):
    layout = qtile.current_layout
    if (layout.name in ["max", "floating"]
        or len(layout.clients) < 2 or qtile.current_window.floating):
        return
    group = qtile.current_group
    main = layout.clients[0]
    target = qtile.current_window
    if target == main:
        if layout.name == "monaddeck":
            target = layout.clients[layout.current_shared] 
        else:
            target = getattr(group, "prev_swapped_main", None)
            if target not in layout.clients or target == main:
                target = layout.clients[1]
    setattr(group, "prev_swapped_main", main)
    i1 = layout.clients.index(target)
    i2 = layout.clients.index(main)
    layout.clients[i1], layout.clients[i2] = layout.clients[i2], layout.clients[i1]
    layout.current_index = i1
    group.layout_all()
    group.focus(target)
    for win in [main, target]:
        if win in group.focus_history:
            group.focus_history.remove(win)
        group.focus_history.append(win)

@lazy.function
def move_floating(qtile, dx: int = 0, dy: int = 0):
    if qtile.current_window:
        qtile.current_window.cmd_move_floating(dx, dy)

@lazy.function
def move_floating_to_edge(qtile, dx: int = 0, dy: int = 0):
    scr = qtile.current_screen
    win = qtile.current_window
    if win:
        bh = scr.top.height if scr.top.is_show() else 0
        x = 0 if dx < 0 else win.x
        y = bh if dy < 0 else win.y
        if dx > 0:
            x = scr.width - win.width - win.borderwidth*2
        if dy > 0:
            y = scr.height - win.height - win.borderwidth*2
        win.cmd_set_position_floating(x, y)

@lazy.function
def resize_floating(qtile, dw: int = 0, dh: int = 0):
    if qtile.current_window:
        qtile.current_window.cmd_resize_floating(dw, dh)

@lazy.function
def aspect_resize_floating(qtile, dh: int = 0):
    win = qtile.current_window 
    if win:
        win.cmd_resize_floating(int(dh * win.width / win.height), dh)

@lazy.function
def fetch_windows(qtile, groupname):
    for win in qtile.groups_map[groupname].windows.copy():
        win.togroup()

@lazy.function
def shrink_main(qtile):
    layout = qtile.current_layout
    if (layout.name in ["monadtall", "monadwide", "monadthreecol", "monaddeck"]
        and len(layout.clients) > 1):
        layout.cmd_shrink_main()
    elif layout.name == "tile":
        layout.cmd_decrease_ratio()

@lazy.function
def grow_main(qtile):
    layout = qtile.current_layout
    if (layout.name in ["monadtall", "monadwide", "monadthreecol", "monaddeck"]
        and len(layout.clients) > 1):
        layout.cmd_grow_main()
    elif layout.name == "tile":
        layout.cmd_increase_ratio()

@lazy.function
def shrink_shared(qtile):
    layout = qtile.current_layout
    if (layout.name in ["monadtall", "monadwide", "monadthreecol"]
        and len(layout.clients) > 2
        and layout.clients.current_index > 0):
        layout.cmd_shrink()

@lazy.function
def grow_shared(qtile):
    layout = qtile.current_layout
    if (layout.name in ["monadtall", "monadwide", "monadthreecol"]
        and len(layout.clients) > 2
        and layout.clients.current_index > 0):
        layout.cmd_grow()

@lazy.function
def decrease_nmaster(qtile):
    layout = qtile.current_layout
    if layout.name == "tile":
        layout.cmd_decrease_nmaster()

@lazy.function
def increase_nmaster(qtile):
    layout = qtile.current_layout
    if layout.name == "tile":
        layout.cmd_increase_nmaster()

@lazy.function
def toggle_minimize(qtile):
    win = qtile.current_window
    if not win:
        return;
    win.toggle_minimize()
    if win.minimized:
        group = qtile.current_group
        for win in reversed(group.focus_history):
            if not win.minimized:
                group.focus(win)
                return

@lazy.function
def toggle_gaps(qtile):
    layout = qtile.current_layout
    old_margin = getattr(layout, "old_margin", layout.margin)
    old_single_margin = getattr(layout, "old_single_margin", layout.single_margin)
    setattr(layout, "old_margin", old_margin)
    setattr(layout, "old_single_margin", old_single_margin)
    layout.margin = 0 if layout.margin else old_margin
    layout.single_margin = 0 if layout.single_margin else old_single_margin
    qtile.current_group.layout_all()

@lazy.function
def volume_control(qtile, cmd, step=None):
    qtile.widgets_map["volumewidget"].volume_control(cmd, step)

@lazy.function
def backlight_control(qtile, cmd):
    qtile.widgets_map['backlightwidget'].cmd_change_backlight(cmd)

@lazy.function
def toggle_auto_fullscreen(qtile):
    qtile.config.auto_fullscreen = not qtile.config.auto_fullscreen
    status = "On" if qtile.config.auto_fullscreen else "Off"
    subprocess.run(["/usr/bin/dunstify", "-t", "2000", "-r",
                    "5560", "--icon=no-icon", "",
                    f"<span font='JetBrainsMono Nerd Font 12'> Auto fullscreen: {status} \n</span>"],
                    capture_output=False)
