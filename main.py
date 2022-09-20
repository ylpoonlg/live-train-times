import pygame
import time

from config import Colors, UPDATE_INTERVAL
from train import TrainDeparture

led_panels = [
    TrainDeparture(320, 160, 6, 0, 100),
]

def init_display():
    global screen
    screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
    pygame.display.init()

def render_decorations():
    global screen
    screen.fill(Colors.SCREEN_BG)
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
    render_decorations()
    main_loop()
