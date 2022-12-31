def load_config():
    try:
        import config
        config.__file__
    except:
        import os
        import shutil
        print("No config file found\nCreating new config file")
        cur_path = os.path.dirname(__file__)
        default_file = cur_path+"/default_config.py"
        new_file     = cur_path+"/config.py"
        shutil.copyfile(default_file, new_file)

load_config()

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
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
                214,
                PIXEL_SIZE,
                0, 20 * PIXEL_SIZE,
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

def update(events):
    global led_panels, screen

    for led in led_panels:
        led.update(events = events)
        led.render(screen)

    pygame.display.flip()

def main_loop():
    running = True
    while running:
        events = pygame.event.get()
        for event in events:  
            if event.type == pygame.QUIT:  
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False

        update(events)
        time.sleep(1/CLK_FREQ)

    print("Stopping...")

if __name__ == "__main__":
    pygame.init()
    args, _ = parser.parse_known_args()
    if args.mode != None:
        cur_mode = args.mode
    init_display()
    init_led_panels()
    render_decorations()
    main_loop()
