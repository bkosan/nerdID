import tempfile
import unittest

import pandas as pd

import prep


class TestPrep(unittest.TestCase):
    def test_validate_ok(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write(
                "image_url,species_code,common_name,group_id,license,credit\n"
                "u,x,y,g,l,c\n"
            )
            name = f.name
        prep.cmd_validate(name)

    def test_validate_missing(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("image_url,common_name\nhttps://example.com,img\n")
            name = f.name
        with self.assertRaises(SystemExit):
            prep.cmd_validate(name)


if __name__ == "__main__":
    unittest.main()
