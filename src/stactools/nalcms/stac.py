from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
# import json
import logging
from stactools.nalcms.constants import (
    EXTENTS, ID, KEYWORDS, LICENSE_LINK, PROJECTIONS, SATELLITES, TITLE,
    DESCRIPTION, PROVIDER, LICENSE, GSDS, YEARS, REGIONS, HREF_DIR, HREFS_ZIP,
    HREFS_METADATA, nalcms_catalog, nalcms_license, gsd30m_collection,
    gsd250m_collection)
import re
import shapely.geometry
import pystac
from datetime import datetime
import fiona
from pyproj import crs, Transformer
from pystac import (Catalog, Collection, StacIO, Asset, Item, MediaType,
                    SpatialExtent, Link, Summaries)
from pystac.extensions.projection import (SummariesProjectionExtension,
                                          ProjectionExtension)
from shapely.geometry import box
from shapely.ops import transform as shapely_transform
from stactools.nrcan_spot_ortho.geobase_ftp import GeobaseSpotFTP
from stactools.nrcan_spot_ortho.utils import (bbox, transform_geom,
                                              CustomStacIO)
from stactools.nrcan_spot_ortho.stac_templates import (spot_sensor, proj_epsg)
import os

StacIO.set_default(CustomStacIO)
null = None

logger = logging.getLogger(__name__)


def create_item(cog_href: str) -> pystac.Item:
    """Creates a STAC item for a North American Land Change Monitoring System dataset.

    Args:
        cog_href (str, optional): Path to COG asset.

    Returns:
        pystac.Item: STAC Item object.
    """

    item_id = cog_href.split(".")[0].split("/")[-1]
    title = re.search("(?<=30m_).*", cog_href).group().replace("_",
                                                               " ").title()
    description = ""

    utc = pytz.utc

    year = 2010
    dataset_datetime = utc.localize(datetime.strptime(year, "%Y"))

    end_datetime = dataset_datetime + relativedelta(years=5)

    start_datetime = dataset_datetime
    end_datetime = end_datetime

    bbox = [-170, 14, -50, 84]  # from metadata file

    polygon = shapely.geometry.box(*bbox, ccw=True)
    coordinates = [list(i) for i in list(polygon.exterior.coords)]

    geometry = {"type": "Polygon", "coordinates": [coordinates]}

    properties = {
        "title": title,
        "description": description,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
    }

    # Create item
    item = pystac.Item(
        id=item_id,
        geometry=geometry,
        bbox=bbox,
        datetime=dataset_datetime,
        properties=properties,
        stac_extensions=[],
    )

    # item.ext.enable("projection")
    # item.ext.projection.epsg = EPSG

    item.add_asset(
        "cog",
        pystac.Asset(
            href=cog_href,
            media_type=pystac.MediaType.COG,
            roles=["data"],
            title=title,
        ),
    )

    return item


def create_collection(metadata: dict):
    # Creates a STAC collection for a Natural Resources Canada Land Cover dataset

    # title = metadata.get("tiff_metadata").get("dct:title")

    utc = pytz.utc
    year = 2010
    dataset_datetime = utc.localize(datetime.strptime(year, "%Y"))

    end_datetime = dataset_datetime + relativedelta(years=5)

    start_datetime = dataset_datetime
    end_datetime = end_datetime

    bbox = [-170, 14, -50, 84]  # from metadata file

    # polygon = shapely.geometry.box(*bbox, ccw=True)
    # coordinates = [list(i) for i in list(polygon.exterior.coords)]

    # geometry = {"type": "Polygon", "coordinates": [coordinates]}

    collection = pystac.Collection(
        id=ID,
        title=TITLE,
        description=DESCRIPTION,
        providers=[PROVIDER],
        license=LICENSE,
        extent=pystac.Extent(
            pystac.SpatialExtent(bbox),
            pystac.TemporalExtent([start_datetime, end_datetime])),
        catalog_type=pystac.CatalogType.RELATIVE_PUBLISHED,
    )

    # Don't have a license link yet
    # collection.add_link(LICENSE_LINK)

    return collection


def create_item(reg, gsd, year):
    """
    TODO
    """
    bbox = EXTENTS[reg]
    polygon = shapely.geometry.box(*bbox, ccw=True)
    coordinates = [list(i) for i in list(polygon.exterior.coords)]
    geometry = {"type": "Polygon", "coordinates": [coordinates]}

    years = year.split("-")
    diff = "change " if "-" in year else ""
    properties = {
        "title": f"{reg} land cover {diff}({year}, {gsd} m)",
        "description":
        f"Land cover {diff}for {year} over {REGIONS[reg]} ({gsd} m)",
        "start_datetime": datetime.strptime(years[0], "%Y"),
        "end_datetime": datetime.strptime(years[-1], "%Y"),
        "gsd": gsd,
    }

    # Create item
    item = pystac.Item(
        id=f"{reg}_{year}_{gsd}m",
        geometry=geometry,
        bbox=bbox,
        datetime=datetime.strptime(years[0], "%Y"),
        properties=properties,
        stac_extensions=[
            "https://stac-extensions.github.io/projection/v1.0.0/schema.json"
        ])

    # Create metadata asset
    metadata_href = os.path.join(HREF_DIR, HREFS_METADATA[f"{gsd}m_{year}"])
    item.add_asset(
        "metadata",
        pystac.Asset(
            href=metadata_href,
            media_type=MediaType.JSON,
            roles=["metadata"],
            title="Metadata for land cover {diff}for {year} ({gsd} m)",
        ))

    # Create source data asset
    data_href = os.path.join(HREF_DIR, HREFS_ZIP[f"{gsd}m_{year}_{reg}"])
    item.add_asset(
        "data",
        pystac.Asset(
            href=data_href,
            media_type="application/zip",
            roles=["data"],
            title=
            "Data for land cover {diff}over {REGIONS[reg]} for {year} ({gsd} m)"
        ))

    # Include projection information
    proj_key = f"{gsd}m_{year}_{reg}"
    proj_ext = ProjectionExtension.ext(item)
    proj_ext.epsg = PROJECTIONS[proj_key]["epsg"]
    proj_ext.transform = PROJECTIONS[proj_key]["transform"]
    proj_ext.bbox = PROJECTIONS[proj_key]["bounds"]
    proj_ext.wkt2 = PROJECTIONS[proj_key]["wkt"]

    return item


def create_region_collection(reg):
    """
    TODO
    """
    region = Collection(
        id=f"NALCMS_{reg}",
        description=f"Land classification for {REGIONS[reg]}",
        extent=EXTENTS[reg],
        title=f"NALCMS for {REGIONS[reg]}",
        stac_extensions=None,
        license=LICENSE,
        summaries=Summaries({
            "platform":
            sum([v["platform"] for v in SATELLITES.values()], []),
            "instruments":
            sum([v["instruments"] for v in SATELLITES.values()], []),
            "constellation":
            sum([v["constellation"] for v in SATELLITES.values()], []),
            "gsd":
            GSDS,
        }))

    return region


def create_nalcms_collection():
    """
    TODO
    """
    nalcms = Collection(
        id=ID,
        description=DESCRIPTION,
        extent=EXTENTS["NA"],
        title=TITLE,
        stac_extensions=[
            "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
        ],
        license=LICENSE,
        keywords=KEYWORDS,
        providers=PROVIDER,
        summaries=Summaries({
            "platform":
            sum([v["platform"] for v in SATELLITES.values()], []),
            "instruments":
            sum([v["instruments"] for v in SATELLITES.values()], []),
            "constellation":
            sum([v["constellation"] for v in SATELLITES.values()], []),
            "gsd":
            GSDS,
        }))
    proj_ext = SummariesProjectionExtension(nalcms)
    proj_ext.epsg = list(PROJECTIONS.values())
    nalcms.add_link(LICENSE_LINK)

    for reg in REGIONS.keys():
        region = create_region_collection(reg)
        nalcms.add_child(region)

        for gsd, year in [(g, y) for g in GSDS for y in YEARS]:
            if (gsd == 250) and (reg != "NA"):
                continue
            item = create_item(reg, gsd, year)
            region.add_child(item)

    return nalcms
