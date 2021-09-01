import unittest

from stactools.nalcms.stac import (create_period_collection, create_item)


class TestSTAC(unittest.TestCase):
    def test_create_item(self):
        args = {"reg": "NA", "gsd": 30, "year": "2010-2015", "source": "cog_filename.tif"}
        ID = f"{args['reg']}_{args['year']}_{args['gsd']}m"

        item = create_item(**args)

        self.assertEqual(item.id, ID)

        asset_hrefs = [asset.href for asset in item.assets.values()]
        self.assertIn(args["source"], asset_hrefs)

        asset = item.assets["data"]

        assert "metadata" in item.assets
        assert "data" in asset.roles

        # Projection Extension
        assert "proj:epsg" in item.properties
        assert "proj:bbox" in item.properties
        assert "proj:transform" in item.properties
        assert "proj:shape" in item.properties

        # File Extension
        assert "file:size" in asset.extra_fields
        assert "file:values" in asset.extra_fields
        assert len(asset.extra_fields["file:values"]) > 0

        # Raster Extension
        assert "raster:bands" in asset.extra_fields
        assert len(asset.extra_fields["raster:bands"]) == 1
        assert "nodata" in asset.extra_fields["raster:bands"][0]
        assert "sampling" in asset.extra_fields["raster:bands"][0]
        assert "data_type" in asset.extra_fields["raster:bands"][0]
        assert "spatial_resolution" in asset.extra_fields["raster:bands"][0]

        # Label Extension
        assert "label:type" in item.properties
        assert "label:tasks" in item.properties
        assert "label:properties" in item.properties
        assert "label:description" in item.properties
        assert "label:classes" in item.properties

        item.validate()

    def test_create_collection(self):
        collection = create_period_collection("yearly")

        collection.set_root(None)
        summaries = collection.summaries.to_dict()

        # Projection Extension
        assert "proj:epsg" in summaries

        # Label Extension

        assert "label:type" in summaries
        assert "label:tasks" in summaries
        assert "label:classes" in summaries

        collection.validate()
