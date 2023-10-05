"""
This file outlines the general structure for the API around a custom, modularized component.

It defines the abstract class definition that all concrete implementations must follow,
the gRPC service that will handle calls to the service,
and the gRPC client that will be able to make calls to this service.

In this example, the ``Neopixel`` abstract class defines what functionality is required for all Neopixel components.
It extends ``ComponentBase``, as all component types must.
It also defines its specific ``SUBTYPE``, which is used internally to keep track of supported types.

The ``NeopixelRPCService`` implements the gRPC service for the Neopixel component. This will allow other robots and clients to make
requests of the Neopixel component. It extends both from ``NeopixelServiceBase`` and ``RPCServiceBase``.
The former is the gRPC service as defined by the proto, and the latter is the class that all gRPC services must inherit from.

Finally, the ``NeopixelClient`` is the gRPC client for a Neopixel component. It inherits from NeopixelService since it implements
 all the same functions. The implementations are simply gRPC calls to some remote Neopixel component.

To see how this custom modular component is registered, see the __init__.py file.
To see the custom implementation of this component, see the neopixel.py file.
"""

import abc
from typing import Final, Sequence

from grpclib.client import Channel
from grpclib.server import Stream

from viam.resource.rpc_service_base import ResourceRPCServiceBase
from viam.resource.types import RESOURCE_TYPE_COMPONENT, Subtype
from viam.components.component_base import ComponentBase

from ..proto.neopixel_grpc import NeopixelServiceBase, NeopixelServiceStub

from ..proto.neopixel_pb2 import SetPixelColorRequest, SetPixelColorResponse, ShowRequest, ShowResponse


class Neopixel(ComponentBase):

    SUBTYPE: Final = Subtype("ianwhalen", RESOURCE_TYPE_COMPONENT, "neopixel")

    @abc.abstractmethod
    async def set_pixel_color(self, index: int, color: int) -> bool:
        ...

    @abc.abstractmethod
    async def show(self) -> bool:
        ...

class NeopixelRPCService(NeopixelServiceBase, ResourceRPCServiceBase):

    RESOURCE_TYPE = Neopixel

    async def set_pixel_color(self, stream: Stream[SetPixelColorRequest, SetPixelColorResponse]) -> None:
        request = await stream.recv_message()
        assert request is not None
        name = request.name
        neopixel = self.get_resource(name)
        resp = await neopixel.set_pixel_color(request.index, request.color)
        await stream.send_message(SetPixelColorResponse(success=resp))

    async def show(self, stream: Stream[ShowRequest, ShowResponse]) -> None:
        request = await stream.recv_message()
        assert request is not None
        name = request.name
        neopixel = self.get_resource(name)
        resp = await neopixel.show()
        await stream.send_message(ShowResponse(success=resp))

class NeopixelClient(Neopixel):

    def __init__(self, name: str, channel: Channel) -> None:
        self.channel = channel
        self.client = NeopixelServiceStub(channel)
        super().__init__(name)

    async def set_pixel_color(self, index: int, color: int) -> bool:
        request = SetPixelColorRequest(name=self.name, index=index, color=color)
        response: SetPixelColorResponse = await self.client.SetPixelColor(request)
        return response.success

    async def show(self) -> bool:
        request = ShowRequest(name=self.name)
        response: ShowResponse = await self.client.Show(request)
        return response.success
