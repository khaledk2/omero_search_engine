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

import sys
from utils import query_the_search_ending, logging


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

query_1 = {
    "and_filters": [
        {"key": "Organism", "value": "Homo sapiens", "operator": "equals"},
        {"key": "Antibody Identifier", "value": "CAB034889", "operator": "equals"},
    ],
    "or_filters": [
        [
            {"key": "Organism Part", "value": "Prostate", "operator": "equals"},
            {
                "key": "Organism Part Identifier",
                "value": "T-77100",
                "operator": "equals",
            },
        ]
    ],
}
query_2 = {
    "and_filters": [{"key": "Organism", "value": "Mus musculus", "operator": "equals"}]
}
main_attributes = []
logging.info("Sending the first query:")
results_1 = query_the_search_ending(query_1, main_attributes)
logging.info("=========================")
logging.info("Sending the second query:")
# It is possible to get the results and exclude one project, e.g. 101
# owner_id': 2

main_attributes_3 = {
    "and_main_attributes": [{"key": "project_id", "value": 101, "operator": "equals"}]
}
results_4 = query_the_search_ending(query_2, main_attributes_3)
