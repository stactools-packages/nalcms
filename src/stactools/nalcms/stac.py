import logging
import os
from shapely.geometry import box
from datetime import datetime

from pystac import (Collection, Asset, Extent, SpatialExtent, TemporalExtent,
                    CatalogType, MediaType)

from pystac.extensions.item_assets import ItemAssetsExtension
from pystac.extensions.projection import SummariesProjectionExtension, ProjectionExtension
from pystac.extensions.scientific import ScientificExtension
from pystac.item import Item
from pystac.summaries import Summaries

from stactools.nalcms.constants import (
    CITATION,
    COLLECTION_ID,
    DOI,
    EXTENTS,
    GSDS,
    HREFS_ZIP,
    HREF_DIR,
    KEYWORDS,
    PROJECTIONS,
    REGIONS,
    SATELLITES,
    SPATIAL_EXTENT,
    TEMPORAL_EXTENT,
    COLLECTION_LICENSE,
    COLLECTION_TITLE,
    COLLECTION_DESCRIPTION,
    NRCAN_PROVIDER,
    INEGI_PROVIDER,
    CONAFOR_PROVIDER,
    USGS_PROVIDER,
    CEC_PROVIDER,
    HREFS_METADATA,
    YEARS,
)

from stactools.nalcms.assets import ITEM_ASSETS

logger = logging.getLogger(__name__)


def create_nalcms_collection() -> Collection:
    """Create a STAC Collection for North American Land Change Monitoring System Data

    These are cartographic products and are intended to be interpreted at the resolution identified.
    Read the original metadata for data caveats.

    Returns:
        Collection: STAC Collection object
    """
    extent = Extent(
        SpatialExtent([bounding_extent(EXTENTS.values())]),
        TemporalExtent(TEMPORAL_EXTENT),
    )

    collection = Collection(
        id=COLLECTION_ID,
        description=COLLECTION_DESCRIPTION,
        title=COLLECTION_TITLE,
        stac_extensions=[
            "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
        ],
        license=COLLECTION_LICENSE,
        keywords=KEYWORDS,
        providers=[
            NRCAN_PROVIDER,
            INEGI_PROVIDER,
            CONAFOR_PROVIDER,
            USGS_PROVIDER,
            CEC_PROVIDER,
        ],
        catalog_type=CatalogType.RELATIVE_PUBLISHED,
        extent=extent,
        summaries=Summaries({
            "platform":
            sum([v["platform"] for v in SATELLITES.values()], []),
            "instruments":
            sum([v["instruments"] for v in SATELLITES.values()], []),
            "constellation":
            sum([v["constellation"] for v in SATELLITES.values()], []),
            "gsd":
            GSDS,
        }),
    )

    # Include projection information
    proj_ext = SummariesProjectionExtension(collection)
    proj_ext.epsg = list([v['epsg'] for v in PROJECTIONS.values()])
    proj_ext.wkt = list([v['wkt'] for v in PROJECTIONS.values()])

    scientific = ScientificExtension.ext(collection, add_if_missing=True)
    scientific.doi = DOI
    scientific.citation = CITATION

    item_assets = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_assets.item_assets = ITEM_ASSETS

    for metadata in HREFS_METADATA.items():
        collection.add_asset(
            f"{metadata[0]} metadata",
            Asset(
                href=(
                    f"{HREF_DIR}{metadata[1]}"  # noqa
                ),
                title=f"NALCMS {metadata[0]} Metadata",
                description=("NALCMS created metadata."),
                media_type="application/msword",
                roles=["metadata"],
            ),
        )

    return collection


def create_region_collection(reg) -> Collection:
    """
    TODO
    """
    extents = [v for k, v in EXTENTS.items if reg in k]
    extent = Extent(
        SpatialExtent([bounding_extent(extents)]),
        TemporalExtent(TEMPORAL_EXTENT),
    )

    collection = Collection(
        id=f"NALCMS_{reg}",
        description=f"Land classification for {REGIONS[reg]}",
        extent=extent,
        title=f"NALCMS for {REGIONS[reg]}",
        stac_extensions=[
            "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
        ],
        license=COLLECTION_LICENSE,
        summaries=Summaries({
            "platform":
            sum([v["platform"] for v in SATELLITES.values()], []),
            "instruments":
            sum([v["instruments"] for v in SATELLITES.values()], []),
            "constellation":
            sum([v["constellation"] for v in SATELLITES.values()], []),
            "gsd":
            GSDS,
        }),
    )

    # Include projection information
    proj_ext = SummariesProjectionExtension(collection)
    proj_ext.epsg = list(
        [v['epsg'] for k, v in PROJECTIONS.items() if reg in k])
    proj_ext.wkt = list([v['wkt'] for k, v in PROJECTIONS.items() if reg in k])

    return collection


def create_item(reg, gsd, year) -> Item:
    """
    TODO
    """
    constants_key = f"{gsd}m_{year}_{reg}"

    # bbox and geometry
    bbox = EXTENTS[constants_key]
    polygon = box(*bbox, ccw=True)
    coordinates = [list(i) for i in list(polygon.exterior.coords)]
    geometry = {"type": "Polygon", "coordinates": [coordinates]}

    # Item properties
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
    item = Item(
        id=f"{reg}_{year}_{gsd}m",
        geometry=geometry,
        bbox=bbox,
        datetime=datetime.strptime(years[0], "%Y"),
        properties=properties,
        stac_extensions=[
            "https://stac-extensions.github.io/projection/v1.0.0/schema.json"
        ],
    )

    # Create metadata asset
    metadata_href = os.path.join(HREF_DIR, HREFS_METADATA[f"{gsd}m_{year}"])
    item.add_asset(
        "metadata",
        Asset(
            href=metadata_href,
            media_type=MediaType.JSON,
            roles=["metadata"],
            title="Metadata for land cover {diff}for {year} ({gsd} m)",
        ),
    )

    # Create source data asset
    data_href = os.path.join(HREF_DIR, HREFS_ZIP[f"{gsd}m_{year}_{reg}"])
    item.add_asset(
        "data",
        Asset(
            href=data_href,
            media_type="application/zip",
            roles=["data"],
            title=
            "Data for land cover {diff}over {REGIONS[reg]} for {year} ({gsd} m)",
        ),
    )

    # Include projection information
    proj_ext = ProjectionExtension.ext(item)
    proj_ext.epsg = PROJECTIONS[constants_key]["epsg"]
    proj_ext.transform = PROJECTIONS[constants_key]["transform"]
    proj_ext.bbox = PROJECTIONS[constants_key]["bounds"]
    proj_ext.wkt2 = PROJECTIONS[constants_key]["wkt"]

    return item


def build_nalcms() -> Collection:
    """
    TODO
    """

    nalcms = create_nalcms_collection()

    for reg in REGIONS.keys():
        region = create_region_collection(reg)
        nalcms.add_child(region)

        for gsd, year in [(g, y) for g in GSDS for y in YEARS]:
            if (gsd == 250) and (reg != "NA"):
                continue
            item = create_item(reg, gsd, year)
            region.add_child(item)

    return nalcms


def bounding_extent(extents):
    """Find the outer extent of a set of extents
    """
    xmin = min(extent[0] for extent in extents)
    ymin = min(extent[1] for extent in extents)
    xmax = max(extent[2] for extent in extents)
    ymax = max(extent[3] for extent in extents)

    return [xmin, ymin, xmax, ymax]
