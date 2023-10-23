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

from . import stats
from flask import request, jsonify, make_response
import json
from tools.utils.logs_analyser import get_search_terms
from flask import jsonify, Response

@stats.route("/", methods=["GET"])
def index():
    return "OMERO search engine (stats API)"


@stats.route("/<resource>/search_terms", methods=["GET"])
def search_terms(resource):
    from omero_search_engine import search_omero_app
    logs_folder=search_omero_app.config.get("SEARCHENGINE_LOGS_FOLDER")
    content=get_search_terms(logs_folder,resource=resource,return_file_content=True)

    return Response(
        content,
        mimetype="text/csv",
        headers={
            "Content-disposition": "attachment; filename=%s_stats.csv"
                                   % (resource)
        },
    )

    return "OMERO search engine (search_terms API)"
