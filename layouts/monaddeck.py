# -*- coding: utf-8 -*-

from libqtile.layout.xmonad import MonadTall

class MonadDeck(MonadTall):
    def __init__(self, **config):
        MonadTall.__init__(self, **config)
        self.current_shared = 1

    def configure(self, client, screen_rect):
        "Position client based on order and sizes"
        self.screen_rect = screen_rect

        # if no sizes or normalize flag is set, normalize
        if not self.relative_sizes or self.do_normalize:
            self.normalize(False)

        # if client not in this layout
        if not self.clients or client not in self.clients:
            client.hide()
            return

        # determine focus border-color
        if client.has_focus:
            px = self.border_focus
        else:
            px = self.border_normal

        # single client - fullscreen
        if len(self.clients) == 1:
            client.place(
                self.screen_rect.x,
                self.screen_rect.y,
                self.screen_rect.width - 2 * self.single_border_width,
                self.screen_rect.height - 2 * self.single_border_width,
                self.single_border_width,
                px,
                margin=self.single_margin,
            )
            client.unhide()
            return
        cidx = self.clients.index(client)
        self._configure_specific(client, screen_rect, px, cidx)

    def _configure_specific(self, client, screen_rect, px, cidx):
        """Specific configuration for xmonad deck."""
        self.screen_rect = screen_rect

        # calculate main/secondary pane size
        width_main = int(self.screen_rect.width * self.ratio)
        width_shared = self.screen_rect.width - width_main

        # calculate client's x offset
        if self.align == self._left:  # left or up orientation
            if cidx == 0:
                # main client
                xpos = self.screen_rect.x
            else:
                # secondary client
                xpos = self.screen_rect.x + width_main
        else:  # right or down orientation
            if cidx == 0:
                # main client
                xpos = self.screen_rect.x + width_shared - self.margin
            else:
                # secondary client
                xpos = self.screen_rect.x

        if self.clients.current_index > 0:
            self.current_shared = self.clients.current_index 
        if self.current_shared >= len(self.clients):
            self.current_shared = len(self.clients)-1

        # calculate client height and place
        if cidx > 0:
            # secondary client
            if cidx == self.current_shared:
                client.place(
                    xpos,
                    self.screen_rect.y,
                    width_shared - 2 * self.border_width,
                    self.screen_rect.height - 2 * self.border_width,
                    self.border_width,
                    px,
                    margin=self.margin,
                )
                client.unhide()
            else:
                client.hide()
        else:
            # main client
            client.place(
                xpos,
                self.screen_rect.y,
                width_main,
                self.screen_rect.height,
                self.border_width,
                px,
                margin=[
                    self.margin,
                    2 * self.border_width,
                    self.margin + 2 * self.border_width,
                    self.margin,
                ],
            )
            client.unhide()
