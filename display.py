from config import Colors
from fonts import Fonts, FontStyles
import pygame

class Display():
    def __init__(self, w, h, px_sep, x, y):
        self.w, self.h = w, h
        self.x, self.y = x, y 
        self.px_sep   = px_sep
        self.pixels   = [[Colors.LED_BG for _ in range(w)] for _ in range(h)]
        self.cache_px = [[Colors.SCREEN_BG for _ in range(w)] for _ in range(h)]

    def get_text_length(self, text, style = FontStyles.REGU):
        text = self.abbrv(text)
        xx = 1
        for c in text:
            if style == FontStyles.BOLD:
                letter = Fonts.bold.get(c, Fonts.bold.get('-', []))
            elif style == FontStyles.NARR:
                letter = Fonts.narrow.get(c, Fonts.narrow.get('-', []))
            elif style == FontStyles.LARG:
                letter = Fonts.large.get(c, Fonts.large.get('-', []))
            else:
                letter = Fonts.regular.get(c, Fonts.regular.get('-', []))

            lw = len(letter[0])
            xx += lw + 1

        return xx - 1

    def print(self, text: str, x: int, y: int,
            w: int = -1, color = Colors.LED_FG, style = FontStyles.REGU,
            ticks: int = -1,
            ):
        text = self.abbrv(text)
        text_length = self.get_text_length(text, style)
        if w == -1:
            w = text_length

        if text_length <= w or ticks == -1:
            xoffset = 0
        else:
            xoffset = (ticks*4) % (text_length+w+5) - w

        font_size = 9
        if style == FontStyles.LARG:
            font_size = 13

        for i in range(x, x+w):
            for j in range(font_size):
                if y+j < self.h and i < self.w:
                    self.pixels[y+j][i] = Colors.LED_BG

        xx = x
        for c in text:
            if style == FontStyles.BOLD:
                letter = Fonts.bold.get(c, Fonts.bold.get('-', []))
            elif style == FontStyles.NARR:
                letter = Fonts.narrow.get(c, Fonts.narrow.get('-', []))
            elif style == FontStyles.LARG:
                letter = Fonts.large.get(c, Fonts.large.get('-', []))
            else:
                letter = Fonts.regular.get(c, Fonts.regular.get('-', []))

            lw, lh = len(letter[0]), len(letter)

            for i in range(font_size):
                for j in range(lw+1):
                    x_pos = x+j-xoffset
                    if y+i < self.h and x_pos < self.w and x_pos < xx + w and x_pos >= xx:
                        if i < lh and j < lw:
                            if letter[i][j] == 1:
                                self.pixels[y+i][x_pos] = color
                            else:
                                self.pixels[y+i][x_pos] = Colors.LED_BG
                        else:
                            self.pixels[y+i][x_pos] = Colors.LED_BG

            x += lw + 1


    def draw_rect(self, x, y, w, h, color = Colors.SCREEN_BG):
        for i in range(h):
            for j in range(w):
                if y+i < self.h and x+j < self.w:
                    self.pixels[y+i][x+j] = color


    def render(self, screen):
        pixels = self.pixels
        px_size = self.px_sep * 0.45
        for i in range(len(pixels)):
            for j in range(len(pixels[0])):
                if self.cache_px[i][j] != pixels[i][j]:
                    pygame.draw.circle(
                        screen,
                        pixels[i][j],
                        (
                            self.x + int((j + 1) * self.px_sep),
                            self.y + int((i + 1) * self.px_sep),
                        ),
                        px_size,
                    )
                    self.cache_px[i][j] = pixels[i][j]

    def draw_decorations(self, screen):
        pass

    def update(self):
        pass

    def abbrv(self, text) -> str:
        return text
