# README 

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

    led = Generic.from_robot(robot, "thing")
    for color in [65280, 0]:
        for pixel in range(7):
            await led.do_command({"set_pixel_color": [pixel, color]})
            await led.do_command({"show": []})
            time.sleep(1)

    await robot.close()


if __name__ == "__main__":
    asyncio.run(main())
```

## CONTRIBUTING

Requires a library that doesn't build on a mac, so need to develop on linux.

## NOTES

Remember to disable sound when running on a rasbperry pi.

