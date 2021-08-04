import unittest

from stactools.nalcms.stac import create_nalcms_collection, create_item


class TestSTAC(unittest.TestCase):
    def test_create_item(self):
        args = {"reg": "NA", "gsd": 30, "year": "2010-2015", "source": "cog_filename.tif"}

        item = create_item(**args)

        self.assertEqual(item.id, f"{args['reg']}_{args['year']}_{args['gsd']}m")

        for asset in item.assets.values():
            self.assertIn(args["source"], asset.href)

        item.validate()

    def test_create_collection(self):
        collection = create_nalcms_collection()
        collection.set_root(None)
        collection.validate()
