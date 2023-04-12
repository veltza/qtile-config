import subprocess
from libqtile.widget import Battery
from libqtile.widget.battery import BatteryState

class BatteryWidget(Battery):
    defs = [
        ("icon_colors", ["#FF0000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#00FF00"], "icon colors"),
        ("notifications", True, "show notifications"),
        ("notification_id", 5557, "id for notifications"),
    ]

    CRIT_CAP = 7        # critical capacity level
    LOW_CAP = 15        # low capacity level
    MED_CAP = 59        # medium capacity level

    LOW_COLOR = 0       # charge:  0% .. 15% 
    MED_COLOR = 1       # charge: 16% .. 59%
    HIGH_COLOR = 2      # charge: 60% .. 100%
    CHARGING_COLOR = 3  # charging
    FULL_COLOR = 4      # full and powered

    def __init__(self, **config):
        Battery.__init__(self, **config)
        self.add_defaults(BatteryWidget.defs)
        self.add_callbacks({"Button1": self.toggle_format})
        self.charging_icons = [ " ", " ", " ", " ", " ", " ", " " ]
        self.discharging_icons = [ "", "", "", "", "", "", "", "", "", "", "" ]
        self.show_time = 0
        self.crit_warning = False
        self.low_warning = False
        self.full_warning = False
        self.state_old = 0
        try:
            self.state_old = self._battery.update_status().state
        except:
            pass

    def _send_notification(self, timeout, text, critical=False):
        if self.notifications:
            args = ["/usr/bin/dunstify", "-t", f"{timeout}",
                    "-r", f"{self.notification_id}", f"{text}"];
            if critical:
                args.insert(1, "critical")
                args.insert(1, "-u")
            subprocess.run(args, capture_output=False)

    def _remove_notification(self):
        if self.notifications:
            subprocess.run(["/usr/bin/dunstify", "-C", f"{self.notification_id}"], capture_output=False)

    def toggle_format(self):
        self.show_time = 0 if self.show_time else 1
        self.update(self.poll())

    def mouse_enter(self, *args, **kwargs):
        self.qtile.core._root.set_cursor("hand2")

    def mouse_leave(self, *args, **kwargs):
        self.qtile.core._root.set_cursor("left_ptr")

    def poll(self):
        """Determine the text to display
        Function returning a string with battery information to display on the
        status bar. Should only use the public interface in _Battery to get
        necessary information for constructing the string.
        """
        try:
            status = self._battery.update_status()
        except RuntimeError as e:
            return "Error: {}".format(e)

        text_color = self.foreground
        percent = int(status.percent * 100 + 0.5)

        # remove notifications when battery is being plugged in or out
        if ((status.state == BatteryState.DISCHARGING and self.state_old == BatteryState.CHARGING)
            or (status.state == BatteryState.DISCHARGING and self.state_old == BatteryState.FULL)
            or (status.state == BatteryState.CHARGING and self.state_old == BatteryState.DISCHARGING)
            or (status.state == BatteryState.CHARGING and self.state_old == BatteryState.EMPTY)):
            self._remove_notification();

        # clear certain warning triggers when battery is plugged in or out
        if status.state == BatteryState.CHARGING:
            self.crit_warning = False
            self.low_warning = False
            self.show_time = self.show_time & 1
        elif status.state == BatteryState.DISCHARGING:
            self.full_warning = False

        # send warning, if battery is critical
        if (status.state == BatteryState.DISCHARGING
            and percent <= self.CRIT_CAP and not self.crit_warning):
            self._send_notification(0, "Battery level is critical!", True)
            self.show_time = self.show_time | 2
            self.crit_warning = True

        # send warning, if battery is low
        if (status.state == BatteryState.DISCHARGING
            and percent <= self.LOW_CAP and not self.crit_warning and not self.low_warning):
            self._send_notification(0, "Battery level is low!")
            self.show_time = self.show_time | 2
            self.low_warning = True

        # send notification, if battery is fully charged
        if (status.state != BatteryState.DISCHARGING
            and percent >= 100 and not self.full_warning):
            self._send_notification(0, "Battery is fully charged")
            self.full_warning = True

        if self.show_time:
            hour = status.time // 3600
            minute = (status.time // 60) % 60
            time = f" ({hour}:{minute:02})"
        else:
            time = ""

        if status.state == BatteryState.CHARGING or status.state == BatteryState.FULL:
            icons = self.charging_icons
            if percent < 100:
                icon_color = self.icon_colors[BatteryWidget.CHARGING_COLOR]
            else:
                icon_color = self.icon_colors[BatteryWidget.FULL_COLOR]
        else:
            icons = self.discharging_icons
            if percent < 10:
                text_color = self.icon_colors[BatteryWidget.LOW_COLOR] 
            if percent <= BatteryWidget.LOW_CAP:
                icon_color = self.icon_colors[BatteryWidget.LOW_COLOR]
            elif percent <= BatteryWidget.MED_CAP:
                icon_color = self.icon_colors[BatteryWidget.MED_COLOR]
            else:
                icon_color = self.icon_colors[BatteryWidget.HIGH_COLOR]

        icon = icons[int(((len(icons)-1) * percent + 50) / 100)]
        self.state_old = status.state

        return  f'<span foreground="{icon_color}">{icon}</span> <span foreground="{text_color}">{percent}%{time}</span>'
