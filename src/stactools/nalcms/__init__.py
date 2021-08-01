from stactools.cli import Registry
import stactools.core

from stactools.nalcms import assets, commands, constants, stac

stactools.core.use_fsspec()


def register_plugin(registry: Registry) -> None:
    registry.register_subcommand(commands.create_nalcms_command)


__all__ = ["constants", "stac", "assets"]
__version__ = "0.0.1"
