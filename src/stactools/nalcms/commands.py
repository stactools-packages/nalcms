import os
from typing import Any, Union
import click  # type: ignore
import logging

from stactools.nalcms import stac
from stactools.nalcms.constants import GSDS, REGIONS, YEARS

logger = logging.getLogger(__name__)


def create_nalcms_command(cli: Any) -> Any:
    """Creates the joint research centre - global surface water command line
     utility."""
    @cli.group(
        "nalcms",
        short_help=("Commands for working with NALCMS data."),
    )
    def nalcms() -> None:
        pass

    @nalcms.command(
        "create-collection",
        short_help="Creates STAC collections for NALCMS data.",
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC Collection json.",
    )
    def create_collection_command(destination: str) -> Any:
        """Creates a STAC Collection for each mapped dataset from the North
        American Land Classification Monitoring System.
        Args:
            destination (str): Directory used to store the STAC collections.
        Returns:
            Callable
        """
        root_col = stac.create_nalcms_collection()

        for reg in REGIONS.keys():
            region = stac.create_region_collection(reg)
            root_col.add_child(region)

            for gsd in GSDS:
                for year in YEARS[gsd]:
                    item = stac.create_item(reg, gsd, year, "")
                    if item:
                        region.add_item(item)

        root_col.normalize_hrefs(destination)
        root_col.save()
        root_col.validate()

    @nalcms.command(
        "create-item",
        short_help="Create a STAC item for a given region, GSD and year.",
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC json.",
    )
    @click.option(
        "-s",
        "--source",
        required=False,
        help="The input COG to create the item from.",
        default=None,
    )
    @click.option("-r",
                  "--region",
                  required=False,
                  help="The region covered by the STAC Item.",
                  type=click.Choice(REGIONS.keys(), case_sensitive=False),
                  default="NA")
    @click.option("-g", "--gsd", required=False, type=click.Choice(GSDS), default=30)
    @click.option("-y",
                  "--year",
                  required=False,
                  help="The year or range of years covered by the STAC Item.",
                  type=click.Choice(list(set(sum(YEARS.values(), [])))),
                  default="2010-2015")
    def create_item_command(destination: str, source: str, region: str, gsd: Union[int, float],
                            year: str) -> Any:
        """Creates a STAC Item
        Args:
            destination (str): The output directory for the STAC json.
            source (str): The input COG to create the item from.
            region (str): The region covered by the STAC Item.
            gsd (int, float): The ground sampling distance of the STAC Item.
            year (str): The year or range of years covered by the STAC Item.
        """
        item = stac.create_item(region, gsd, year, source)
        if item:
            item_path = os.path.join(destination, f"{item.id}.json")
            item.set_self_href(item_path)
            item.save_object()
        else:
            print(f"{gsd}m_{year}_{region} not found in NALCMS")

    return nalcms
