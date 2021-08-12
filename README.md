# stactools-nalcms

- Name: nalcms
- Package: `stactools.nalcms`
- PyPI: https://pypi.org/project/stactools-nalcms/
- Owner: @jbants
- Dataset homepage: http://www.cec.org/north-american-land-change-monitoring-system/
- STAC extensions used:
  - [proj](https://github.com/stac-extensions/projection/)

This package is intended to help describe the National Land Change Monitoring System (NALCMS) data hosted by the Commission for Environmental Cooperation (CEC) as [STAC](https://github.com/stac-spec).

### Command-line usage

Example command line functions:

```bash
scripts/stac nalcms create-collection ./examples/

scripts/stac nalcms create-item ./examples/
```

Use `stac nalcms --help` to see all subcommands and options.

