import asyncio
import sys

sys.path.append(".")

from led import Led
from viam.module.module import Module
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.components.generic import Generic


async def main():
    """This function creates and starts a new module, after adding all desired resource models.
    Resource creators must be registered to the resource registry before the module adds the resource model.
    """
    registration = ResourceCreatorRegistration(Led.new, Led.validate_config)
    Registry.register_resource_creator(Generic.SUBTYPE, Led.MODEL, registration)

    module = Module.from_args()
    module.add_model_from_registry(Generic.SUBTYPE, Led.MODEL)
    await module.start()


if __name__ == "__main__":
    asyncio.run(main())
