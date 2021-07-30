import stactools.core

from stactools.nalcms import stac, assets, constants

stactools.core.use_fsspec()


def register_plugin(registry):
    from stactools.nalcms import commands

    registry.register_subcommand(commands.create_nalcms_command)



__all__ = ["constants", "stac", "assets"]
__version__ = "0.0.1"
