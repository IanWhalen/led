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
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.sparklepulse import SparklePulse
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.animation.customcolorchase import CustomColorChase
import time

import busio


from adafruit_led_animation.helper import PixelMap
from adafruit_neopxl8 import NeoPxl8

uart = busio.UART(board.TX, board.RX, baudrate=9600)

# Customize for your strands here
num_strands = 3
strand_length = 120
first_led_pin = board.NEOPIXEL0        

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
    def __init__(self, strand) -> None:
        self.strand = strand
        self.active_animation = "blink"
        self.regenerate_animations()
        
    def set_animation(self, params:dict) -> None:
        for (name, args) in params.items():
            if name == "animation":
                self.active_animation = args
                self.strand.fill((0,0,0))
                self.strand.show()
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
            elif  name == "set_pixel_colors":
                # clear active animation if we're explicitly setting pixel colors and zero all pixels if switching from animation to manual mode
                if self.active_animation != "":
                    self.strand.fill((0,0,0))
                    self.strand.show()
                self.active_animation = ""
                self.set_pixel_colors(args)
            else:
                raise ValueError(f"invalid arg: {name}")
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
            "teal": TEAL
        }
        strip_color = color_map.get(color.lower())
        if not strip_color:
            raise ValueError(f"invalid color name {color}")
        return strip_color
    
    def set_pixel_colors(self, pixel_colors:dict):
        for pixel, color in pixel_colors.items():
            # convert from floats to ints
            self.strand[int(pixel)] = [int(y) for y in color]
        self.strand.show()   
    
    def regenerate_animations(self):
        self.blink = Blink(self.strand, speed=self.speed, color=self.colors[0])
        self.colorcycle = ColorCycle(self.strand, speed=self.speed, colors=self.colors)
        self.comet = Comet(self.strand, speed=self.speed, color=self.colors[0], tail_length=self.tail_length, bounce=self.bounce)
        self.chase = Chase(self.strand, speed=self.speed, size=self.size, spacing=self.spacing, color=self.colors[0])
        self.pulse = Pulse(self.strand, speed=self.speed, period=self.period, color=self.colors[0])
        self.sparkle = Sparkle(self.strand, speed=self.speed, color=self.colors[0], num_sparkles=self.num_sparkles)
        self.solid = Solid(self.strand, color=self.colors[0])
        self.rainbow = Rainbow(self.strand, speed=self.speed, period=self.period)
        self.sparkle_pulse = SparklePulse(self.strand, speed=self.speed, period=self.period, color=self.colors[0])
        self.rainbow_comet = RainbowComet(self.strand, speed=self.speed, tail_length=self.tail_length, bounce=self.bounce)
        self.rainbow_chase = RainbowChase(self.strand, speed=self.speed, size=self.size, spacing=self.spacing, step=self.step)
        self.rainbow_sparkle = RainbowSparkle(self.strand, speed=self.speed, num_sparkles=self.num_sparkles)
        self.custom_color_chase = CustomColorChase(self.strand, speed=self.speed, size=self.size, spacing=self.spacing, colors=self.colors)

    def get_animation(self, animation: str) -> Animation:
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
            "custom_color_chase": self.custom_color_chase
        }
        animationl = animation_map.get(animation.lower())
        if not animationl:
            raise ValueError("invalid animation name")
        return animationl 

    def get_active_animation(self) -> Animation:
        if self.active_animation != "":
            return self.get_animation(self.active_animation)

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
        strands = [self.strand(i, self.strand_length) for i in range(self.num_strands)]
        strands_list = []
        for strand in strands:
            strands_list.append(PixelStrand(strand))
        self.strand_list = strands_list
        print("set strand list")
        print(self.strand_list)
        print(f"reconfigured with {self.num_strands} strands, {self.strand_length} pixels per strand, and brigthness of {self.brightness}")
        
    def animate(self):
        if self.animations == None:
            self.regenerate_animation_group()
        self.animations.animate()
    
    def set_animation(self, strand_index:int, params:dict):
        if strand_index >= len(self.strand_list):
            raise ValueError("index out of bound for configured number of leds")
        self.strand_list[strand_index].set_animation(params)
        self.regenerate_animation_group()

        
    def regenerate_animation_group(self):
        raw_anim = []
        for pxs in self.strand_list:
            a = pxs.get_active_animation()
            # active animation can be none if we manually set pixel colors
            if a is not None:
                raw_anim.append(a)
        self.animations = AnimationGroup(*raw_anim)

        
    def strand(self, n, pixels_count):
        return PixelMap(
            self.pixels,
            range(n * pixels_count, (n + 1) * pixels_count),
            individual_pixels=True,
        )

count = 0
myPixelStrands = []
pixel_display = PixelDisplay(num_strands=num_strands, strand_length=strand_length, brightness=.50)
pixel_display.set_animation(0, {"speed": .02, "period": 2})
pixel_display.set_animation(0, {"animation": "rainbow"})
pixel_display.set_animation(1, {"speed": .1, "size": 10, "spacing": 2, "step": 1 })
pixel_display.set_animation(1, {"animation": "rainbow_chase"})
pixel_display.set_animation(2, {"speed": .2, "tail_length": 30, "animation": "rainbow_comet"})



while True:
    print("shuold be blinking")
    pixel_display.set_animation(2, {"speed": .02, "tail_length": 30, "animation": "rainbow_comet"})
    count = 0

    while count < 5000:
        pixel_display.animate()
        count += 1
    pixel_display.set_animation(2, {"speed": .1, "animation": "blink"})

    print("changing animation")
    count = 0
    while count < 5000:
        pixel_display.animate() 
        count +=1

    print("changing animation 2") 
    pixel_display.set_animation(2, {"speed": .1, "animation": "comet"})

    count = 0
    while count < 5000:
        pixel_display.animate() 
        count +=1
    
    print("changing animation 2, should just be solid pixels now") 
    pixel_display.set_animation(2, {"set_pixel_colors": {1: [0, 255, 0], 2: [0, 255, 0], 3: [0, 255, 0]}})
    count = 0
    while count < 5000:
        pixel_display.animate() 
        count +=1
        
