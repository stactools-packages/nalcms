import click
import logging

from stactools.nalcms import stac

logger = logging.getLogger(__name__)


def create_nalcms_command(cli: click.Group) -> click.Command:
    """Creates the nalcms command line utility."""
    @cli.group(
        "nalcms",
        short_help=
        "Commands for working with North American Land Change Monitoring System data",
    )
    def nalcms() -> None:
        pass

    @nalcms.command(
        "create-collection",
        short_help="Creates a STAC collection.",
    )
    @click.argument("destination")
    def create_collection_command(destination: str) -> None:
        """Creates a STAC Collection
        Args:
            destination (str): An HREF for the Collection JSON
        """
        collection = stac.create_collection()

        collection.set_self_href(destination)

        collection.save_object()

    return nalcms
