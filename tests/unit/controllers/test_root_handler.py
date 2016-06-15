# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


from mock import MagicMock, patch
from repository.controllers.root_handler import RootHandler
from repository import __version__


class PartialMockedHandler(RootHandler):
    def __init__(self):
        super(PartialMockedHandler, self).__init__(application=MagicMock(), request=MagicMock(), version=__version__)
        self.finish = MagicMock()


@patch('repository.controllers.root_handler.options')
@patch('tornado.process')
def test_get_service_status(process, options):
    options.service_id = 'repository'
    handler = PartialMockedHandler()

    # MUT
    handler.get()
    msg = {
        'status': 200,
        'data': {
            'service_name': 'Open Permissions Platform Repository Service',
            'service_id': 'repository',
            'version': '{}'.format(__version__)
        }
    }

    handler.finish.assert_called_once_with(msg)
