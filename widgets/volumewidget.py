from libqtile.widget import base
import subprocess
import time

class VolumeWidget(base.ThreadPoolText):
    defaults = [
        ("icon_color", "#FFFFFF", "icon color"),
        ("step", 5, "Percent of volume step"),
        ("update_interval", None, "Update interval for the clock widget"),
        ("notifications", True, "show notifications"),
        ("notification_font", "Mononoki Nerd Font 15", "font for notifications"),
        ("notification_time", 1500, "expiration time (in milliseconds) for notifications"),
        ("notification_id", 5555, "id for notifications"),
    ]

    LO_VOL = 20
    HI_VOL = 75

    def __init__(self, **config):
        base.ThreadPoolText.__init__(self, "", **config)
        self.add_defaults(VolumeWidget.defaults)
        self.vol_left = 0
        self.vol_right = 0
        self.mute = 0
        self.headphones = 0
        self.icons = [[" ", " ", " ", " "], [" ", " ", " ", " "]]
        self._future = None
        self.prev_timestamp = None

    def _get_icon(self, vol_left, vol_right, mute, headphones):
        vol = vol_left if vol_left > vol_right else vol_right
        idx = 0 if mute else 1 if vol <= VolumeWidget.LO_VOL else 2 if vol < VolumeWidget.HI_VOL else 3
        return self.icons[headphones & 1][idx]

    def _send_notification(self, vol_left, vol_right, mute, mute_changed, headphones):
        if not self.notifications:
            return
        if mute and mute_changed:
            volume = "Mute"
        elif vol_left == vol_right:
            volume = f"{vol_left}%"
        else:
            volume = f"L: {vol_left}% R: {vol_right}%"
        icon = self._get_icon(vol_left, vol_right, mute, headphones)
        subprocess.run(["/usr/bin/dunstify", "-t", f"{self.notification_time}", "-r",
                        f"{self.notification_id}", "--icon=no-icon", "",
                        f"<span font='{self.notification_font}'> {icon} {volume} \n</span>"],
                       capture_output=False)

    def _change_volume(self, vol_left, vol_right, mute, headphones, vol_changed, mute_changed):
        self._send_notification(vol_left, vol_right, mute, mute_changed, headphones)
        if vol_changed:
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@",
                            f"{vol_left}%", f"{vol_right}%"], capture_output=False)
        if mute_changed:
            subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@",
                            f"{mute}%"], capture_output=False)
        self.mute = mute
        self.vol_left = vol_left
        self.vol_right = vol_right
        self.headphones = headphones
        self.update(self._render(vol_left, vol_right, mute, headphones))

    def _render(self, vol_left, vol_right, mute, headphones):
        icon = self._get_icon(vol_left, vol_right, mute, headphones)
        icon = f'<span foreground="{self.icon_color}">{icon}</span>'
        if mute:
            return f'{icon}'
        if vol_left == vol_right:
            return f'{icon} {vol_left}%'
        else:
            return f'{icon} {vol_left}% {vol_right}%'

    def mouse_enter(self, *args, **kwargs):
        self.qtile.core._root.set_cursor("hand2")

    def mouse_leave(self, *args, **kwargs):
        self.qtile.core._root.set_cursor("left_ptr")

    def volume_control(self, cmd, step=None):
        if self._future and not self._future.done():
            return

        cur_timestamp = time.time()

        if self.prev_timestamp is None or cur_timestamp - self.prev_timestamp > 0.5:
            info = subprocess.run("qtile-pulseinfo", capture_output=True)
            if info.returncode != 0:
                return
            info = info.stdout.split()
            if len(info) < 3:
                return
            mute = int(info[0])
            vol_left = int(info[1])
            vol_right = int(info[2])
            headphones = int(info[3])
        else:
            mute = self.mute
            vol_left = self.vol_left
            vol_right = self.vol_right
            headphones = self.headphones

        self.prev_timestamp = cur_timestamp

        if "up" in cmd or "down" in cmd:
            step = int(self.step) if not step else int(step)
            step = -step if "down" in cmd else step
            vol_max = 150 if "boost" in cmd else 100 
            vol_left = max(min(vol_left + step, vol_max), 0)
            vol_right = max(min(vol_right + step, vol_max), 0)
            mute = 0 if step > 0 else mute
        elif cmd == "toggle mute":
            mute = 0 if mute else 1

        vol_changed = (vol_left != self.vol_left or vol_right != self.vol_right)
        mute_changed = (mute != self.mute)

        self._future = self.qtile.run_in_executor(self._change_volume,
                                                  vol_left, vol_right,
                                                  mute, headphones,
                                                  vol_changed, mute_changed)

    def poll(self):
        info = subprocess.run("qtile-pulseinfo", capture_output=True)
        if info.returncode != 0:
            return f'{self.icons[0][1]}ERR'
        info = info.stdout.split()
        if len(info) < 3:
            return f'{self.icons[0][1]}-'

        self.mute = int(info[0])
        self.vol_left = int(info[1])
        self.vol_right = int(info[2])
        self.headphones = int(info[3])
        return self._render(self.vol_left, self.vol_right, self.mute, self.headphones)
