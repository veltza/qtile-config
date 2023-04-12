from os import listdir
from os.path import exists
from socket import AF_INET, AF_INET6
from libqtile.widget import base
import psutil

class NetWidget(base.InLoopPollText):
    defaults = [
        ("icon_colors", ["#808080", "#FFFFFF"], "icon colors (inactive, active)"),
        ("update_interval", 3.0, "Update interval for the memory widget"),
    ]

    NETWORK_INTERFACES = "/sys/class/net"

    def __init__(self, **config):
        base.InLoopPollText.__init__(self, **config)
        self.add_defaults(NetWidget.defaults)
        self.last_connection = 'eth'
        self.eth_icon = ' '
        self.wifi_icon = ' '

    def _is_connected(self, iface):
        try:
            with open(f"{NetWidget.NETWORK_INTERFACES}/{iface}/carrier") as f:
                if f.read() == 0:
                    return 0
            with open(f"{NetWidget.NETWORK_INTERFACES}/{iface}/operstate") as f:
                if f.read().strip() != "up":
                    return 0
        except:
            return 0

        addrs = psutil.net_if_addrs()
        if iface in addrs:
            for addr in addrs[iface]:
                if addr.family == AF_INET or addr.family == AF_INET6:
                    return 1
        return 0

    def _read_network_status(self):
        status = {"eth": 0, "wifi": 0}
        for iface in listdir(NetWidget.NETWORK_INTERFACES):
            try:
                with open(f"{NetWidget.NETWORK_INTERFACES}/{iface}/type") as f:
                    if int(f.read()) != 772:
                        type = "wifi" if exists(f"{NetWidget.NETWORK_INTERFACES}/{iface}/wireless") else "eth"
                        type = "wifi" if exists(f"{NetWidget.NETWORK_INTERFACES}/{iface}/phy80211") else type
                        status[type] = status[type] or self._is_connected(iface)
            except:
                pass
        return status

    def mouse_enter(self, *args, **kwargs):
        self.qtile.core._root.set_cursor("hand2")

    def mouse_leave(self, *args, **kwargs):
        self.qtile.core._root.set_cursor("left_ptr")

    def poll(self):
        net_status = self._read_network_status()
        eth_icon = f'<span foreground="{self.icon_colors[net_status["eth"]]}">{self.eth_icon}</span>'
        wifi_icon = f'<span foreground="{self.icon_colors[net_status["wifi"]]}">{self.wifi_icon}</span>'

        if net_status["eth"] and not net_status["wifi"]:
            self.last_connection = "eth"
        elif not net_status["eth"] and net_status["wifi"]:
            self.last_connection = "wifi"

        if net_status["eth"] and net_status["wifi"]:
            return f'{eth_icon}{wifi_icon}'
        elif net_status["eth"] or self.last_connection == "eth":
            return f'{eth_icon}'
        else:
            return f'{wifi_icon}'
