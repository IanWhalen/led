import time
from typing import ClassVar, Mapping
from typing_extensions import Self

import logging

from viam.components.generic import Generic
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes

from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase

from rpi_ws281x import Adafruit_NeoPixel, Color

from typing import Optional
from typing_extensions import Self

# LED strip configuration:
LED_COUNT = 7  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53

ORDER = "RGB"

STRIP = Adafruit_NeoPixel(
    LED_COUNT,
    LED_PIN,
    LED_FREQ_HZ,
    LED_DMA,
    LED_INVERT,
    LED_BRIGHTNESS,
    LED_CHANNEL,
)
STRIP.begin()

LOG = logging.getLogger()

class Led(Generic):
    MODEL: ClassVar[Model] = Model(ModelFamily("ianwhalen", "demo"), "led_ring")

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        LOG.info("entering `do_command`")
        result = {}
        for name, _ in command.items():
            if name == "test":
                await self.test_cycle()
                result["color"] = "flashed: " + name
        return result

    async def test_cycle(self):
        try:
            print("\nGreen wipe")
            self.color_wipe(Color(0, 255, 0))
            time.sleep(1)

            print("\nBlue wipe")
            self.color_wipe(Color(0, 0, 255))
            time.sleep(1)

            self.color_wipe(Color(0, 0, 0))
            print("\nEnd of program")
        except KeyboardInterrupt:
            self.color_wipe(Color(0, 0, 0))
            print("\nEnd of program")

    def color_wipe(self, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        color = self.LED_TYPR(ORDER, color)
        for i in range(STRIP.numPixels()):
            STRIP.setPixelColor(i, color)
            STRIP.show()
            time.sleep(wait_ms / 1000.0)

    def LED_TYPR(self, order, R_G_B):
        B = R_G_B & 255
        G = R_G_B >> 8 & 255
        R = R_G_B >> 16 & 255
        Led_type = ["GRB", "GBR", "RGB", "RBG", "BRG", "BGR"]
        color = [
            Color(G, R, B),
            Color(G, B, R),
            Color(R, G, B),
            Color(R, B, G),
            Color(B, R, G),
            Color(B, G, R),
        ]
        if order in Led_type:
            return color[Led_type.index(order)]

    @classmethod
    def new(
        cls,
        config: ComponentConfig,
        dependencies: Mapping[ResourceName, ResourceBase],
    ) -> Self:
        return cls(config.name)

    @classmethod
    def validate_config(self, config: ComponentConfig) -> None:
        # Custom validation can be done by specifiying a validate function like this one. Validate functions
        # can raise errors that will be returned to the parent through gRPC. Validate functions can
        # also return a sequence of strings representing the implicit dependencies of the resource.
        return None
