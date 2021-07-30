from typing import Dict
import pystac
from pystac.extensions.item_assets import AssetDefinition

LANDCOVER_CHANGE_30M_KEY = "landcover_change_30m"
LANDCOVER_2015_30M_KEY = "landcover_2015_30m"
LANDCOVER_2010_30M_KEY = "landcover_2010_30m"
LANDCOVER_2010_250M_KEY = "landcover_2010_250m"
LANDCOVER_2005_250M_KEY = "landcover_2005_250m"
LANDCOVER_CHANGE_250M_KEY = "landcover_change_250m"

ITEM_ASSETS: Dict[str, AssetDefinition] = {
    LANDCOVER_CHANGE_30M_KEY:
    AssetDefinition({
        "title":
        "Land Cover Change 30m, 2010-2015 (Landsat)",
        "description": ("This map demonstrates land cover change between 2010 and 2015 "
                        "in North America at a spatial resolution of 30 meters. "
                        "The dataset shows the 2010-2015 changes between the nineteen Level "
                        "II land cover classes, which were defined using the Land Cover "
                        "Classification System (LCCS) standard developed by the "
                        "Food and Agriculture Organization (FAO) of United Nations."),
        "type":
        pystac.MediaType.COG,
        "roles": ["data"],
    }),
    LANDCOVER_2015_30M_KEY:
    AssetDefinition({
        "title":
        "Land Cover 30m, 2015 (Landsat and RapidEye)",
        "description": ("This map of North American land cover at a spatial resolution of 30"
                        " meters provides a harmonized view of the physical cover of Earth’s"
                        " surface across the continent based on 2015 Landsat satellite imagery"
                        " for Canada and the United States, and RapidEye imagery for Mexico."
                        " Nineteen Level II land cover classes were defined using the Land"
                        " Cover Classification System (LCCS) standard developed by the Food and"
                        " Agriculture Organization (FAO) of the United Nations."),
        "type":
        pystac.MediaType.COG,
        "roles": ["data"],
    }),
    LANDCOVER_2010_30M_KEY:
    AssetDefinition({
        "title":
        "Land Cover, 2010 (Landsat, 30m)",
        "description": ("This map of North American land cover at a spatial resolution of 30"
                        " meters provides a harmonized view of the physical cover of Earth’s"
                        " surface across the continent based on 2010 Landsat satellite imagery."
                        " Nineteen Level II land cover classes were defined using the Land"
                        " Cover Classification System (LCCS) standard developed by the Food and"
                        " Agriculture Organization (FAO) of United Nations."),
        "type":
        pystac.MediaType.COG,
        "roles": ["data"],
    }),
    LANDCOVER_CHANGE_250M_KEY:
    AssetDefinition({
        "title":
        "Land Cover Change, 2005-2010 (MODIS, 250m)",
        "description": ("This map demonstrates land cover change between 2005 and 2010 in North"
                        " America at a spatial resolution of 250 meters. The dataset shows the"
                        " 2005-2010 changes between the nineteen Level II land cover classes,"
                        " which were defined using the Land Cover Classification System (LCCS)"
                        " standard developed by the Food and Agriculture Organization (FAO) of"
                        " United Nations."),
        "type":
        pystac.MediaType.COG,
        "roles": ["data"],
    }),
    LANDCOVER_2010_250M_KEY:
    AssetDefinition({
        "title":
        "Land Cover, 2010 (MODIS, 250m)",
        "description": ("This map of North American land cover at a spatial resolution of 250"
                        " meters provides a harmonized view of the physical cover of Earth’s"
                        " surface across the continent based on 2010 Moderate Resolution"
                        " Imaging Spectroradiometer (MODIS) satellite imagery. Nineteen Level"
                        " II land cover classes were defined using the Land Cover"
                        " Classification System (LCCS) standard developed by the Food and"
                        " Agriculture Organization (FAO) of United Nations."),
        "type":
        pystac.MediaType.COG,
        "roles": ["data"],
    }),
    LANDCOVER_2005_250M_KEY:
    AssetDefinition({
        "title":
        "Land Cover, 2005 (MODIS, 250m)",
        "description": ("This map of North American land cover at a spatial resolution of 250"
                        " meters provides a harmonized view of the physical cover of Earth’s"
                        " surface across the continent based on 2005 Moderate Resolution"
                        " Imaging Spectroradiometer (MODIS) satellite imagery. Nineteen Level"
                        " II land cover classes were defined using the Land Cover"
                        " Classification System (LCCS) standard developed by the Food and"
                        " Agriculture Organization (FAO) of United Nations."),
        "type":
        pystac.MediaType.COG,
        "roles": ["data"],
    }),
}
