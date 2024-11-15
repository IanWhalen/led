import board
import rainbowio
import adafruit_ticks
from adafruit_led_animation.color import (
    AMBER,
    AQUA,
    BLACK,
    BLUE,
    GREEN,
    ORANGE,
    PINK,
    PURPLE,
    RED,
    WHITE,
    YELLOW,
    GOLD,
    JADE,
    MAGENTA,
    OLD_LACE,
    TEAL,
)
from adafruit_led_animation.group import AnimationGroup
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.colorcycle import ColorCycle
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.sparklepulse import SparklePulse
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.animation.customcolorchase import CustomColorChase
import time


from adafruit_led_animation.helper import PixelMap
from adafruit_neopxl8 import NeoPxl8

# # Customize for your strands here
# num_strands = 3
# strand_length = 120
first_led_pin = board.NEOPIXEL0

# num_pixels = num_strands * strand_length

# # Make the object to control the pixels
# pixels = NeoPxl8(
#     first_led_pin,
#     num_pixels,
#     num_strands=num_strands,
#     auto_write=False,
#     brightness=0.25,
# )

class PixelDisplay:
    num_strands = 0
    strand_length = 0
    first_led_pin = board.NEOPIXEL0
    brightness = 0.0

    pixels = None
    strand_list = []
    
    animations:AnimationGroup = None

    def __init__(self, num_strands, strand_length, brightness) -> None:
        self.reconfigure(num_strands, strand_length, brightness)
        
    def reconfigure(self, num_strands, strand_length, brightness) ->None:
        if num_strands != 0:
            self.num_strands = num_strands
        if strand_length != 0:
            self.strand_length = strand_length
        if brightness != 0.0:
            self.brightness = brightness
            
        if self.pixels is not None:
            self.pixels.deinit()
        self.pixels = NeoPxl8(
            first_led_pin,
            self.strand_length * self.num_strands,
            num_strands=self.num_strands,
            auto_write=False,
            brightness=self.brightness,
        )
        print("set pixels")
        self.strand_list = [PixelStrand(self.strand(i, self.strand_length)) for i in range(self.num_strands)]
        print("set strand list")
        print(self.strand_list)
        print(f"reconfigured with {self.num_strands} strands, {self.strand_length} pixels per strand, and brigthness of {self.brightness}")
        
    def animate(self):
        print("in animate")
        if self.animations == None:
            # raw_anim = 
            self.animations = AnimationGroup(*[pxs.get_active_animation() for pxs in self.strand_list])
        self.animations.animate()
    
    def set_animation(self, strand_index:int, params:dict):
        if strand_index >= len(self.strand_list):
            raise ValueError("index out of bound for configured number of leds")
        self.strand_list[strand_index].set_animation(params)
        # regnerate animation group if one changed
        self.animations = AnimationGroup(*[pxs.get_active_animation() for pxs in self.strand_list])

        
    def strand(self, n, pixels_count):
        return PixelMap(
            self.pixels,
            range(n * pixels_count, (n + 1) * pixels_count),
            individual_pixels=True,
        )


class PixelStrand:
    # Animation settings
    speed: float = 0.1
    colors = [RED]
    tail_length: int = 1
    bounce: bool = False
    size: int = 1
    spacing: int = 1
    period: int = 1
    num_sparkles: int = 1
    step: int = 1
    active_animation: str = ""


    def __init__(self, strand) -> None:
        self.strand = strand
        self.active_animation = ""
        self.regenerate_animations()


    def set_animation(self, params: dict) -> None:
        for name, args in params.items():
            if name == "animation":
                self.active_animation = args
            elif name == "speed":
                self.speed = float(args)
            elif name == "color":
                color = self.get_color(args)
                self.colors = [color]
            elif name == "colors":
                new_colors = []
                for color in args:
                    new_colors.append(self.get_color(color))
                self.colors = new_colors
            elif name == "tail_length":
                self.tail_length = int(args)
            elif name == "bounce":
                self.bounce = int(args)
            elif name == "size":
                self.size = int(args)
            elif name == "spacing":
                self.spacing = int(args)
            elif name == "period":
                self.period = int(args)
            elif name == "speed":
                self.speed = int(args)
            elif name == "num_sparkles":
                self.num_sparkles = int(args)
            elif name == "step":
                self.step = int(args)
            else:
                raise ValueError("invalid arg")
        self.regenerate_animations()

    def get_color(self, color: str) -> adafruit_led_animation.color:
        color_map = {
            "amber": AMBER,
            "aqua": AQUA,
            "black": BLACK,
            "blue": BLUE,
            "green": GREEN,
            "orange": ORANGE,
            "pink": PINK,
            "purple": PURPLE,
            "red": RED,
            "white": WHITE,
            "yellow": YELLOW,
            "gold": GOLD,
            "jade": JADE,
            "magenta": MAGENTA,
            "old_lace": OLD_LACE,
            "teal": TEAL,
        }
        strip_color = color_map.get(color.lower())
        if not strip_color:
            raise ValueError(f"invalid color name {color}")
        return strip_color

    def regenerate_animations(self):
        self.blink = Blink(self.strand, speed=self.speed, color=self.colors[0])
        self.colorcycle = ColorCycle(self.strand, speed=self.speed, colors=self.colors)
        self.comet = Comet(
            self.strand,
            speed=self.speed,
            color=self.colors[0],
            tail_length=self.tail_length,
            bounce=self.bounce,
        )
        self.chase = Chase(
            self.strand,
            speed=self.speed,
            size=self.size,
            spacing=self.spacing,
            color=self.colors[0],
        )
        self.pulse = Pulse(
            self.strand, speed=self.speed, period=self.period, color=self.colors[0]
        )
        self.sparkle = Sparkle(
            self.strand,
            speed=self.speed,
            color=self.colors[0],
            num_sparkles=self.num_sparkles,
        )
        self.solid = Solid(self.strand, color=self.colors[0])
        self.rainbow = Rainbow(self.strand, speed=self.speed, period=self.period)
        self.sparkle_pulse = SparklePulse(
            self.strand, speed=self.speed, period=self.period, color=self.colors[0]
        )
        self.rainbow_comet = RainbowComet(
            self.strand,
            speed=self.speed,
            tail_length=self.tail_length,
            bounce=self.bounce,
        )
        self.rainbow_chase = RainbowChase(
            self.strand,
            speed=self.speed,
            size=self.size,
            spacing=self.spacing,
            step=self.step,
        )
        self.rainbow_sparkle = RainbowSparkle(
            self.strand, speed=self.speed, num_sparkles=self.num_sparkles
        )
        self.custom_color_chase = CustomColorChase(
            self.strand,
            speed=self.speed,
            size=self.size,
            spacing=self.spacing,
            colors=self.colors,
        )

    def get_animation(self, animation: str) -> Animation:
        # TODO try to take this out
        animation_map = {
            "blink": self.blink,
            "colorcycle": self.colorcycle,
            "comet": self.comet,
            "chase": self.chase,
            "pulse": self.pulse,
            "sparkle": self.sparkle,
            "solid": self.solid,
            "rainbow": self.rainbow,
            "sparkle_pulse": self.sparkle_pulse,
            "rainbow_comet": self.rainbow_comet,
            "rainbow_chase": self.rainbow_chase,
            "rainbow_sparkle": self.rainbow_sparkle,
            "custom_color_chase": self.custom_color_chase,
        }
        animationl = animation_map.get(animation.lower())
        if not animationl:
            raise ValueError("invalid animation name")
        return animationl

    def get_active_animation(self) -> Animation:
        return self.get_animation(self.active_animation)


# Create the 8 virtual strands
# strands = [strand(i, strand_length) for i in range(num_strands)]


# def reconfigure_pixels(pixels_count, num_strands, brightness):
#     global pixels
#     pixels.fill(0)
#     pixels.show()
#     time.sleep(0.1)
#     pixels.deinit()
#     new_pixels = NeoPxl8(
#         board.NEOPIXEL0,
#         num_strands * pixels_count,
#         num_strands=num_strands,
#         auto_write=False,
#         brightness=brightness,
#     )
#     pixels = new_pixels
#     print("regenerated pixels")
#     global strands
#     strands = [strand(i, pixels_count) for i in range(num_strands)]
#     print("regenerated strands")


# For each strand, create a comet animation of a different color
# animations = [
#     Comet(strand, 0.02, (255,255,255), ring=True)
#     for i, strand in enumerate(strands)
# ]

# working commands:     Pulse(strands[2], speed=0.2, color=(255,0,80), period=2),

# Pulse(strands[1], speed=0.2, color=(255,0,80), period=2),
# Pulse(strands[2], speed=0.2, color=(255,0,80), period=2),
# Blink(strand[1], 0.02, (255,125,128)),
# Sparkle(strand[3], 0.02, 2, (0,232,232))

# Solid(strands[0], color=TEAL),
# CustomColorChase(strands[0], speed=0.02, size=30, spacing=0, colors=[(50,255,5), (255,0,120), (255,0,5)])
# while True:
#     reconfigure_pixels(120, 3, 0.4)
#     animations = [
#         Pulse(strands[0], speed=0.2, color=(255, 0, 80), period=2),
#         Pulse(strands[1], speed=0.02, color=(255, 0, 80), period=5),
#         Pulse(strands[2], speed=0.02, color=(255, 0, 80), period=5),
#     ]

#     # Advance the animations by varying amounts so that they become staggered
#     # for i, animation in enumerate(animations):
#     #     animation._tail_start = 30 * 5 * i // 8  # pylint: disable=protected-access

#     # Group them so we can run them all at once
#     animations = AnimationGroup(*animations)

#     # Run the animations and report on the speed in frame per secodn
#     t0 = adafruit_ticks.ticks_ms()
#     frame_count = 0
#     count = 0

#     while count < 10000:
#         animations.animate()
#         frame_count += 1
#         count += 1
#         t1 = adafruit_ticks.ticks_ms()
#         dt = adafruit_ticks.ticks_diff(t1, t0)
#         if dt > 1000:
#             print(f"{frame_count * 1000/dt:.1f}fps")
#             t0 = t1
#             frame_count = 0

#     reconfigure_pixels(30, 2, 0.2)
#     # animations = [
#     #     Pulse(strands[0], speed=0.2, color=(255,0,0), period=2),
#     #     Pulse(strands[1], speed=0.02, color=(255,0,0), period=5),
#     # ]
#     # animations = AnimationGroup(*animations)
#     myPixelStrands = []
#     for strand in strands:
#         myPixelStrands.append(PixelStrand(strand))
#     myPixelStrands[0].set_animation({"speed": 0.2, "period": 2})
#     myPixelStrands[0].set_animation({"animation": "rainbow"})
#     myPixelStrands[1].set_animation({"speed": 0.6, "size": 10, "spacing": 2, "step": 1})
#     myPixelStrands[1].set_animation({"animation": "rainbow_chase"})
#     animations_temp = [pxs.get_active_animation() for pxs in myPixelStrands]
#     animations = AnimationGroup(*animations_temp)
#     while count < 200000:
#         animations.animate()
#         frame_count += 1
#         count += 1

# display = PixelDisplay(num_strands=3, strand_length=120, brightness=.1)
# display.set_animation(0, {"speed": 1.0, "period": 2})
# display.set_animation(0,{"animation": "rainbow"})
# display.set_animation(1, {"speed": 2.5, "period": 2})
# display.set_animation(1,{"animation": "blink"})
# display.set_animation(2, {"speed": 5.0, "period": 2})
# display.set_animation(2,{"animation": "rainbow"})
count = 0

strand_length = 120
num_strands = 3

pixels = NeoPxl8(
    first_led_pin,
    strand_length * num_strands,
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
    
strands = [strand(i, strand_length) for i in range(num_strands)]

myPixelStrands = []
for strand in strands:
    myPixelStrands.append(PixelStrand(strand))
    
myPixelStrands[0].set_animation({"speed": 0.2, "period": 2})
myPixelStrands[0].set_animation({"animation": "rainbow"})
myPixelStrands[1].set_animation({"speed": 0.6, "size": 10, "spacing": 2, "step": 1})
myPixelStrands[1].set_animation({"animation": "rainbow_chase"})
myPixelStrands[2].set_animation({"animation": "blink"})

    
animations_temp = [pxs.get_active_animation() for pxs in myPixelStrands]
animations = AnimationGroup(*animations_temp)

while count < 10:
    animations.animate()
    count+=1
