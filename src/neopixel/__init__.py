"""
This file registers the model with the Python SDK
"""

from viam.resource.registry import Registry, ResourceCreatorRegistration, ResourceRegistration

from .api import NeopixelClient, NeopixelRPCService, Neopixel
from .neopixel import neopixel

Registry.register_subtype(ResourceRegistration(Neopixel, NeopixelRPCService, lambda name, channel: NeopixelClient(name, channel)))

Registry.register_resource_creator(Neopixel.SUBTYPE, neopixel.MODEL, ResourceCreatorRegistration(neopixel.new))
