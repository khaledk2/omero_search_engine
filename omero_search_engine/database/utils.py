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
    print (search_omero_app.config.get("DATA_SOURCES"))
    print (search_omero_app.config.database_connectors.keys())
    for data_source in search_omero_app.config.get("DATA_SOURCES"):
        print(data_source["name"])
        if source and source.lower() != "all" and data_source["name"].lower() != source.lower():
            continue
        restore_command = "psql --username %s  --host %s --port %s -d %s -f  %s" % (
            data_source.get("DATABASE").get("DATABASE_USER"),
            data_source.get("DATABASE").get("DATABASE_SERVER_URI"),
            data_source.get("DATABASE").get("DATABASE_PORT"),
            data_source.get("DATABASE").get("DATABASE_NAME"),
            dat_file_name,
        )
        print("Resore command: %s"%restore_command)
        try:
            proc = subprocess.Popen(
                restore_command,
                shell=True,
                env={"PGPASSWORD": search_omero_app.config.get("DATABASE_PASSWORD")},
            )
            proc.wait()
        except Exception as e:
            print("Error, exception happened during dump %s" % (e))
