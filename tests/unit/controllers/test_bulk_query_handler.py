# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import json

from mock import MagicMock, patch
from koi.test_helpers import make_future, gen_test
from repository.controllers.assets_handler import BulkOfferHandler


class PartialMockedHandler(BulkOfferHandler):
    def __init__(self):
        super(PartialMockedHandler, self).__init__(application=MagicMock(), request=MagicMock())
        self.finish = MagicMock()
        self.client_organisation = 'testco'


@patch('repository.controllers.assets_handler.Offer')
@gen_test
def test_offer_handler_success_check_id_types(Offer):
    body = json.dumps([
        {'source_id_type': 'testcopictureid', 'source_id': '100456'},
        {'source_id_type': 'testcopictureid', 'source_id': '100123'},
        {'source_id_type': 'testcopictureid', 'source_id': '100123'},
        {'source_id_type': 'chub', 'source_id': 'hk:ASSET1'},
        {'source_id_type': 'chub', 'source_id': 'hk:ASSET1'},
        {'source_id_type': 'chub', 'source_id': 'hk:ASSET2'}
    ])
    handler = PartialMockedHandler()
    handler.request.headers = {'Content-Type': 'application/json'}
    handler.request.body = body
    repository_id = 'c8ab01'

    def mock_retrieve(source_id_list, repository_id):
        return make_future([(a['source_id_type'], a['source_id']) for a in source_id_list])

    Offer.retrieve_for_assets.side_effect = mock_retrieve
    result = [
        (u'testcopictureid', '100456'),
        (u'testcopictureid', '100123'),
        ('chub', 'hk:ASSET1'),
        ('chub', 'hk:ASSET2')
    ]

    yield handler.post(repository_id)
    handler.finish.assert_called_once_with({'status': 200, 'data': result})
