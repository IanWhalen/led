from functools import wraps
import time
from typing import ClassVar, Mapping, Optional

from rpi_ws281x import Adafruit_NeoPixel
from typing_extensions import Self
from viam.components.generic import Generic
from viam.logging import getLogger
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes

LOG = getLogger("led")


class Led(Generic):
    MODEL: ClassVar[Model] = Model(ModelFamily("weatherbox", "weatherbox"), "neopixel")

    def __init__(self, name: str) -> None:
        self.STRIP = Adafruit_NeoPixel(self.led_count, self.led_pin)
        self.STRIP.begin()

        super().__init__(name)

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Mapping[str, ValueTypes]:
        result = {}
        for name, args in command.items():
            if name == "set_pixel_color":
                await self.set_pixel_color(*args)
                result[name] = True
            if name == "show":
                await self.show()
                result[name] = True
        return result

    async def set_pixel_color(self, i, color):
        self.STRIP.setPixelColor(int(i), int(color))

    async def show(self):
        self.STRIP.show()

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        cls.led_count = int(config.attributes.fields["led_count"].number_value)
        cls.led_pin = int(config.attributes.fields["led_pin"].number_value)
        return cls(config.name)

    @classmethod
    def validate_config(self, config: ComponentConfig) -> None:
        return None
    
    def __del__(self):
        print("deleting self")
        self.stop_thread()
