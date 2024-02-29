import asyncio
import sys
from viam import logging

sys.path.append("..")

LOGGER = logging.getLogger(__name__)

from models import LedModel
from viam.module.module import Module
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.components.generic import Generic


async def main():
    """This function creates and starts a new module, after adding all desired resource models.
    Resource creators must be registered to the resource registry before the module adds the resource model.
    """
    LOGGER.info("Starting neopixel module")

    registration = ResourceCreatorRegistration(LedModel.new, LedModel.validate_config)
    Registry.register_resource_creator(Generic.SUBTYPE, LedModel.MODEL, registration)

    module = Module.from_args()
    module.add_model_from_registry(Generic.SUBTYPE, LedModel.MODEL)
    await module.start()

if __name__ == "__main__":
    asyncio.run(main())
