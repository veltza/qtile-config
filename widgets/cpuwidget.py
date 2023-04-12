from libqtile.widget import base

class CpuWidget(base.InLoopPollText):
    defaults = [
        ("icon_color", "#FFFFFF", "icon color"),
        ("update_interval", 2.0, "Update interval for the cpu widget"),
    ]

    def __init__(self, **config):
        base.InLoopPollText.__init__(self, **config)
        self.add_defaults(CpuWidget.defaults)
        self.idle = 0
        self.total = 0
        self.icon = ' '

    def mouse_enter(self, *args, **kwargs):
        self.qtile.core._root.set_cursor("hand2")

    def mouse_leave(self, *args, **kwargs):
        self.qtile.core._root.set_cursor("left_ptr")

    def poll(self):
        idle, total, usage = 0, 0, 0

        with open("/proc/stat") as f:
            for line in f:
                s = line.split()
                if s.pop(0) == "cpu":
                    idle  = int(s[3])
                    total = sum((int(n) for n in s))

        if total > self.total and self.total:
            diff_total = total - self.total
            diff_idle = idle - self.idle
            if (diff_total > diff_idle and diff_idle > 0):
                usage = int((diff_total - diff_idle) / diff_total * 100 + 0.5)

        self.idle = idle
        self.total = total
        return  f'<span foreground="{self.icon_color}">{self.icon}</span>{usage:3}%'
