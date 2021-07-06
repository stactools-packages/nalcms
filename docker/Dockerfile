ARG STACTOOLS_VERSION=latest
FROM stacutils/stactools:$STACTOOLS_VERSION

WORKDIR /opt/stactools-nalcms

# For caching purposes, install dependencies but remove the actual package
COPY pyproject.toml setup.cfg ./
COPY src/stactools/nalcms/__init__.py src/stactools/nalcms/
RUN pip install . \
    && rm -r /opt/conda/lib/python3.8/site-packages/stactools/nalcms

COPY src ./src
RUN pip install .
