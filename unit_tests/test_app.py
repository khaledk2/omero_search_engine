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
import json

from omero_search_engine.api.v1.resources.utils import (
    elasticsearch_query_builder,
    search_resource_annotation,
)

from omero_search_engine.cache_functions.elasticsearch.elasticsearch_templates import (  # noqa
    image_template,
    key_values_resource_cache_template,
)

from omero_search_engine.validation.results_validator import (
    Validator,
    check_number_images_sql_containers_using_ids,
)
from omero_search_engine.cache_functions.elasticsearch.transform_data import (
    delete_es_index,
    create_index,
    get_all_indexes_from_elasticsearch,
)
from test_data import (
    sql,
    valid_and_filters,
    valid_or_filters,
    not_valid_and_filters,
    not_valid_or_filters,
    query,
    query_image_and,
    query_image_or,
    query_image_and_or,
    simple_queries,
    query_in,
    images_keys,
    images_value_parts,
    contains_not_contains_queries,
    image_owner,
    image_group,
    image_owner_group,
)

from omero_search_engine import search_omero_app, create_app

create_app("testing")
# deep_check should be a configuration item
deep_check = True

# for data_source in search_omero_app.config.database_connectors.keys():


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_no_images_containers(self):
        for data_source in search_omero_app.config.database_connectors.keys():
            self.assertTrue(check_number_images_sql_containers_using_ids(data_source))

    def test_multi_or_quries(self):
        pass


if __name__ == "__main__":
    unittest.main()
