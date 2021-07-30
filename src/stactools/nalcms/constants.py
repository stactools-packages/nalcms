from datetime import datetime
from pystac import Provider

COLLECTION_ID = "nalcms"
COLLECTION_EPSG = 3978
COLLECTION_TITLE = "North American Land Change Monitoring System data"
COLLECTION_LICENSE = "PDDL-1.0"

COLLECTION_DESCRIPTION = (
    "Land Cover change maps shows class transitions from 2010 to 2015 over Canada, Alaska, the conterminous United States, and Mexico. "
    "Changes have been assessed from Land Cover maps at 30 meters resolution.")

#[xmin, ymin, xmax, ymax]]
#[west, east, noth, south]

SPATIAL_EXTENT = [-170.0, -50.0, 84.0, 14.0]
# The first grid was released in 2003, and Items will provide additional
# temporal information as they are created
TEMPORAL_EXTENT = [
    datetime(2005, 1, 1),
    None,
]

NRCAN_PROVIDER = Provider(
    name=
    "Natural Resources Canada / Canada Centre Mapping and Earth Observation",
    roles=["producer", "processor"],
    url="https://www.nrcan.gc.ca")

INEGI_PROVIDER = Provider(name="Instituto Nacional de Estadística y Geografía",
                          roles=["producer", "processor"],
                          url="https://www.inegi.org.mx/")

CONAFOR_PROVIDER = Provider(name="Comisión Nacional Forestal",
                            roles=["producer", "processor"],
                            url="https://www.gob.mx/conafor")

USGS_PROVIDER = Provider(name="U.S. Geological Survey",
                         roles=["producer", "processor"],
                         url="https://www.usgs.gov")

CEC_PROVIDER = Provider(
    name="Commission for Environmental Cooperation",
    roles=["producer", "processor"],
    url="http://www.cec.org/north-american-environmental-atlas/")
