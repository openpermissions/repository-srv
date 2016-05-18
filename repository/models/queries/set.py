# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


# Used in conjunction with GENERIC_LIST query.
# :param id_name: name of the variable for the id
# :returns title: Title of set
SET_LIST_EXTRA_IDS = """?title"""
SET_LIST_EXTRA_QUERY = """
    OPTIONAL {{ ?{id_name} dcterm:title ?title . }}
"""

# Template to create new serts
# :param id: internal set id
# :param class_: op:Set
# :param title: Title of set
SET_TEMPLATE = """
{id} a {class_} .
{id} dcterm:title {title} .
"""
