from libqtile.widget import base
from libqtile.widget import Clock
from datetime import datetime, timezone

class ClockWidget(Clock):
    defaults = [
        ("format", "%-H:%M", "A Python datetime format string"),
        ("format_alt", "%a %-d.%b %-H:%M", "A Python datetime format string"),
        ("icon_color", "#FFFFFF", "icon color"),
        ("update_interval", 1.0, "Update interval for the clock widget"),
    ]

    def __init__(self, **config):
        Clock.__init__(self, **config)
        self.add_defaults(Clock.defaults)
        self.add_callbacks({"Button1": self.toggle_format})
        self.icon = ' '

    def toggle_format(self):
        self.format, self.format_alt = self.format_alt, self.format
        self.tick()

    def mouse_enter(self, *args, **kwargs):
        self.qtile.core._root.set_cursor("hand2")

    def mouse_leave(self, *args, **kwargs):
        self.qtile.core._root.set_cursor("left_ptr")

    def poll(self):
        if self.timezone:
            now = datetime.now(timezone.utc).astimezone(self.timezone)
        else:
            now = datetime.now(timezone.utc).astimezone()
        now = now + Clock.DELTA
        mon = now.strftime("%b").lower()[:3]    # abbreviate month, max 3 letters
        format = self.format.replace("%b", mon)
        text = now.strftime(format)
        return  f'<span foreground="{self.icon_color}">{self.icon}</span> {text}'
