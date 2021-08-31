[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/stactools-packages/nalcms/main?filepath=docs/installation_and_basic_usage.ipynb)

# stactools-nalcms

- Name: nalcms
- Package: `stactools.nalcms`
- PyPI: https://pypi.org/project/stactools-nalcms/
- Owner: @jbants
- Dataset homepage: http://www.cec.org/north-american-land-change-monitoring-system/
- STAC extensions used:
  - [proj](https://github.com/stac-extensions/projection/)
  - [raster](https://github.com/stac-extensions/raster/)
  - [file](https://github.com/stac-extensions/file/)
  - [scientific](https://github.com/stac-extensions/scientific/)

This package is intended to help describe the National Land Change Monitoring System (NALCMS) data hosted by the Commission for Environmental Cooperation (CEC) as [STAC](https://github.com/stac-spec).

## Usage

1. As a Python module

```python
from stactools.nalcms import stac
from stactools.nalcms.constants import GSDS, REGIONS, YEARS
import os

# Create the STAC
root_col = stac.create_nalcms_collection()
for reg in REGIONS.keys():
    region = stac.create_region_collection(reg)
    root_col.add_child(region)

    for gsd in GSDS:
        for year in YEARS[gsd]:
            item = stac.create_item(reg, gsd, year, "")
            if item:
                region.add_item(item)

# Create a specific STAC Item
item = stac.create_item("CAN", "30", "2010", source="path/to/cog.tif")
```

2. Using the CLI

```bash
scripts/stac nalcms create-collection -d ./examples/

scripts/stac nalcms create-item -d ./examples/

scripts/stac nalcms create-cog -s ./examples/image.tif -d ./examples/
```

Use `scripts/stac nalcms --help` to see all subcommands and options.

