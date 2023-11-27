import re
import subprocess

from libqtile.widget import base


class CapslockWidget(base.ThreadPoolText):
    defaults = [
        ("update_interval", 1, "Update time in seconds"),
        ("notifications", True, "show notifications"),
        ("notification_font", "JetBrainsMono NF 12", "font for notifications"),
        ("notification_time", 2000, "expiration time (in milliseconds) for notifications"),
        ("notification_id", 5559, "id for notifications"),
    ]

    def __init__(self, **config):
        base.ThreadPoolText.__init__(self, "", **config)
        self.add_defaults(CapslockWidget.defaults)
        self.oldstatus = ""

    def _send_notification(self, status):
        if not self.notifications or status == self.oldstatus:
            return
        status = " Caps Lock On" if status else " Caps Lock Off"
        subprocess.run(["/usr/bin/dunstify", "-t", f"{self.notification_time}", "-r",
                        f"{self.notification_id}", "--icon=no-icon", "",
                        f"<span font='{self.notification_font}'> {status} \n</span>"],
                       capture_output=False)

    def get_indicators(self):
        """Return a list with the current state of the keys."""
        try:
            output = self.call_process(["xset", "q"])
        except subprocess.CalledProcessError as err:
            output = err.output
            return []
        if output.startswith("Keyboard"):
            indicators = re.findall(r"(Caps|Num)\s+Lock:\s*(\w*)", output)
            return indicators

    def poll(self):
        """Poll content for the text box."""
        indicators = self.get_indicators()
        status = " ".join([" ".join(indicator) for indicator in indicators])
        status = "CAPS | " if "Caps on" in status else ""
        self._send_notification(status)
        self.oldstatus = status
        return status
