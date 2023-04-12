import os
import subprocess
from libqtile.widget import Backlight
from libqtile.log_utils import logger

class BacklightWidget(Backlight):
    defaults = [
        ("icon_color", "#FFFFFF", "icon color"),
        ("hide", False, "hide the widget"),
        ("notifications", True, "show notifications"),
        ("notification_font", "Mononoki Nerd Font 15", "font for notifications"),
        ("notification_time", 1500, "expiration time (in milliseconds) for notifications"),
        ("notification_id", 5555, "id for notifications"),
    ]

    def __init__(self, **config):
        Backlight.__init__(self, **config)
        self.add_defaults(BacklightWidget.defaults)
        self.icon = ' '
        self.brightness = 0
        self.max_brightness = 0
        self.percentage = 0
        if not self.backlight_name:
            self._detect_backlight()
        if self.backlight_name:
            self.brightness = self._load_file(self.brightness_file)
            self.max_brightness = self._load_file(self.max_brightness_file)
            self.percentage = max(int(100 * self.brightness / self.max_brightness), 0)
            self.percentage = int((self.percentage + 3) / 5) * 5;  # round to nearest 5
            try:
                with open(self.brightness_file, "w") as f:
                    f.write(str(int(self.brightness)))
            except PermissionError:
                logger.warning("Cannot set brightness: no write permission for %s", self.brightness_file)
                self.backlight_name = None
            except Exception as e:
                logger.warning("Cannot set brightness: %s", e)
                self.backlight_name = None
        else:
            logger.warning("backlight_name is not set")

    def _detect_backlight(self):
        backlight_dir = "/sys/class/backlight"
        for backlight in os.listdir(backlight_dir):
            try:
                with open(f"{backlight_dir}/{backlight}/max_brightness") as f:
                    max_brightness = int(f.read().strip())
                if self.max_brightness <= max_brightness:
                    self.max_brightness = max_brightness
                    self.backlight_name = backlight
                    self.brightness_file = f"{backlight_dir}/{backlight}/brightness"
                    self.max_brightness_file = f"{backlight_dir}/{backlight}/max_brightness"
            except:
                pass
        if not self.backlight_name:
            logger.warning("Cannot detect the backlight device")

    def _load_file(self, path):
        try:
            with open(path, "r") as f:
                return int(f.read().strip())
        except FileNotFoundError:
            logger.debug("Failed to get %s", path)
            raise RuntimeError("Unable to read status for {}".format(os.path.basename(path)))

    def _send_notification(self):
        if self.notifications:
            subprocess.run(["/usr/bin/dunstify", "-t", f"{self.notification_time}", "-r",
                            f"{self.notification_id}", "--icon=no-icon", "",
                            f"<span font='{self.notification_font}'> {self.icon} {self.percentage}% \n</span>"],
                            capture_output=False)

    def _change_backlight(self, value):
        self.percentage = value
        self.brightness = min(int(self.max_brightness * self.percentage / 100), self.max_brightness)
        try:
            with open(self.brightness_file, "w") as f:
                f.write(str(int(self.brightness)))
        except PermissionError:
            logger.warning("Cannot set brightness: no write permission for %s", self.brightness_file)
        self._send_notification()
        self.update(self.poll())

    def poll(self):
        if not self.backlight_name:
            return  f'<span foreground="{self.icon_color}">{self.icon}</span> ERR | '
        brightness = self._load_file(self.brightness_file)
        if self.brightness != brightness:
            self.brightness = brightness
            self.percentage = max(int(100 * self.brightness / self.max_brightness), 0)
            self._send_notification()
        if self.hide:
            return "";
        else:
            return  f'<span foreground="{self.icon_color}">{self.icon}</span> {self.percentage}% | '

    def cmd_change_backlight(self, direction, step=None):
        if not self.backlight_name:
            return
        if self._future and not self._future.done():
            return
        if not step:
            step = self.step
        if direction == "up":
            percentage = min(self.percentage + step, 100)
        elif direction == "down":
            percentage = max(self.percentage - step, 0)
        else:
            return;
        self._future = self.qtile.run_in_executor(self._change_backlight, percentage)
