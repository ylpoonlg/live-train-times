import pygame
import time

from config import CLK_FREQ, Colors, PIXEL_SIZE, parser
from train import TrainDeparture

led_panels = []
cur_mode   = "traindep0"

def init_display():
    global screen
    screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
    pygame.display.init()
    pygame.display.set_caption('Live Train Times') 

def init_led_panels():
    global led_panels, screen
    scr_w, scr_h = screen.get_width(), screen.get_height()
    if cur_mode == "traindep0":
        led_panels = [
            TrainDeparture(
                scr_w//PIXEL_SIZE,
                (scr_h - 120)//PIXEL_SIZE,
                PIXEL_SIZE,
                0, 120,
            ),
        ]
    else:
        led_panels = []

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
        time.sleep(1/CLK_FREQ)

if __name__ == "__main__":
    pygame.init()
    args, _ = parser.parse_known_args()
    if args.mode != None:
        cur_mode = args.mode
    init_display()
    init_led_panels()
    render_decorations()
    main_loop()
