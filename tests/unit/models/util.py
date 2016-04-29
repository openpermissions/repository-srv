# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

from mock import Mock
from koi.test_helpers import make_future

from repository.models.framework.db import DatabaseConnection

TEST_NAMESPACE = 'c8ab01'


def create_mockdb():
    db = DatabaseConnection(TEST_NAMESPACE)
    db.store = Mock()
    db.update = Mock()
    db.query = Mock()
    db.store.return_value = make_future(None)
    db.update.return_value = make_future(None)
    db.query.return_value = make_future(None)
    return db
