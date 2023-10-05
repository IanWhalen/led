from typing import ClassVar, Mapping
from typing_extensions import Self

from rpi_ws281x import Adafruit_NeoPixel
from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily

from .api import Neopixel

class neopixel(Neopixel, Reconfigurable):
    

    MODEL: ClassVar[Model] = Model(ModelFamily("ianwhalen", "display"), "neopixel")

    def __init__(self, name: str) -> None:
        self.strip = Adafruit_NeoPixel(self.led_count, self.led_pin)
        self.strip.begin()

        super().__init__(name)

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        cls.led_count = int(config.attributes.fields["led_count"].number_value)
        cls.led_pin = int(config.attributes.fields["led_pin"].number_value)
        return cls(config.name)

    async def set_pixel_color(self, i, color):
        self.strip.setPixelColor(int(i), int(color))

    async def show(self):
        self.strip.show()
