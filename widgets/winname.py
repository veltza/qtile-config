from libqtile import pangocffi
from libqtile.log_utils import logger
from libqtile.widget import WindowName
from sticky import is_sticky_window

class WinName(WindowName):
    def hook_response(self, *args):
        if self.for_current_screen:
            w = self.qtile.current_screen.group.current_window
        else:
            w = self.bar.screen.group.current_window
        state = ""
        if w:
            if w.maximized:
                state = "[] "
            elif w.minimized:
                state = "_ "
            elif w.floating:
                state = "V "
            if is_sticky_window(w):
                state = "+ " + state
            var = {}
            var["state"] = state
            var["name"] = w.name
            if callable(self.parse_text):
                try:
                    var["name"] = self.parse_text(var["name"])
                except:  # noqa: E722
                    logger.exception("parse_text function failed:")
            wm_class = w.get_wm_class()
            var["class"] = wm_class[0] if wm_class else ""
            unescaped = self.format.format(**var)
        else:
            unescaped = self.empty_group_string
        self.update(pangocffi.markup_escape_text(unescaped))
