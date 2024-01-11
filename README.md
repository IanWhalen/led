# README 

## CONFIG

To use this module in your smart machine, go to your machine configuration, click on the "Create component" button, search for neopixel, and add the generic neopixel component. Click "Add module" and give it a name. This will deploy the module to your machine. 

Alternatively, you can add it as a local module with the proper executable path.

Then add the sensor (either from the registry or as a local component) by clicking on the "Create component" button.

Example configuration for the Attributes section of the component looks like this:

{
  "led_count": 24,
  "led_pin": 12
}

led_count refers to the number of lights you have on the strip or the ring, so replace it according to the model you have. You will also have to update the "for pixel in range(your led count)" line in the code example to match this number. 

led_pin refers to which GPIO pin the lights are wired to, so replace it according to which pin you are using on the board. 

Save your config after adding the Attributes. 

## USAGE

```python
import asyncio
import time

from viam.components.generic import Generic
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions


async def connect():
    creds = Credentials(
        type="robot-location-secret", payload="PAYLOAD")
    opts = RobotClient.Options(
        refresh_interval=0, dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address("ROBOT_ADDRESS", opts)


async def main():
    robot = await connect()
    
    #replace "thing" with the actual name of the generic component in the machine config 
    led = Generic.from_robot(robot, "thing")
    for color in [65280, 0]:
        #replace with the actual number of lights on the ring or strip
        for pixel in range(7):
            await led.do_command({"set_pixel_color": [pixel, color]})
            await led.do_command({"show": []})
            time.sleep(1)

    await robot.close()


if __name__ == "__main__":
    asyncio.run(main())
```

## CONTRIBUTING

Requires a library that doesn't build on a Mac, so you need to develop on Linux.

## NOTES

Remember to disable sound when running on a Raspberry Pi.

