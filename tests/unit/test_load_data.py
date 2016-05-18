# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import os
from mock import patch
from click.testing import CliRunner

from repository.commands.load_data import cli

from koi.test_helpers import make_future

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
FIXTURE_FILE_COUNT = 5
TEST_NAMESPACE = 'c8ab01'

import sys
sys.argv = sys.argv[:1]


@patch('repository.commands.load_data.db.load_data', return_value=make_future(None))
def test_cli(load_data):
    params = ([
        os.path.abspath(os.path.join(FIXTURE_DIR, 'sample.xml')),
        os.path.abspath(os.path.join(FIXTURE_DIR, 'sample.xml')),
        os.path.abspath(os.path.join(FIXTURE_DIR, 'sample.xml')),
        os.path.abspath(os.path.join(FIXTURE_DIR, 'sample.xml')),
        '--repository', 'c8ab01'
    ])

    runner = CliRunner()
    result = runner.invoke(cli, params)

    assert load_data.call_count == 4
    assert result.exit_code == 0

#FIXME: DON'T REALLY LIKE THIS UNIT TEST AS THE NUMBER OF INITIAL DATA FILE IS NOT REALLY A MEANINGFUL THING
#AND WILL VARY FROM ONE SITE TO ANOTHER
@patch('repository.commands.load_data.db.load_data', return_value=make_future(None))
def test_cli_path(load_data):
    params = ([os.path.abspath(FIXTURE_DIR), '--repository', TEST_NAMESPACE])

    runner = CliRunner()
    result = runner.invoke(cli, params)

    assert load_data.call_count >= FIXTURE_FILE_COUNT
    assert result.exit_code == 0


@patch('repository.commands.load_data.db.load_data', return_value=make_future(None))
def test_cli_repository_from_options(load_data):
    params = ([os.path.abspath(FIXTURE_DIR),  '--repository', TEST_NAMESPACE])

    runner = CliRunner()
    result = runner.invoke(cli, params)

    assert load_data.call_count >= FIXTURE_FILE_COUNT
    assert result.exit_code == 0


@patch('repository.commands.load_data.db.load_data', return_value=make_future(None))
def test_cli_no_repository(load_data):
    params = ([os.path.abspath(FIXTURE_DIR)])

    runner = CliRunner()
    result = runner.invoke(cli, params)

    assert not load_data.called
    assert result.exit_code == 2
