#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 University of Dundee & Open Microscopy Environment.
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

import os
import sys
import subprocess


def restore_database(source):
    """
    restote the database from a database dump file
    """
    from omero_search_engine import search_omero_app
    main_dir = os.path.abspath(os.path.dirname(__file__))
    print(main_dir)
    mm = main_dir.replace("omero_search_engine/database", "")
    print(mm)
    sys.path.append(mm)
    dat_file_name = os.path.join(mm, "app_data/omero.pgdump")
    print(dat_file_name)
    for data_source in search_omero_app.config.database_connectors.keys():
        if source.lower() != "all" and data_source.lower() != source.lower():
            continue
        conn = search_omero_app.config.database_connectors[data_source]
        restore_command = "psql --username %s  --host %s --port %s -d %s -f  %s" % (
            search_omero_app.config.get("DATA_SOURCES").get("DATABASE_USER"),
            search_omero_app.config.get("DATA_SOURCES").get("DATABASE_SERVER_URI"),
            search_omero_app.config.get("DATA_SOURCES").get("DATABASE_PORT"),
            search_omero_app.config.get("DATA_SOURCES").get("DATABASE_NAME"),
            dat_file_name,
        )
        print(restore_command)
        try:
            proc = subprocess.Popen(
                restore_command,
                shell=True,
                env={"PGPASSWORD": search_omero_app.config.get("DATABASE_PASSWORD")},
            )
            proc.wait()
        except Exception as e:
            print("Exception happened during dump %s" % (e))
