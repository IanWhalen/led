from functools import wraps
import time
from typing import ClassVar, Mapping, Optional, Sequence

from rpi_ws281x import Adafruit_NeoPixel
from typing_extensions import Self
from viam.components.generic import Generic
from viam.logging import getLogger
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


LOG = logging.getLogger(__name__)


class LedModel(Generic):
    MODEL: ClassVar[Model] = Model(ModelFamily("weatherbox", "weatherbox"), "neopixel")

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
    blink: Animation = Blink(pixels, speed=speed, color=colors[0])
    colorcycle: Animation = ColorCycle(pixels, speed=speed, colors=colors)
    comet: Animation = Comet(pixels, speed=speed, color=colors[0], tail_length=tail_length, bounce=bounce)
    chase: Animation = Chase(pixels, speed=speed, size=size, spacing=spacing, color=colors[0])
    pulse: Animation = Pulse(pixels, speed=speed, period=period, color=colors[0])
    sparkle: Animation = Sparkle(pixels, speed=speed, color=colors[0], num_sparkles=num_sparkles)
    solid: Animation = Solid(pixels, color=colors[0])
    rainbow: Animation = Rainbow(pixels, speed=speed, period=period)
    sparkle_pulse: Animation = SparklePulse(pixels, speed=speed, period=period, color=colors[0])
    rainbow_comet: Animation = RainbowComet(pixels, speed=speed, tail_length=tail_length, bounce=bounce)
    rainbow_chase: Animation = RainbowChase(pixels, speed=speed, size=size, spacing=spacing, step=step)
    rainbow_sparkle: Animation = RainbowSparkle(pixels, speed=speed, num_sparkles=num_sparkles)
    custom_color_chase: Animation = CustomColorChase(pixels, speed=speed, size=size, spacing=spacing, colors=colors)

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
            
            animation = self.get_animation(self.annimation_name)
            animation.animate()

    async def do_command(
            self, command: Mapping[str, ValueTypes], *, timeout: Optional[float] = None,**kwargs,
    ) -> Mapping[str, ValueTypes]:
        result = {}
        for name, args in command.items():
            match name:
                # TODO should prob validate this
                case "animation":
                    self.annimation_name = args
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

    async def set_pixel_color(self, i, color):
        self.STRIP.setPixelColor(int(i), int(color))

    async def set_pixel_colors(self, pixel_colors):
        for pix_color in pixel_colors:
            self.STRIP.setPixelColor(int(pix_color[0]), int(pix_color[1]))

    async def show(self):
        self.STRIP.show()

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
        num_pixels: int = config.attributes.fields["num_pixels"].number_value
        pixel_order: str = config.attributes.fields["pixel_order"].string_value
        brightness: float = config.attributes.fields["brightness"].float_value
        pin: microcontroller.Pin = self.initialize_pin(pin_number)
        order: any = self.initialize_pixel_order(pixel_order)
        self.pixels = neopixel.NeoPixel(
            pin, num_pixels, brightness=brightness, pixel_order=order
        )

        self.regenerate_animations()

        self.start_thread()
    
    def __del__(self):
        LOG.info("Stopping module")
        self.stop_thread()
