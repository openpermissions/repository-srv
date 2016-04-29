# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

from mock import patch
import repository.app


@patch('repository.app.audit')
@patch('repository.app.options')
@patch('tornado.ioloop.IOLoop.instance')
@patch('repository.app.koi.make_application')
@patch('repository.app.koi.make_server')
@patch('repository.app.koi.load_config')
def test_main_makes_an_application(load_config, make_server, make_application,
                                   instance, options, audit):
    repository.app.main()
    assert make_application.call_count == 1


@patch('repository.app.audit')
@patch('repository.app.options')
@patch('tornado.ioloop.IOLoop.instance')
@patch('repository.app.koi.make_server')
@patch('repository.app.koi.load_config')
def test_main_makes_a_server(load_config, make_server,
                             instance, options, audit):
    repository.app.main()
    assert make_server.call_count == 1


@patch('repository.app.audit')
@patch('repository.app.options')
@patch('tornado.ioloop.IOLoop.instance')
@patch('repository.app.koi.make_server')
@patch('repository.app.koi.load_config')
def test_main_starts_process_with_config(load_config, make_server, instance,
                                         options, audit):
    server = make_server.return_value
    options.processes = 999

    repository.app.main()
    server.start.assert_called_once_with(options.processes)


@patch('repository.app.audit')
@patch('repository.app.options')
@patch('tornado.ioloop.IOLoop.instance')
@patch('repository.app.koi.make_application')
@patch('repository.app.koi.make_server')
@patch('repository.app.koi.load_config')
def test_main_starts_an_instance(load_config, make_server, make_application,
                                 instance, options, audit):
    repository.app.main()
    assert instance().start.call_count == 1
