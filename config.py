from os.path import expanduser
from libqtile import bar, layout, widget
from libqtile.config import Click, Drag, Group, EzKey, Match, Screen, ScratchPad, DropDown
from libqtile.lazy import lazy
from qtile_extras.widget.currentlayout import CurrentLayoutIcon
from layouts import *
from widgets import *
from functions import *
from swallow import *

keys = [
    # Switch between windows
    EzKey("M-h",                    left_or_main,                       desc="Move focus to left"),
    EzKey("M-l",                    right_or_stack,                     desc="Move focus to right"),
    EzKey("M-j",                    lazy.function(next_window),         desc="Move focus to next window"),
    EzKey("M-k",                    lazy.function(prev_window),         desc="Move focus to previous window"),
    EzKey("M-<Left>",               lazy.layout.left(),                 desc="Move focus to left"),
    EzKey("M-<Right>",              lazy.layout.right(),                desc="Move focus to right"),
    EzKey("M-<Up>",                 lazy.layout.up(),                   desc="Move focus down"),
    EzKey("M-<Down>",               lazy.layout.down(),                 desc="Move focus up"),
    # Move windows up/down and rotate windows
    EzKey("M-S-j",                  lazy.layout.shuffle_down(),         desc="Move window down"),
    EzKey("M-S-k",                  lazy.layout.shuffle_up(),           desc="Move window up"),
    EzKey("M-S-h",                  rotate_column(dir=-1),              desc="Rotate main or shared windows"),
    EzKey("M-S-l",                  rotate_column(dir=+1),              desc="Rotate main or shared windows"),
    EzKey("M-S-C-h",                rotate_all(dir=-1),                 desc="Rotate all windows"),
    EzKey("M-S-C-l",                rotate_all(dir=+1),                 desc="Rotate all windows"),
    # Grow windows
    EzKey("M-C-h",                  shrink_main,                        desc="Shrink main window"),
    EzKey("M-C-l",                  grow_main,                          desc="Grow main window"),
    EzKey("M-C-j",                  shrink_shared,                      desc="Shrink shared window down"),
    EzKey("M-C-k",                  grow_shared,                        desc="Grow shared window up"),
    EzKey("M-C-n",                  lazy.layout.normalize(),            desc="Reset all window sizes"),
    EzKey("M-C-o",                  lazy.layout.maximize(),             desc="Grow the currently focused client to the max size"),
    # Window control
    EzKey("M-S-<Right>",            move_floating(dx=20),               desc="Move floating window to right"),
    EzKey("M-S-<Left>",             move_floating(dx=-20),              desc="Move floating window to left"),
    EzKey("M-S-<Down>",             move_floating(dy=20),               desc="Move floating window to down"),
    EzKey("M-S-<Up>",               move_floating(dy=-20),              desc="Move floating window to up"),
    EzKey("M-S-C-<Right>",          move_floating_to_edge(dx=1),        desc="Move floating window to right edge"),
    EzKey("M-S-C-<Left>",           move_floating_to_edge(dx=-1),       desc="Move floating window to left edge"),
    EzKey("M-S-C-<Down>",           move_floating_to_edge(dy=1),        desc="Move floating window to bottom edge"),
    EzKey("M-S-C-<Up>",             move_floating_to_edge(dy=-1),       desc="Move floating window to top edge"),
    EzKey("M-C-<Right>",            resize_floating(dw=20),             desc="Increase floating window width"),
    EzKey("M-C-<Left>",             resize_floating(dw=-20),            desc="Decrease floating window width"),
    EzKey("M-C-<Down>",             resize_floating(dh=20),             desc="Incease floating window height"),
    EzKey("M-C-<Up>",               resize_floating(dh=-20),            desc="Decrease floating window height"),
    EzKey("M-A-<Right>",            aspect_resize_floating(dh=20),      desc="Increase floating window aspect size"),
    EzKey("M-A-<Left>",             aspect_resize_floating(dh=-20),     desc="Decrease floating window aspect size"),
    EzKey("M-A-<Down>",             aspect_resize_floating(dh=20),      desc="Increase floating window aspect size"),
    EzKey("M-A-<Up>",               aspect_resize_floating(dh=-20),     desc="Decrease floating window aspect size"),
    EzKey("M-S-f",                  toggle_auto_fullscreen(),           desc="Toggle auto fullscreen"),
    EzKey("M-f",                    lazy.window.toggle_fullscreen(),    desc="Toggle fullscreen"),
    EzKey("M-g",                    lazy.window.toggle_floating(),      desc="Toggle floating"),
    EzKey("M-x",                    toggle_minimize,                    desc="Toggle minimize"),
    EzKey("M-a",                    toggle_gaps,                        desc="Toggle gaps"),
    EzKey("M-C-g",                  float_to_front,                     desc="Bring floating windows to front"),
    EzKey("M-<Space>",              swap_main,                          desc="Swap current window to main pane"),
    EzKey("M-S-q",                  lazy.window.kill(),                 desc="Kill focused window"),
    # Layouts
    EzKey("M-u",                    lazy.to_layout_index(0),            desc="MonadTall layout"),
    EzKey("M-S-u",                  lazy.to_layout_index(1),            desc="MonadWide layout"),
    EzKey("M-C-u",                  lazy.to_layout_index(2),            desc="Tile layout"),
    EzKey("M-i",                    lazy.to_layout_index(6),            desc="Max layout"),
    EzKey("M-S-i",                  lazy.to_layout_index(3),            desc="MonadDeck layout"),
    EzKey("M-C-i",                  lazy.to_layout_index(4),            desc="MonadThreeCol layout"),
    EzKey("M-S-g",                  lazy.to_layout_index(5),            desc="Floating layout"),
    # Applications
    EzKey("M-<Return>",             lazy.spawn("st"),                   desc="Launch terminal"),
    EzKey("M-p",                    lazy.spawn("dmenu_run"),            desc="Launch dmenu_run"),
    EzKey("M-d",                    lazy.spawn("rofi-launcher"),        desc="Launch rofi-launcher"),
    EzKey("M-S-d",                  lazy.spawn("rofi-find"),            desc="Launch rofi-finder"),
    EzKey("M-S-e",                  lazy.spawn("thunar"),               desc="Launch file manager"),
    EzKey("M-w",                    lazy.spawn("chromium"),             desc="Launch chromium"),
    EzKey("M-C-w",                  lazy.spawn("firefox"),              desc="Launch firefox"),
    EzKey("M-C-S-w",                lazy.spawn("firefox --private"),    desc="Launch firefox (private)"),
    EzKey("M-v",                    lazy.spawn("ytmpv"),                desc="Launch youtube-mpv"),
    EzKey("<Print>",                lazy.spawn("xfce4-screenshooter"),                desc="Launch screen capturer"),
    EzKey("A-<Print>",              lazy.spawn("xfce4-screenshooter -w --no-border"), desc="Capture window"),
    EzKey("S-<Print>",              lazy.spawn("xfce4-screenshooter -f"),             desc="Capture screen"),
    EzKey("C-<Print>",              lazy.spawn("flameshot gui"),                      desc="Capture selection"),
    # Misc
    EzKey("<XF86AudioMute>",        volume_control("toggle mute"),      desc="Toggle mute"),
    EzKey("<XF86AudioLowerVolume>", volume_control("down"),             desc="Volume down"),
    EzKey("<XF86AudioRaiseVolume>", volume_control("up"),               desc="Volume up"),
    EzKey("M-<F9>",                 volume_control("toggle mute"),      desc="Toggle mute"),
    EzKey("M-<F10>",                volume_control("down"),             desc="Volume down"),
    EzKey("M-<F11>",                volume_control("up"),               desc="Volume up"),
    EzKey("M-S-<F10>",              volume_control("boost down"),       desc="Volume down"),
    EzKey("M-S-<F11>",              volume_control("boost up"),         desc="Volume up"),
    EzKey("<XF86MonBrightnessDown>",backlight_control("down"),          desc="Backlight down"),
    EzKey("<XF86MonBrightnessUp>",  backlight_control("up"),            desc="Backlight up"),
    EzKey("M-<F3>",                 backlight_control("down"),          desc="Backlight down"),
    EzKey("M-<F4>",                 backlight_control("up"),            desc="Backlight up"),
    EzKey("M-m",                    increase_nmaster,                   desc="Increase the number of main windows"),
    EzKey("M-S-m",                  decrease_nmaster,                   desc="Decrease the number of main windows"),
    EzKey("M-b",                    lazy.hide_show_bar(),               desc="Toggle bar"),
    EzKey("M-<Tab>",                prev_group,                         desc="Switch to previous group"),
    EzKey("A-C-<delete>",           lazy.spawn("qtile-powermenu"),      desc="Launch powermenu"),
    EzKey("A-C-l",                  lazy.spawn("qtile-lock forcelock"), desc="Lock the session"),
    EzKey("M-S-C-r",                lazy.reload_config(),               desc="Reload the config"),
]

groups = [
    ScratchPad("scratchpad",
        [
            DropDown("spterm", "st",                        opacity=1.0, x=0.24, y=0.200, width=0.519, height=0.584),
            DropDown("spfm",   "st -e 'lf - File Manager'", opacity=1.0, x=0.20, y=0.158, width=0.594, height=0.685),
            DropDown("spcalc", "qalculate-gtk",             opacity=1.0, x=0.31, y=0.255, width=0.380, height=0.490),
        ]
    ),
    Group("1", label=""),
    Group("2", label=""),
    Group("3", label="", matches=[Match(wm_class=["Thunar"])]),
    Group("4", label="", matches=[Match(title=["LibreOffice", "Soffice"]),
                                   Match(wm_instance_class=["soffice"])]),
    Group("5", label=""),
    Group("6", label="", matches=[Match(wm_class=["Gimp"]),
                                   Match(title=["GIMP Startup", "GNU Image Manipulation Program"])]),
    Group("7", label=""),
    Group("8", label=""),
    Group("9", label=""),
]

for i in groups:
    if i.name == "scratchpad":
        keys.extend([
            EzKey("M-s", lazy.group['scratchpad'].dropdown_toggle('spterm'), desc="ScratchPad (terminal)"),
            EzKey("M-e", lazy.group['scratchpad'].dropdown_toggle('spfm'),   desc="ScratchPad (file manager)"),
            EzKey("M-c", lazy.group['scratchpad'].dropdown_toggle('spcalc'), desc="ScratchPad (calculator)"),
        ])
        continue
    keys.extend(
        [
            # mod + letter of group = switch to group
            EzKey("M-" + i.name,
                  lazy.group[i.name].toscreen(),
                  desc="Switch to group {}".format(i.name)
            ),
            # mod + shift + letter of group = move focused window to group
            EzKey("M-S-" + i.name,
                  lazy.window.togroup(i.name),
                  desc="Move focused window to group {}".format(i.name)
            ),
            # mod + control + letter of group = move windows from group to current group
            EzKey("M-C-" + i.name,
                  fetch_windows(i.name), 
                  desc="Move windows from group {} to current group".format(i.name)
            ),
        ]
    )

colors = dict(
    # Bar backround
    bar_bg = "#07070d",
    # window borders and title
    win_border_sel = "#AEC2C6",
    win_border_norm = "#404040",
    win_fg_sel = "#E5FBFF",
    # groupbox
    grp_fg_sel = "#E5FBFF",
    grp_fg_norm = "#A0A7B3",
    grp_bg_sel = ["#4F4F4F", "#4F4F4F"],
    grp_border_sel = "#E5FBFF",
    grp_border_norm = "#A0A7B3",
    # status monitor
    mon_clock_icon = "#FFFFFF",
    mon_cpu_icon = "#FFFFFF",
    mon_backlight_icon = "#FFFFFF",
    mon_battery_icons = ["#FF0000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#00FF00"],
    mon_mem_icon = "#FFFFFF",
    mon_net_icons = ["#808080", "#FFFFFF"],
    mon_volume_icon = "#FFFFFF",
    mon_text = "#E5FBFF",
    )

layout_theme = dict(
    border_focus = colors["win_border_sel"],
    border_normal = colors["win_border_norm"],
    border_width = 2,
    margin = 7,
    single_margin = 7,
    single_border_width = 0,
)

layouts = [
    layout.MonadTall(
        **layout_theme, ratio=0.55,
    ),
    layout.MonadWide(
        **layout_theme, ratio=0.50
    ),
    layout.Tile(
        **layout_theme, ratio=0.50, master_length=2, shift_windows=True, border_on_single=False,
    ),
    MonadDeck(
        **layout_theme, ratio=0.55
    ),
    layout.MonadThreeCol(
        **layout_theme, ratio=0.45
    ),
    layout.Floating(
        border_focus = layout_theme["border_focus"],
        border_normal = layout_theme["border_normal"],
        border_width = layout_theme["border_width"],
    ),
    layout.Max(),
]

widget_defaults = dict(
    font = "Mononoki Nerd Font",
    fontsize = 13.2,
    foreground = colors["mon_text"],
    background = colors["bar_bg"],
    padding = 0,
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.GroupBox(
                    highlight_method = "line",
                    highlight_color = colors["grp_bg_sel"],
                    block_highlight_text_color = colors["grp_fg_sel"],
                    this_current_screen_border = colors["grp_border_sel"],
                    this_screen_border = colors["grp_border_norm"],
                    other_current_screen_border = colors["grp_border_norm"],
                    other_screen_border = colors["grp_border_norm"],
                    active = colors["grp_fg_sel"],
                    inactive = colors["grp_fg_norm"],
                    borderwidth = 2,
                    font = "monospace",
                    fontsize = 15,
                    margin_x = 0,
                    margin_y = 4,
                    spacing = 1,
                    padding = 3,
                ),
                CurrentLayoutIcon(
                    foreground = colors["win_fg_sel"],
                    custom_icon_paths = [expanduser("~/.config/qtile/icons")],
                    scale = 0.7,
                    use_mask = True,
                    padding = 8,
                ),
                widget.WindowName(
                    foreground = colors["win_fg_sel"],
                    font = "Fira Sans Dwm",
                    fontsize = 13.7,
                    mouse_callbacks  =  {
                        'Button1': toggle_minimize,
                        'Button3': lazy.spawn("xmenu-apps"),
                    },
                    padding = 2,
                ),
                CapslockWidget(
                    update_interval = 86400,
                ),
                BacklightWidget(
                    icon_color = colors["mon_backlight_icon"],
                    backlight_name = "",
                    hide = True,
                    step = 5,
                    update_interval = 2,
                ),
                VolumeWidget(
                    icon_color = colors["mon_volume_icon"],
                    mouse_callbacks = {
                        'Button1': lazy.spawn("pavucontrol"),
                        'Button3': volume_control("toggle mute"),
                        'Button4': volume_control("up"),
                        'Button5': volume_control("down"),
                    },
                    step = 5,
                    update_interval = 2.5,
                ),
                widget.TextBox(" | "),
                CpuWidget(
                    icon_color = colors["mon_cpu_icon"],
                    mouse_callbacks = {'Button1': lazy.spawn("st -e htop -s PERCENT_CPU")},
                    update_interval = 2,
                ),
                widget.TextBox(" | "),
                MemWidget(
                    icon_color = colors["mon_mem_icon"],
                    update_interval = 3,
                ),
                widget.TextBox(" | "),
                BatteryWidget(
                    icon_colors = colors["mon_battery_icons"],
                    update_interval = 7,
                ),
                widget.TextBox(" | "),
                ClockWidget(
                    icon_color = colors["mon_clock_icon"],
                    format = "%-H:%M",
                    format_alt = "%a %-d.%b %-H:%M",
                    update_interval = 5,
                ),
                widget.TextBox(" |"),
                widget.Spacer(length=5),
                NetWidget(
                    icon_colors = colors["mon_net_icons"],
                    mouse_callbacks = {
                        'Button1': lazy.spawn("networkmanager_dmenu"),
                        'Button3': lazy.spawn("nm-connection-editor"),
                    },
                    update_interval = 4,
                ),
                widget.Systray(icon_size=17, padding=2),
                widget.Spacer(length=3),
            ],
            23,
        ),
    ),
]

# Drag floating layouts.
mouse = [
    Drag(["mod4"],  "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag(["mod4"],  "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click(["mod4"], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = False
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(wm_class="Dragon-drop"),
        Match(wm_class="Gnome-calculator"),
        Match(wm_class="Galculator"),
        Match(wm_class="Pavucontrol"),
        Match(wm_class="flameshot"),
        Match(wm_class="Yad"),
        Match(wm_class="pinentry-gtk-2"),  # GPG key password entry
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ],
    border_focus = colors["win_border_sel"],
    border_normal = colors["win_border_norm"],
    border_width = 2,
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
