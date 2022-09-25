import argparse

CLK_FREQ = 8
PIXEL_SIZE  = 4

class Colors():
    SCREEN_BG = (10, 10, 10)

    LED_FG = (249, 154, 12)
    LED_BG = (38, 29, 18)

# Train LDBWS
LDBWS_TOKEN = "your-ldbws-token-here"

parser = argparse.ArgumentParser(description="Live Train Times help")
parser.add_argument("--mode", type=str, help="Display Mode")
