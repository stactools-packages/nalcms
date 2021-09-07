import logging
import os
from shapely.geometry import box
import itertools as it
from typing import Any, List, Union

from pystac import (Collection, Asset, Extent, SpatialExtent, TemporalExtent, CatalogType,
                    MediaType)

from pystac.extensions.projection import (SummariesProjectionExtension, ProjectionExtension)
from pystac.extensions.scientific import ScientificExtension
from pystac.extensions.raster import RasterExtension, RasterBand
from pystac.extensions.file import FileExtension
from pystac.extensions.label import (
    LabelClasses,
    LabelExtension,
    LabelTask,
    LabelType,
)
from pystac.item import Item
from pystac.summaries import Summaries
from pystac.utils import str_to_datetime

from stactools.nalcms.constants import (
    CITATION,
    COLLECTION_ID,
    DATA_TYPE,
    DOI,
    FILE_SIZES,
    NODATA,
    PERIODS,
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

values: List[Any] = [dict(values=[i], summary=s) for i, s in VALUES.items()]
values_change: List[Any] = [
    dict(values=[int(f"{v1}{str(v2).zfill(2)}")], summary=f'"{VALUES[v1]}" to "{VALUES[v2]}"')
    for v1, v2 in it.product(VALUES.keys(), VALUES.keys())
]


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
            "gsd": [float(gsd) for gsd in GSDS],
        }),
    )

    # Include projection information
    proj_ext = SummariesProjectionExtension(collection)
    proj_ext.epsg = list(set([v['epsg'] for v in PROJECTIONS.values()]))

    scientific = ScientificExtension.ext(collection, add_if_missing=True)
    scientific.doi = DOI
    scientific.citation = CITATION

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


def create_period_collection(period: str) -> Collection:
    """Returns a STAC Collection for yearly land classifications or change between years.

    Args:
        period (str): "yearly" or "change".
    """
    years = PERIODS[period]
    extents = [v for k, v in SPATIAL_EXTENTS.items() if k.split("_")[1] in years]
    extent = Extent(
        SpatialExtent([bounding_extent(extents)]),
        TemporalExtent(TEMPORAL_EXTENT),
    )

    collection = Collection(
        id=f"NALCMS_{period}",
        description=f"Land classification, {period}",
        extent=extent,
        title=f"NALCMS, {period}",
        license=COLLECTION_LICENSE,
        stac_extensions=["https://stac-extensions.github.io/projection/v1.0.0/schema.json"],
        summaries=Summaries({
            "platform":
            sum([v["platform"] for v in SATELLITES.values()], []),
            "instruments":
            sum([v["instruments"] for v in SATELLITES.values()], []),
            "constellation":
            sum([v["constellation"] for v in SATELLITES.values()], []),
            "gsd": [float(gsd) for gsd in GSDS],
            "file:values":
            values_change if period == "change" else values
        }),
    )

    # Include projection summaries
    proj_ext = SummariesProjectionExtension(collection)
    proj_ext.epsg = list(
        set([v['epsg'] for k, v in PROJECTIONS.items() if k.split("_")[1] in years]))

    # Include label information
    vals = values_change if period == "change" else values
    classes: List[Any] = sum([d["values"] for d in vals], [])
    label_ext = LabelExtension.summaries(collection, add_if_missing=True)
    label_ext.label_type = [LabelType.RASTER]
    label_ext.label_tasks = [LabelTask.CLASSIFICATION]
    label_ext.label_properties = None
    label_ext.label_classes = [
        # TODO: The STAC Label extension JSON Schema is incorrect.
        # https://github.com/stac-extensions/label/pull/8
        # https://github.com/stac-utils/pystac/issues/611
        # When it is fixed, this should be None, not the empty string.
        LabelClasses.create(classes, "")
    ]

    return collection


def create_item(reg: str, gsd: str, year: str, source: str) -> Union[Item, None]:
    """Returns a STAC Item for a given (region, GSD, year) if that combination
     exists in the dataset, else None.

    Args:
        reg (str): The Region.
        gsd (str): The GSD [m].
        year (str): The year or difference in years (e.g. "2010-2015").
        source (str): The path to the corresponding COG to be included as an
         asset.
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
        "gsd": float(gsd),
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
            media_type="application/vnd.ms-word.document",
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
    sampling: Any = ["area"]
    rast_band = RasterBand.create(nodata=NODATA[constants_key],
                                  sampling=sampling[0],
                                  data_type=DATA_TYPE[constants_key],
                                  spatial_resolution=float(gsd))
    rast_ext = RasterExtension.ext(data_asset, add_if_missing=True)
    rast_ext.bands = [rast_band]

    # Include file information
    vals = values_change if "-" in year else values
    file_ext = FileExtension.ext(data_asset, add_if_missing=True)
    file_ext.size = FILE_SIZES[constants_key]
    file_ext.values = vals

    # Include label information
    classes: List[Any] = sum([d["values"] for d in vals], [])
    label_ext = LabelExtension.ext(item, add_if_missing=True)
    label_ext.label_type = LabelType.RASTER
    label_ext.label_tasks = [LabelTask.CLASSIFICATION]
    label_ext.label_properties = None
    label_ext.label_description = ""
    label_ext.label_classes = [
        # TODO: The STAC Label extension JSON Schema is incorrect.
        # https://github.com/stac-extensions/label/pull/8
        # https://github.com/stac-utils/pystac/issues/611
        # When it is fixed, this should be None, not the empty string.
        LabelClasses.create(classes, "")
    ]

    return item


def bounding_extent(extents: List[Any]) -> List[Any]:
    """Find the outer extent of a list of extents
    """
    xmin = min(extent[0] for extent in extents)
    ymin = min(extent[1] for extent in extents)
    xmax = max(extent[2] for extent in extents)
    ymax = max(extent[3] for extent in extents)

    return [xmin, ymin, xmax, ymax]
