from functools import wraps
import time
from typing import ClassVar, Mapping, Optional, Sequence

from rpi_ws281x import Adafruit_NeoPixel
from typing_extensions import Self
from viam.components.generic import Generic
from viam import logging
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes
import asyncio

from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model
# TODO: Convert to generic service
from viam import logging

from threading import Thread
from threading import Event

import microcontroller
import board
import neopixel

from adafruit_led_animation.color import AMBER, AQUA, BLACK, BLUE, GREEN, ORANGE, PINK, PURPLE, RED, WHITE, YELLOW, GOLD, JADE, MAGENTA, OLD_LACE, TEAL
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
from adafruit_led_animation.animation import Animation
import adafruit_led_animation



LOG = logging.getLogger(__name__)


class LedModel(Generic):
    MODEL: ClassVar[Model] = Model.from_string('vijayvuyyuru:animate:neopixel')

    pixels: neopixel.NeoPixel = None
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

    # Animation configuration
    animation_name: str = 'blink'
    blink: Animation = None
    colorcycle: Animation = None
    comet: Animation = None
    chase: Animation = None
    pulse: Animation = None
    sparkle: Animation = None
    solid: Animation = None
    rainbow: Animation = None
    sparkle_pulse: Animation = None
    rainbow_comet: Animation = None
    rainbow_chase: Animation =None
    rainbow_sparkle: Animation = None
    custom_color_chase: Animation = None

    # Animation thread settings
    thread = None
    event = None

    def thread_run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.animate())

    def start_thread(self):
        self.thread = Thread(target=self.thread_run())
        self.event = Event()
        self.thread.start()

    def stop_thread(self):
        if self.thread is not None and self.event is not None:
            self.event.set()
            self.thread.join()

    async def animate(self):
        while True:
            if self.event.is_set():
                return
            
            animation = self.get_animation(self.animation_name)
            animation.animate()

    async def do_command(
            self, command: Mapping[str, ValueTypes], *, timeout: Optional[float] = None,**kwargs,
    ) -> Mapping[str, ValueTypes]:
        result = {}
        for name, args in command.items():
            match name:
                # TODO should prob validate this
                case "animation":
                    self.animation_name = args
                case "speed":
                    self.speed = args
                case "colors":
                    new_colors = []
                    for color in args:
                        new_colors.append(self.get_color(color))
                    self.colors = new_colors
                case "tail_length":
                    self.tail_length = args
                case "bounce":
                    self.bounce = args
                case "size":
                    self.size = args
                case "spacing":
                    self.spacing = args
                case "period":
                    self.period = args
                case "num_sparkles":
                    self.num_sparkles = args
                case "step":
                    self.step = args
                case "set_pixel_colors":
                    await self.set_pixel_colors(args)
                    result[name] = True
                case "set_pixel_color":
                    await self.set_pixel_color(*args)
                    result[name] = True
                case "show":
                    await self.show()
                    result[name] = True

        self.regenerate_animations()
        return result
    
    def regenerate_animations(self):
        self.blink = Blink(self.pixels, speed=self.speed, color=self.colors[0])
        self.colorcycle = ColorCycle(self.pixels, speed=self.speed, colors=self.colors)
        self.comet = Comet(self.pixels, speed=self.speed, color=self.colors[0], tail_length=self.tail_length, bounce=self.bounce)
        self.chase = Chase(self.pixels, speed=self.speed, size=self.size, spacing=self.spacing, color=self.colors[0])
        self.pulse = Pulse(self.pixels, speed=self.speed, period=self.period, color=self.colors[0])
        self.sparkle = Sparkle(self.pixels, speed=self.speed, color=self.colors[0], num_sparkles=self.num_sparkles)
        self.solid = Solid(self.pixels, color=self.colors[0])
        self.rainbow = Rainbow(self.pixels, speed=self.speed, period=self.period)
        self.sparkle_pulse = SparklePulse(self.pixels, speed=self.speed, period=self.period, color=self.colors[0])
        self.rainbow_comet = RainbowComet(self.pixels, speed=self.speed, tail_length=self.tail_length, bounce=self.bounce)
        self.rainbow_chase = RainbowChase(self.pixels, speed=self.speed, size=self.size, spacing=self.spacing, step=self.step)
        self.rainbow_sparkle = RainbowSparkle(self.pixels, speed=self.speed, num_sparkles=self.num_sparkles)
        self.custom_color_chase = CustomColorChase(self.pixels, speed=self.speed, size=self.size, spacing=self.spacing, colors=self.colors)

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
        return animation_map.get(animation.lower(), self.blink) 

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
        return color_map.get(color.lower(), BLACK) 

    async def set_pixel_color(self, i, color):
        self.pixels.setPixelColor(int(i), int(color))

    async def set_pixel_colors(self, pixel_colors):
        for pix_color in pixel_colors:
            self.pixels.setPixelColor(int(pix_color[0]), int(pix_color[1]))

    async def show(self):
        self.pixels.show()

    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        cls.led_count = int(config.attributes.fields["led_count"].number_value)
        cls.led_pin = int(config.attributes.fields["led_pin"].number_value)
        led_module = cls(config.name)
        led_module.reconfigure(config, dependencies)
        return led_module

    @classmethod
    def validate_config(self, config: ComponentConfig) -> None:
        if "pin" not in config.attributes.fields:
            raise Exception("A pin_number attribute is required for nt-light-strip component. Must be a string in the format like 'D18' and must be connected to must be 'D10', 'D12', 'D18' or 'D21'")

        if "num_pixels" not in config.attributes.fields:
            raise Exception("A num_pixels attribute is required for nt-light-strip component. Must be an integer")
        
        if "brightness" not in config.attributes.fields:
            raise Exception("A brightness attribute is required for nt-light-strip component. Must be a float like 0.2 for 20% brightness")

        if "pixel_order" not in config.attributes.fields:
            raise Exception("A pixel_order attribute is required for nt-light-strip component. Must be a string of: 'GRB', 'GRBW', 'RGB', or 'RGBW'")

        return None
    
    def initialize_pin(self, pin_name):
        pin_object = getattr(board, pin_name, None)
        if pin_object is None:
            raise ValueError("Invalid pin_name: {}".format(pin_name))
        return pin_object
    
    def initialize_pixel_order(self, pixel_order):
        order = getattr(neopixel, pixel_order, None)
        if order is None:
            raise ValueError("Invalid pixel_order: {}".format(pixel_order))
        return order
    
    def reconfigure(self,
                    config: ComponentConfig,
                    dependencies: Mapping[ResourceName, ResourceBase]):
        self.stop_thread()

        pin_number: str = config.attributes.fields["pin"].string_value
        num_pixels: int = int(config.attributes.fields["num_pixels"].number_value)
        pixel_order: str = config.attributes.fields["pixel_order"].string_value
        brightness: float = config.attributes.fields["brightness"].number_value
        pin: microcontroller.Pin = self.initialize_pin(pin_number)
        order: any = self.initialize_pixel_order(pixel_order)
        self.pixels = neopixel.NeoPixel(
            pin, num_pixels, brightness=brightness, auto_write=False, pixel_order=order
        )

        self.regenerate_animations()

        self.start_thread()
    
    def __del__(self):
        LOG.info("Stopping module")
        self.stop_thread()
