import logging
import os
from shapely.geometry import box
import itertools as it
from typing import Any, List, Union

from pystac import (Collection, Asset, Extent, SpatialExtent, TemporalExtent, CatalogType,
                    MediaType)

from pystac.extensions.projection import (SummariesProjectionExtension, ProjectionExtension)
from pystac.extensions.scientific import ScientificExtension
# from pystac.extensions.raster import RasterExtension
# from pystac.extensions.file import FileExtension
from pystac.item import Item
from pystac.summaries import Summaries
from pystac.utils import str_to_datetime

from stactools.nalcms.constants import (
    CITATION,
    COLLECTION_ID,
    DOI,
    # FILE_SIZES,
    SPATIAL_EXTENTS,
    GSDS,
    HREFS_ZIP,
    HREF_DIR,
    KEYWORDS,
    PROJECTIONS,
    REGIONS,
    SATELLITES,
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
    VALUES,
)

logger = logging.getLogger(__name__)

values: Any = [{"value": [i], "summary": s} for i, s in VALUES.items()]
values_change: Any = [{
    "value": [int(f"{v1}{str(v2).zfill(2)}")],
    "summary": f'"{VALUES[v1]}" to "{VALUES[v2]}"'
} for v1, v2 in it.product(VALUES.keys(), VALUES.keys())]


def create_nalcms_collection() -> Collection:
    """Create a STAC Collection for North American Land Change Monitoring System
     Data.

    These are cartographic products and are intended to be interpreted at the
     resolution identified.

    Read the original metadata for data caveats.

    Returns:
        Collection: STAC Collection object
    """
    spatial_extents = list(SPATIAL_EXTENTS.values())
    extent = Extent(
        SpatialExtent([bounding_extent(spatial_extents)]),
        TemporalExtent(TEMPORAL_EXTENT),
    )

    collection = Collection(
        id=COLLECTION_ID,
        description=COLLECTION_DESCRIPTION,
        title=COLLECTION_TITLE,
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
    proj_ext.epsg = list(set([v['epsg'] for v in PROJECTIONS.values()]))
    # proj_ext.wkt = list(set([v['wkt'] for v in PROJECTIONS.values()]))

    scientific = ScientificExtension.ext(collection, add_if_missing=True)
    scientific.doi = DOI
    scientific.citation = CITATION

    # item_assets = ItemAssetsExtension.ext(collection, add_if_missing=True)
    # item_assets.item_assets = ITEM_ASSETS

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


def create_region_collection(reg: str) -> Collection:
    """
    TODO
    """
    extents = [v for k, v in SPATIAL_EXTENTS.items() if reg in k]
    extent = Extent(
        SpatialExtent([bounding_extent(extents)]),
        TemporalExtent(TEMPORAL_EXTENT),
    )

    collection = Collection(
        id=f"NALCMS_{reg}",
        description=f"Land classification for {REGIONS[reg]}",
        extent=extent,
        title=f"NALCMS for {REGIONS[reg]}",
        license=COLLECTION_LICENSE,
        stac_extensions=["https://stac-extensions.github.io/projection/v1.0.0/schema.json"],
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
    proj_ext.epsg = list(set([v['epsg'] for k, v in PROJECTIONS.items() if reg in k]))
    # proj_ext.wkt = list(set([v['wkt'] for k, v in PROJECTIONS.items() if reg in k]))

    return collection


def create_item(reg: str, gsd: str, year: str, source: str) -> Union[Item, None]:
    """Creates a STAC Item
    TODO
    """
    constants_key = f"{gsd}m_{year}_{reg}"

    if constants_key not in HREFS_ZIP.keys():
        return None

    # bbox and geometry
    bbox = SPATIAL_EXTENTS[constants_key]
    polygon = box(*bbox, ccw=True)
    coordinates = [list(i) for i in list(polygon.exterior.coords)]
    geometry = {"type": "Polygon", "coordinates": [coordinates]}

    # Item properties
    years = year.split("-")
    diff = "change " if "-" in year else ""
    properties = {
        "title": f"{reg} land cover {diff}({year}, {gsd} m)",
        "description": f"Land cover {diff}for {year} over {REGIONS[reg]} ({gsd} m)",
        "start_datetime": f"{years[0]}-01-01T00:00:00Z",
        "end_datetime": f"{years[-1]}-12-31T00:00:00Z",
        "gsd": gsd,
    }

    # Create item
    item = Item(
        id=f"{reg}_{year}_{gsd}m",
        geometry=geometry,
        bbox=bbox,
        datetime=str_to_datetime(f"{years[0]}, 1, 1"),
        properties=properties,
    )

    # Create metadata asset
    metadata_href = os.path.join(HREF_DIR, HREFS_METADATA[f"{gsd}m_{year}"])
    item.add_asset(
        "metadata",
        Asset(
            href=metadata_href,
            media_type=MediaType.JSON,
            roles=["metadata"],
            title=f"Metadata for land cover {diff}for {year} ({gsd} m)",
        ),
    )

    # Create source data asset
    if source:
        data_href = source
    else:
        data_href = os.path.join(HREF_DIR, HREFS_ZIP[f"{gsd}m_{year}_{reg}"])
    data_asset = Asset(
        href=data_href,
        media_type="application/zip" if not source else MediaType.COG,
        roles=["data"],
        title=(f"Data for land cover {diff}over "
               f"{REGIONS[reg]} for {year} ({gsd} m)"),
    )
    item.add_asset("data", data_asset)

    # Include projection information
    proj_ext = ProjectionExtension.ext(item, add_if_missing=True)
    proj_ext.epsg = PROJECTIONS[constants_key]["epsg"]
    proj_ext.transform = PROJECTIONS[constants_key]["transform"]
    proj_ext.bbox = PROJECTIONS[constants_key]["bounds"]
    proj_ext.wkt2 = PROJECTIONS[constants_key]["wkt"]
    proj_ext.shape = PROJECTIONS[constants_key]["shape"]

    # Include raster information
    # rast_ext = RasterExtension.ext(data_asset, add_if_missing=True)
    # rast_ext.nodata = NODATA[constants_key]
    # rast_ext.data_type = DATA_TYPE[constants_key]
    # rast_ext.spatial_resolution = gsd

    # Include file information
    # file_ext = FileExtension.ext(data_asset, add_if_missing=True)
    # file_ext.size = FILE_SIZES[constants_key]
    # file_ext.values = values_change if "-" in year else values

    return item


def bounding_extent(extents: List[Any]) -> List[Any]:
    """Find the outer extent of a list of extents
    """
    xmin = min(extent[0] for extent in extents)
    ymin = min(extent[1] for extent in extents)
    xmax = max(extent[2] for extent in extents)
    ymax = max(extent[3] for extent in extents)

    return [xmin, ymin, xmax, ymax]
