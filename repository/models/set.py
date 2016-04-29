# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


import uuid
import datetime
from tornado.gen import coroutine, Return
from .asset import Asset
from .framework.entity import (Entity, build_sparql_str, build_uuid_reference)
from .queries.generic import TURTLE_PREFIXES
from .queries.set import (SET_TEMPLATE,
                          SET_LIST_EXTRA_IDS,
                          SET_LIST_EXTRA_QUERY
                          )
from .queries.policy import (
    SET_CLASS,
    SET_HAS_ELEMENT
)


class Set(Asset):
    CLASS = SET_CLASS
    LIST_EXTRA_IDS = SET_LIST_EXTRA_IDS
    LIST_EXTRA_QUERY = SET_LIST_EXTRA_QUERY

    @classmethod
    @coroutine
    def new_set(cls, repository, title=None):
        if title is None:
            title = "new set created on %s" % (datetime.datetime.utcnow().isoformat(),)
        new_id = str(uuid.uuid4()).replace('-', '')
        set_ = SET_TEMPLATE.format(id="id:" + new_id,
                                   class_=cls.CLASS,
                                   title=build_sparql_str(title)
                                   )
        set_ = TURTLE_PREFIXES + set_

        if hasattr(repository, "parse"):
            yield repository.parse(data=set_, format="turtle")
        else:
            yield repository.store(set_, content_type="application/x-turtle")

        raise Return(new_id)

    @classmethod
    @coroutine
    def has_element(cls, repository, set_id, element_id):
        res = yield cls.match_attr(repository, set_id, SET_HAS_ELEMENT,
                                   value=cls.normalise_id(element_id)
                                   )
        raise Return(res)

    @classmethod
    @coroutine
    def get_elements(cls, repository, set_id, page=1, page_size=100):
        res = yield cls.get_attr(repository, set_id, SET_HAS_ELEMENT, page=page, page_size=page_size)
        raise Return(res)

    @classmethod
    @coroutine
    def set_elements(cls, repository, set_id, elements_id):
        res = yield cls.set_attr(repository, set_id, SET_HAS_ELEMENT,
                                 [cls.normalise_id(element_id) for element_id in elements_id],
                                 None
                                 )
        raise Return(res)

    @classmethod
    @coroutine
    def append_elements(cls, repository, set_id, elements_id):
        res = yield cls.append_attr(repository, set_id, SET_HAS_ELEMENT,
                                    [cls.normalise_id(element_id) for element_id in elements_id],
                                    None
                                    )
        raise Return(res)

    @classmethod
    @coroutine
    def remove_elements(cls, repository, set_id, elements_id):
        yield cls.filter_out_attr(repository, set_id, SET_HAS_ELEMENT,
                                  [cls.normalise_id(element_id) for element_id in elements_id],
                                  None
                                  )
