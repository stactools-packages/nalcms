from datetime import datetime
import re
import logging

from pystac import (
    Collection,
    Item,
    Asset,
    Extent,
    SpatialExtent,
    TemporalExtent,
    CatalogType,
    MediaType,
)
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.item_assets import ItemAssetsExtension
from pystac.extensions.scientific import ScientificExtension

from stactools.nalcms.constants import (
    COLLECTION_ID,
    SPATIAL_EXTENT,
    TEMPORAL_EXTENT,
    COLLECTION_LICENSE,
    COLLECTION_TITLE,
    COLLECTION_DESCRIPTION,
    COLLECTION_EPSG,
    NRCAN_PROVIDER,
    INEGI_PROVIDER,
    CONAFOR_PROVIDER,
    USGS_PROVIDER,
    CEC_PROVIDER,
)

from stactools.nalcms.assets import ITEM_ASSETS

logger = logging.getLogger(__name__)


def create_collection() -> Collection:
    """Create a STAC Collection for North American Land Change Monitoring System Data

    These are cartographic products and are intended to be interpreted at the resolution identified.
    Read the original metadata for data caveats.

    Returns:
        Collection: STAC Collection object
    """
    extent = Extent(
        SpatialExtent([SPATIAL_EXTENT]),
        TemporalExtent(TEMPORAL_EXTENT),
    )

    collection = Collection(
        id=COLLECTION_ID,
        title=COLLECTION_TITLE,
        description=COLLECTION_DESCRIPTION,
        license=COLLECTION_LICENSE,
        providers=[
            NRCAN_PROVIDER,
            INEGI_PROVIDER,
            CONAFOR_PROVIDER,
            USGS_PROVIDER,
            CEC_PROVIDER,
        ],
        extent=extent,
        catalog_type=CatalogType.RELATIVE_PUBLISHED,
    )

    # scientific = ScientificExtension.ext(collection, add_if_missing=True)
    # scientific.doi = DOI
    # scientific.citation = CITATION

    item_assets = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_assets.item_assets = ITEM_ASSETS

    collection.add_asset(
        "metadata",
        Asset(
            href=(
                "http://www.cec.org/wp-content/uploads/wpallimport/files/Atlas/Files/Land_Cover_05_10/Metadata_NALCMS_2005_2010.doc"  # noqa
            ),
            title="NALCMS Metadata",
            description=("Metadata from NALCSM."),
            media_type="application/msword",
            roles=["metadata"],
        ),
    )

    return collection


def create_item(nc_href: str, cog_href: str) -> Item:
    """Create a STAC Item

    Collect metadata from a Seabed 2030 netcdf file to create the Item

    Args:
        nc_href (str): The HREF pointing to the GECBO grid netcdf file
        cog_href (str): The HREF pointing to the associated asset COG. The COG should
        be created in advance using `cog.create_cog`

    Returns:
        Item: STAC Item object
    """
    with Dataset(nc_href) as ds:
        properties = {
            "title": ds.title,
            "institution": ds.institution,
            "source": ds.source,
            "history": ds.history,
            "comment": ds.comment,
        }

        dims = ds.dimensions
        ds_shape = [dims["lon"].size, dims["lat"].size]
        x_cellsize = 360.0 / float(dims["lon"].size)
        y_cellsize = 180.0 / float(dims["lat"].size)

    global_geom = {
        "type": "Polygon",
        "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]],
    }

    # Create item
    item = pystac.Item(
        id=item_id,
        geometry=geometry,
        bbox=[float(x) for x in bbox],
        datetime=dataset_datetime,
        properties=properties,
        geometry=global_geom,
        bbox=SPATIAL_EXTENT,
        datetime=item_datetime,
        stac_extensions=[],
    )

    proj_attrs = ProjectionExtension.ext(item, add_if_missing=True)
    proj_attrs.epsg = SEABED_EPSG
    proj_attrs.bbox = SPATIAL_EXTENT
    proj_attrs.shape = ds_shape
    proj_attrs.transform = [
        SPATIAL_EXTENT[0],
        x_cellsize,
        0.0,
        SPATIAL_EXTENT[1],
        0.0,
        -y_cellsize,
    ]

    # Add the COG asset
    item.add_asset(
        "image",
        Asset(
            href=cog_href,
            media_type=MediaType.COG,
            roles=["data"],
            title=properties["title"].replace("Grid", "COG"),
        ),
    )

    return item


def create_collection(metadata: dict):
    # Creates a STAC collection for a Natural Resources Canada Land Cover dataset

    # title = metadata.get("tiff_metadata").get("dct:title")

    utc = pytz.utc
    year = "2010"
    dataset_datetime = utc.localize(datetime.strptime(year, "%Y"))

    start_datetime = dataset_datetime
    end_datetime = start_datetime + relativedelta(years=5)

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
            pystac.SpatialExtent([[float(x) for x in bbox]]),
            pystac.TemporalExtent(
                [[start_datetime or None, end_datetime or None]])),
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
