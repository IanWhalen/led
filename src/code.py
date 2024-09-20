# SPDX-FileCopyrightText: 2022 Jeff Epler
#
# SPDX-License-Identifier: Unlicense

import board
import rainbowio
import adafruit_ticks
from adafruit_led_animation.color import AMBER, AQUA, BLACK, BLUE, GREEN, ORANGE, PINK, PURPLE, RED, WHITE, YELLOW, GOLD, JADE, MAGENTA, OLD_LACE, TEAL
from adafruit_led_animation.group import AnimationGroup
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.colorcycle import ColorCycle
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.animation.customcolorchase import CustomColorChase
import time


from adafruit_led_animation.helper import PixelMap
from adafruit_neopxl8 import NeoPxl8

# Customize for your strands here
num_strands = 3
strand_length = 120
first_led_pin = board.NEOPIXEL0

num_pixels = num_strands * strand_length

# Make the object to control the pixels
pixels = NeoPxl8(
    first_led_pin,
    num_pixels,
    num_strands=num_strands,
    auto_write=False,
    brightness=0.25,
)

def strand(n, pixels_count):
    return PixelMap(
        pixels,
        range(n * pixels_count, (n + 1) * pixels_count),
        individual_pixels=True,
    )


# Create the 8 virtual strands
strands = [strand(i, strand_length) for i in range(num_strands)]

def reconfigure_pixels(pixels_count, num_strands, brightness):
    global pixels
    pixels.fill(0)
    pixels.show()
    time.sleep(0.1)
    pixels.deinit()
    new_pixels = NeoPxl8(
        board.NEOPIXEL0,
        num_strands*pixels_count,
        num_strands=num_strands,
        auto_write=False,
        brightness=brightness,
    )
    pixels = new_pixels
    print('regenerated pixels')
    global strands
    strands = [strand(i, pixels_count) for i in range(num_strands)]
    print('regenerated strands')
    


# For each strand, create a comet animation of a different color
# animations = [
#     Comet(strand, 0.02, (255,255,255), ring=True)
#     for i, strand in enumerate(strands)
# ]

# working commands:     Pulse(strands[2], speed=0.2, color=(255,0,80), period=2),

    #Pulse(strands[1], speed=0.2, color=(255,0,80), period=2),
    #Pulse(strands[2], speed=0.2, color=(255,0,80), period=2),
    # Blink(strand[1], 0.02, (255,125,128)),
    #Sparkle(strand[3], 0.02, 2, (0,232,232))

    # Solid(strands[0], color=TEAL),
    #CustomColorChase(strands[0], speed=0.02, size=30, spacing=0, colors=[(50,255,5), (255,0,120), (255,0,5)])
animations = [
    Pulse(strands[0], speed=0.2, color=(255,0,80), period=2),
    Pulse(strands[1], speed=0.02, color=(255,0,80), period=5),
    Pulse(strands[2], speed=0.02, color=(255,0,80), period=5)
]

# Advance the animations by varying amounts so that they become staggered
# for i, animation in enumerate(animations):
#     animation._tail_start = 30 * 5 * i // 8  # pylint: disable=protected-access

# Group them so we can run them all at once
animations = AnimationGroup(*animations)

# Run the animations and report on the speed in frame per secodn
t0 = adafruit_ticks.ticks_ms()
frame_count = 0
count = 0

while count < 5000:
    animations.animate()
    frame_count += 1
    count += 1
    t1 = adafruit_ticks.ticks_ms()
    dt = adafruit_ticks.ticks_diff(t1, t0)
    if dt > 1000:
        print(f"{frame_count * 1000/dt:.1f}fps")
        t0 = t1
        frame_count = 0

reconfigure_pixels(30, 2, .2)
print(f"len: {len(strands)}")
print(strands)
for s in strands:
    print("in here")
    print(s)
animations = [
    Pulse(strands[0], speed=0.2, color=(255,0,0), period=2),
    Pulse(strands[1], speed=0.02, color=(255,0,0), period=5),
]
animations = AnimationGroup(*animations)
while count < 10000:
    print('here')
    animations.animate()
    frame_count += 1
    count += 1
