# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""
initial data loader
"""
import click
import os
from functools import partial
from tornado.ioloop import IOLoop

import koi
from ..models.framework import db
from repository.app import CONF_DIR


@click.command(help='load fixture data')
@click.option('--repository', help='id of repository to load data to', required=True)
@click.argument('files', nargs=-1, type=click.Path('rb'))
def cli(files, repository):
    """
    Takes a list of files or a directory, and loads any ttl or xml files to the given repository.
    If repository namespace does not already exist, create the namespace before loading the data
    :param files
    :param repository: repository id / namespace in blazegraph
    """
    koi.load_config(CONF_DIR)
    for fixture in files:
        if os.path.isdir(fixture):
            IOLoop.current().run_sync(partial(db.load_directory, fixture, repository))
        else:
            IOLoop.current().run_sync(partial(db.load_data, fixture, repository))
