import argparse

CLK_FREQ = 8
PIXEL_SIZE  = 5

class Colors():
    SCREEN_BG = (10, 10, 10)

    LED_FG = (249, 154, 12)
    LED_BG = (38, 29, 18)

parser = argparse.ArgumentParser(description="Live Train Times help")
parser.add_argument("--mode", type=str, help="Display Mode")
