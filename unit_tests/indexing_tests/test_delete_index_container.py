#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2022 University of Dundee & Open Microscopy Environment.
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Basic app unit tests
"""

import unittest

# from omero_search_engine.api.v1.resources.utils import (
#    update_data_source_cache,
#    delete_container,
# )

from omero_search_engine.api.v1.resources.resource_analyser import (
    return_containes_images,
)

# from omero_search_engine.cache_functions.elasticsearch.elasticsearch_templates import (  # noqa
#    image_template,
#    key_values_resource_cache_template,
# )


from test_data import (
    containers_n,
)

from manage import (
    delete_conatiner,
    index_container_from_database,
)

from omero_search_engine import create_app

create_app("testing")

# for data_source in search_omero_app.config.database_connectors.keys():


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_delete_index_one_container(self):
        import time

        # test delete container
        ids_ = list(containers_n.keys())
        ids = ",".join(ids_)
        data_source = "omero1" #containers_n[ids_[0]]["data_source"]
        resource = "project" #containers_n[ids_[0]]["type"]
        delete_conatiner(resource, data_source, ids, "True")
        time.sleep(60)
        for id, container in containers_n.items():
            containers_ad = return_containes_images(
                container["data_source"],
            )
            for con1 in containers_ad["results"]["results"]:
                self.assertNotEquals(int(con1["id"]), int(id))
        # test index container
        index_container_from_database(resource, data_source, ids, "False", "True")
        time.sleep(60)
        containers_ai = return_containes_images("omero1")
        for id, container in containers_n.items():
            found = False
            cur_res = None
            for con1 in containers_ai["results"]["results"]:
                if int(con1["id"]) == int(id) and con1["type"] == container["type"]:
                    found = True
                    cur_res = con1
                    break
            self.assertTrue(found)
            self.assertEqual(int(cur_res["image count"]), int(container["image count"]))
            self.assertEqual(cur_res["name"], container["name"])


if __name__ == "__main__":
    unittest.main()
