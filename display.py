from config import Colors
from fonts import Fonts, FontStyles
import pygame

class Display():
    def __init__(self, w, h, px_sep, x, y):
        self.w, self.h = w, h
        self.x, self.y = x, y 
        self.px_sep = px_sep
        self.pixels = [[Colors.LED_BG for j in range(w)] for i in range(h)]

    def get_text_length(self, text, style = FontStyles.REGU):
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

    def print(self, text: str, x: int, y: int, w: int = -1, color = Colors.LED_FG, style = FontStyles.REGU):
        if w == -1:
            w = self.get_text_length(text, style)

        xx = x
        font_size = 9
        for c in text:
            if style == FontStyles.BOLD:
                letter = Fonts.bold.get(c, Fonts.bold.get('-', []))
            elif style == FontStyles.NARR:
                letter = Fonts.narrow.get(c, Fonts.narrow.get('-', []))
            elif style == FontStyles.LARG:
                letter = Fonts.large.get(c, Fonts.large.get('-', []))
                font_size = 13
            else:
                letter = Fonts.regular.get(c, Fonts.regular.get('-', []))

            lw, lh = len(letter[0]), len(letter)

            for i in range(font_size):
                for j in range(lw+1):
                    if y+i < self.h and x+j < self.w and x+j < xx + w:
                        if i < lh and j < lw:
                            if letter[i][j] == 1:
                                self.pixels[y+i][x+j] = color
                            else:
                                self.pixels[y+i][x+j] = Colors.LED_BG
                        else:
                            self.pixels[y+i][x+j] = Colors.LED_BG

            x += lw + 1

        while x < xx + w and x < self.w:
            for i in range(font_size):
                self.pixels[y+i][x] = Colors.LED_BG
            x += 1

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
                pygame.draw.circle(
                    screen,
                    pixels[i][j],
                    (
                        self.x + int((j + 1) * self.px_sep),
                        self.y + int((i + 1) * self.px_sep),
                    ),
                    px_size,
                )
