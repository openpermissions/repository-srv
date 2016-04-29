# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import pytest
from koi.test_helpers import gen_test, make_future
from mock import patch, Mock

from repository.models.framework.helper import ValidationException
from repository.models.policy import Policy, Set

from .util import create_mockdb

ASSET_TARGETS = [{
    'id': 'asset1',
    'type': 'http://openpermissions.org/ns/op/1.1/Asset',
    'set_id': None,
    'max_items': 1,
    'sel_required': True
}, {
    'id': 'asset2',
    'type': 'http://openpermissions.org/ns/op/1.1/Asset',
    'set_id': None,
    'max_items': 1,
    'sel_required': True
}]
SELECTOR_TARGETS = [{
    'id': 'selector1',
    'type': 'http://openpermissions.org/ns/op/1.1/AssetSelector',
    'set_id': 'set1',
    'max_items': 1,
    'sel_required': True
}, {
    'id': 'selector2',
    'type': 'http://openpermissions.org/ns/op/1.1/AssetSelector',
    'set_id': 'set2',
    'max_items': 1,
    'sel_required': True
}]

ENTITY_ID = 'entity1'
ASSETS = ['asset1', 'asset2']

asset_targets = Mock(return_value=make_future(ASSET_TARGETS))
selectors = Mock(return_value=make_future(SELECTOR_TARGETS))
DB = create_mockdb()


@patch.object(Policy, 'get_targets', return_value=make_future(ASSET_TARGETS))
@gen_test
def test_validate_assets(get_targets):
    assets = yield Policy.validate_assets(DB, ENTITY_ID, ASSETS)

    assert sorted(assets) == ASSETS
    get_targets.assert_called_once_with(DB, ENTITY_ID)


@patch.object(Policy, 'get_targets', asset_targets)
@gen_test
def test_validate_no_assets():
    assets = yield Policy.validate_assets(DB, ENTITY_ID, [])
    # have permission for assets even if didn't request them
    assert sorted(assets) == ASSETS


@patch.object(Policy, 'get_targets', Mock(return_value=make_future([])))
@gen_test
def test_validate_assets_policy_does_not_contain_targets():
    with pytest.raises(ValidationException):
        yield Policy.validate_assets(DB, ENTITY_ID, ASSETS)


@patch.object(Policy, 'get_targets', asset_targets)
@gen_test
def test_validate_target_not_requested():
    assets = yield Policy.validate_assets(DB, ENTITY_ID, ['asset1'])

    assert sorted(assets) == ['asset1', 'asset2']


@patch.object(Policy, 'get_targets', asset_targets)
@gen_test
def test_validate_target_not_requested_explicit():
    with pytest.raises(ValidationException):
        yield Policy.validate_assets(DB, ENTITY_ID, ['asset1'], explicit=True)


@patch.object(Policy, 'get_targets', asset_targets)
@gen_test
def test_validate_target_asset_not_in_policy():
    with pytest.raises(ValidationException):
        yield Policy.validate_assets(DB, ENTITY_ID, ['something'])


@patch.object(Policy, 'get_targets', asset_targets)
@gen_test
def test_validate_target_asset_not_in_policy_not_all_required():
    assets = yield Policy.validate_assets(DB, ENTITY_ID, ['something'],
                                          require_all=False)

    assert sorted(assets) == ASSETS


@patch.object(Set, 'has_element', return_value=make_future(True))
@patch.object(Policy, 'get_targets', selectors)
@gen_test
def test_validate_asset_selector(mock_has_element):
    assets = yield Policy.validate_assets(DB, ENTITY_ID, ['asset1'])

    assert assets == ['asset1']
    mock_has_element.assert_called_once_with(DB, 'set1', 'asset1')


@patch.object(Set, 'has_element', Mock(return_value=make_future(False)))
@patch.object(Policy, 'get_targets', selectors)
@gen_test
def test_validate_no_assets_within_selector():
    with pytest.raises(ValidationException):
        yield Policy.validate_assets(DB, ENTITY_ID, ['asset1'])


@patch.object(Set, 'has_element', Mock(return_value=make_future(True)))
@patch.object(Policy, 'get_targets', selectors)
@gen_test
def test_validate_selected_too_many_assets():
    with pytest.raises(ValidationException):
        yield Policy.validate_assets(DB, ENTITY_ID, ['asset1', 'asset2'])


@patch.object(Set, 'has_element', Mock(return_value=make_future(True)))
@gen_test
def test_validate_selected_multiple_assets_in_selector():
    selectors = Mock(return_value=make_future([{
        'id': 'selector1',
        'type': 'http://openpermissions.org/ns/op/1.1/AssetSelector',
        'set_id': 'set1',
        'max_items': 3,
        'sel_required': True
    }]))

    with patch.object(Policy, 'get_targets', selectors):
        assets = yield Policy.validate_assets(DB, ENTITY_ID,
                                              ['asset1', 'asset2', 'asset3'])

    assert sorted(assets) == ['asset1', 'asset2', 'asset3']


@patch.object(Set, 'has_element', Mock(return_value=make_future(True)))
@patch.object(Policy, 'get_targets', selectors)
@gen_test
def test_validate_no_assets_selected_for_selector():
    with pytest.raises(ValidationException):
        yield Policy.validate_assets(DB, ENTITY_ID, [])


@gen_test
def test_ignore_invalid_target_type():
    targets = Mock(return_value=make_future([{
        'id': 'asset1',
        'type': 'http://openpermissions.org/ns/op/1.1/Asset',
        'set_id': None,
        'max_items': 1,
        'sel_required': True
    }, {
        'id': 'asset2',
        'type': 'http://openpermissions.org/ns/op/1.1/something',
        'set_id': None,
        'max_items': 1,
        'sel_required': True
    }]))

    with patch.object(Policy, 'get_targets', targets):
        assets = yield Policy.validate_assets(DB, ENTITY_ID, ['asset1'])

    assert assets == ['asset1']


@patch.object(Set, 'has_element', return_value=make_future(False))
@gen_test
def test_no_select_required(has_element):
    targets = Mock(return_value=make_future([{
        'id': 'assetselector1',
        'type': 'http://openpermissions.org/ns/op/1.1/AssetSelector',
        'set_id': '010101202',
        'max_items': 1,
        'sel_required': False
    }
    ]))
    
    with pytest.raises(ValidationException):
        with patch.object(Policy, 'get_targets', targets):
            assets = yield Policy.validate_assets(DB, ENTITY_ID, ['asset1'])



@patch.object(Set, 'has_element', return_value=make_future(True))
@gen_test
def test_no_select_required_asset_in_set(has_element):
    targets = Mock(return_value=make_future([{
        'id': 'assetselector1',
        'type': 'http://openpermissions.org/ns/op/1.1/AssetSelector',
        'set_id': '010101202',
        'max_items': 1,
        'sel_required': False
    }
    ]))

    with patch.object(Policy, 'get_targets', targets):
        assets = yield Policy.validate_assets(DB, ENTITY_ID, ['asset1'])

    assert assets == ['assetselector1']



@patch.object(Set, 'has_element', Mock(return_value=make_future(True)))
@gen_test
def test_ignore_invalid_selector():
    targets = Mock(return_value=make_future([{
        'id': 'selector1',
        'type': 'http://openpermissions.org/ns/op/1.1/AssetSelector',
        'set_id': 'set1',
        'max_items': 1,
        'sel_required': True

    }, {
        'id': 'asset2',
        'type': 'http://openpermissions.org/ns/op/1.1/AssetSelector',
        'set_id': None,
        'max_items': 1,
        'sel_required': True
    }]))

    with patch.object(Policy, 'get_targets', targets):
        assets = yield Policy.validate_assets(DB, ENTITY_ID, ['asset1'])

    assert assets == ['asset1']
