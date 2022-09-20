import pygame
import time

from config import Colors, PIXEL_SIZE
from train import TrainDeparture

led_panels = []

def init_display():
    global screen
    screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
    pygame.display.init()
    pygame.display.set_caption('Live Train Times') 

def init_led_panels():
    global led_panels, screen
    scr_w, scr_h = screen.get_width(), screen.get_height()
    led_panels = [
        TrainDeparture(
            scr_w//PIXEL_SIZE,
            (scr_h - 120)//PIXEL_SIZE,
            PIXEL_SIZE,
            0, 120,
            crs="MAN",
        ),
    ]

def render_decorations():
    global screen
    screen.fill(Colors.SCREEN_BG)
    for led in led_panels:
        led.draw_decorations(screen)
    pygame.display.flip()

def update():
    global led_panels, screen

    for led in led_panels:
        led.update()
        led.render(screen)

    pygame.display.flip()

def main_loop():
    running = True
    while running:
        for event in pygame.event.get():  
            if event.type == pygame.QUIT:  
                running = False

        update()
        time.sleep(0.5)

if __name__ == "__main__":
    pygame.init()
    init_display()
    init_led_panels()
    render_decorations()
    main_loop()
