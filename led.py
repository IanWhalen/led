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

GREEN = 65280
BLUE = 255
CLEAR = 0

LOG = getLogger("led")


class Led(Generic):
    MODEL: ClassVar[Model] = Model(ModelFamily("ianwhalen", "demo"), "led_ring")

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
        for name, _ in command.items():
            if name == "test":
                await self.test_cycle()
                result["color"] = f"flashed: {name}"
        return result

    async def test_cycle(self):
        LOG.info("entering `test_cycle`")
        try:
            for color in [GREEN, BLUE, CLEAR]:
                self.color_wipe(color)
        except KeyboardInterrupt:
            self.color_wipe(CLEAR)

        LOG.info("End of program")

    def color_wipe(self, color):
        """Wipe color across display a pixel at a time."""
        LOG.info(f"entering `color_wipe` with color: {color}")
        for i in range(self.STRIP.numPixels()):
            self.STRIP.setPixelColor(i, color)
            self.STRIP.show()
            LOG.info(f"Showed {color}.")
            time.sleep(1)
        time.sleep(1)

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
