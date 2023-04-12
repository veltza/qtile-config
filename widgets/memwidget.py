from libqtile.widget import base

class MemWidget(base.InLoopPollText):
    defaults = [
        ("icon_color", "#FFFFFF", "icon color"),
        ("update_interval", 3.0, "Update interval for the memory widget"),
    ]

    def __init__(self, **config):
        base.InLoopPollText.__init__(self, **config)
        self.add_defaults(MemWidget.defaults)
        self.add_callbacks({"Button1": self.toggle_format})
        self.format_percent = True
        self.icon = ' '

    def toggle_format(self):
        self.format_percent = not self.format_percent
        self.tick()

    def mouse_enter(self, *args, **kwargs):
        self.qtile.core._root.set_cursor("hand2")

    def mouse_leave(self, *args, **kwargs):
        self.qtile.core._root.set_cursor("left_ptr")

    def poll(self):
        total, free, buffers, cached, sreclaimable, n = 0, 0, 0, 0, 0, 0
        icon = f'<span foreground="{self.icon_color}">{self.icon}</span>'

        with open("/proc/meminfo") as f:
            for line in f:
                s = line.split()
                if s[0] == "MemTotal:":
                    total = int(s[1])
                    n = n + 1
                elif s[0] == "MemFree:":
                    free = int(s[1])
                    n = n + 1
                elif s[0] == "Buffers:":
                    buffers = int(s[1])
                    n = n + 1
                elif s[0] == "Cached:":
                    cached = int(s[1])
                    n = n + 1
                elif s[0] == "SReclaimable:":
                    sreclaimable = int(s[1])
                    n = n + 1
                if n >= 5:
                    break;

        if total == 0:
            return  f'{icon} ERR'

        used_diff = free + buffers + cached + sreclaimable;
        used = (total - used_diff) if total >= used_diff else (total - free)

        if self.format_percent:
            return f'{icon}{int(used/total*100+0.5):3}%'
        elif used < 1024000:
            return  f'{icon} {int(used/1024)}M/{total/1048576:.1f}G'
        elif used < 1048576:
            return  f'{icon} 1.0G/{total/1048576:.1f}G'
        else:
            return  f'{icon} {used/1048576:.1f}G/{total/1048576:.1f}G'
