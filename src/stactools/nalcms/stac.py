import logging

from pystac import (
    Collection,
    Asset,
    Extent,
    SpatialExtent,
    TemporalExtent,
    CatalogType,
)

from pystac.extensions.item_assets import ItemAssetsExtension

from stactools.nalcms.constants import (
    COLLECTION_ID,
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

    for metadata in HREFS_METADATA.items():
        collection.add_asset(
            f"{metadata[0]} metadata",
            Asset(
                href=(
                    f"http://www.cec.org/wp-content/uploads/wpallimport/files/Atlas/Files/{metadata[1]}"  # noqa
                ),
                title=f"NALCMS {metadata[0]} Metadata",
                description=("NALCMS created metadata."),
                media_type="application/msword",
                roles=["metadata"],
            ),
        )

    return collection


# def create_item(reg, gsd, year):
#     """
#     TODO
#     """
#     bbox = EXTENTS[reg]
#     polygon = shapely.geometry.box(*bbox, ccw=True)
#     coordinates = [list(i) for i in list(polygon.exterior.coords)]
#     geometry = {"type": "Polygon", "coordinates": [coordinates]}

#     years = year.split("-")
#     diff = "change " if "-" in year else ""
#     properties = {
#         "title": f"{reg} land cover {diff}({year}, {gsd} m)",
#         "description": f"Land cover {diff}for {year} over {REGIONS[reg]} ({gsd} m)",
#         "start_datetime": datetime.strptime(years[0], "%Y"),
#         "end_datetime": datetime.strptime(years[-1], "%Y"),
#         "gsd": gsd,
#     }

#     # Create item
#     item = pystac.Item(
#         id=f"{reg}_{year}_{gsd}m",
#         geometry=geometry,
#         bbox=bbox,
#         datetime=datetime.strptime(years[0], "%Y"),
#         properties=properties,
#         stac_extensions=[
#             "https://stac-extensions.github.io/projection/v1.0.0/schema.json"
#         ],
#     )

#     # Create metadata asset
#     metadata_href = os.path.join(HREF_DIR, HREFS_METADATA[f"{gsd}m_{year}"])
#     item.add_asset(
#         "metadata",
#         pystac.Asset(
#             href=metadata_href,
#             media_type=MediaType.JSON,
#             roles=["metadata"],
#             title="Metadata for land cover {diff}for {year} ({gsd} m)",
#         ),
#     )

#     # Create source data asset
#     data_href = os.path.join(HREF_DIR, HREFS_ZIP[f"{gsd}m_{year}_{reg}"])
#     item.add_asset(
#         "data",
#         pystac.Asset(
#             href=data_href,
#             media_type="application/zip",
#             roles=["data"],
#             title="Data for land cover {diff}over {REGIONS[reg]} for {year} ({gsd} m)",
#         ),
#     )

#     # Include projection information
#     proj_key = f"{gsd}m_{year}_{reg}"
#     proj_ext = ProjectionExtension.ext(item)
#     proj_ext.epsg = PROJECTIONS[proj_key]["epsg"]
#     proj_ext.transform = PROJECTIONS[proj_key]["transform"]
#     proj_ext.bbox = PROJECTIONS[proj_key]["bounds"]
#     proj_ext.wkt2 = PROJECTIONS[proj_key]["wkt"]

#     return item

# def create_region_collection(reg):
#     """
#     TODO
#     """
#     region = Collection(
#         id=f"NALCMS_{reg}",
#         description=f"Land classification for {REGIONS[reg]}",
#         extent=EXTENTS[reg],
#         title=f"NALCMS for {REGIONS[reg]}",
#         stac_extensions=None,
#         license=LICENSE,
#         summaries=Summaries(
#             {
#                 "platform": sum([v["platform"] for v in SATELLITES.values()], []),
#                 "instruments": sum([v["instruments"] for v in SATELLITES.values()], []),
#                 "constellation": sum(
#                     [v["constellation"] for v in SATELLITES.values()], []
#                 ),
#                 "gsd": GSDS,
#             }
#         ),
#     )

#     return region

# def create_nalcms_collection():
#     """
#     TODO
#     """
#     nalcms = Collection(
#         id=ID,
#         description=DESCRIPTION,
#         extent=EXTENTS["NA"],
#         title=TITLE,
#         stac_extensions=[
#             "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
#         ],
#         license=LICENSE,
#         keywords=KEYWORDS,
#         providers=PROVIDER,
#         summaries=Summaries(
#             {
#                 "platform": sum([v["platform"] for v in SATELLITES.values()], []),
#                 "instruments": sum([v["instruments"] for v in SATELLITES.values()], []),
#                 "constellation": sum(
#                     [v["constellation"] for v in SATELLITES.values()], []
#                 ),
#                 "gsd": GSDS,
#             }
#         ),
#     )
#     proj_ext = SummariesProjectionExtension(nalcms)
#     proj_ext.epsg = list(PROJECTIONS.values())
#     nalcms.add_link(LICENSE_LINK)

#     for reg in REGIONS.keys():
#         region = create_region_collection(reg)
#         nalcms.add_child(region)

#         for gsd, year in [(g, y) for g in GSDS for y in YEARS]:
#             if (gsd == 250) and (reg != "NA"):
#                 continue
#             item = create_item(reg, gsd, year)
#             region.add_child(item)

#     return nalcms
