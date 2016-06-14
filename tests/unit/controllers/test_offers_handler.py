# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

from functools import partial
from mock import MagicMock, patch
import pytest
from koi.test_helpers import make_future
from koi.exceptions import HTTPError
from tornado.ioloop import IOLoop

from repository.controllers import offers_handler

TEST_NAMESPACE = 'c8ab01'


@patch("repository.models.offer.Offer.expired", return_value=make_future(False))
@patch("repository.controllers.offers_handler.DatabaseConnection", return_value=TEST_NAMESPACE)
def test__validate_offer_expiry(DatabaseConnection, expired):
    func = partial(
        offers_handler.OfferHandler._validate_offer_expiry,
        TEST_NAMESPACE,
        'offerid',
        '2015-01-01T00:00:00Z')
    IOLoop.current().run_sync(func)


@patch("repository.models.offer.Offer.expired", return_value=make_future(True))
@patch("repository.controllers.offers_handler.DatabaseConnection", return_value=TEST_NAMESPACE)
def test__validate_offer_expiry_expired(DatabaseConnection, expired):
    func = partial(
        offers_handler.OfferHandler._validate_offer_expiry,
        TEST_NAMESPACE,
        'offerid',
        '2015-01-01T00:00:00Z')
    with pytest.raises(HTTPError) as exc:
        IOLoop.current().run_sync(func)
    assert exc.value.status_code == 400
    assert exc.value.errors == 'Already expired'


@patch("repository.controllers.offers_handler.DatabaseConnection", return_value=TEST_NAMESPACE)
def test__validate_offer_expiry_invalid(DatabaseConnection):
    func = partial(
        offers_handler.OfferHandler._validate_offer_expiry,
        TEST_NAMESPACE,
        'offerid',
        'foobar')
    with pytest.raises(HTTPError) as exc:
        IOLoop.current().run_sync(func)
    assert exc.value.status_code == 400
    assert exc.value.errors == 'Invalid expires'


class PartialMockedOfferHandler(offers_handler.OfferHandler):
    def __init__(self):
        super(PartialMockedOfferHandler, self).__init__(application=MagicMock(), request=MagicMock())
        self.finish = MagicMock()
        self.token ={"client": { "id": "client3"}, "sub": "client1"}
        self.request.headers = {}


class PartialMockedOffersHandler(offers_handler.OffersHandler):
    def __init__(self):
        super(PartialMockedOffersHandler, self).__init__(application=MagicMock(), request=MagicMock())
        self.finish = MagicMock()
        self.token = {"client": {"id": "client3"}, "sub": "client1"}
        self.request.headers = {}


@patch("repository.controllers.offers_handler.Offer")
@patch("repository.controllers.offers_handler.DatabaseConnection", return_value=TEST_NAMESPACE)
def test_offer_handler_get(DatabaseConnection, offer):
    offer.retrieve.return_value = make_future('offer')
    handler = PartialMockedOfferHandler()
    handler.get(TEST_NAMESPACE, '0ffe31').result()
    handler.finish.assert_called_once_with({'status': 200, 'data': 'offer'})


@patch("repository.controllers.offers_handler.Offer")
@patch("repository.controllers.offers_handler.DatabaseConnection", return_value=TEST_NAMESPACE)
def test_offer_handler_get_no_offer(DatabaseConnection, offer):
    offer.retrieve.return_value = make_future(None)
    handler = PartialMockedOfferHandler()
    with pytest.raises(HTTPError) as exc:
        handler.get(TEST_NAMESPACE, '0ffe31').result()
    assert exc.value.status_code == 404


@patch("repository.controllers.offers_handler.audit")
@patch("repository.controllers.offers_handler.Offer")
@patch("repository.controllers.offers_handler.OfferHandler._validate_offer_expiry", return_value=make_future(None))
@patch("repository.controllers.offers_handler.DatabaseConnection", return_value=TEST_NAMESPACE)
def test_offers_handler_put(DatabaseConnection, _validate_offer_expiry, offer, audit):
    offer.expire.return_value = make_future(None)
    audit.log_update_offer_expiry.return_value = make_future(None)

    handler = PartialMockedOfferHandler()
    handler.request.body = '{"expires": "1999-12-31T23:59:59Z"}'
    handler.request.headers = {"Content-Type": "application/json"}

    handler.put(TEST_NAMESPACE, "0ffe31").result()

    offer.expire.assert_called_once_with(TEST_NAMESPACE, '0ffe31', '1999-12-31T23:59:59Z')
    audit.log_update_offer_expiry.assert_called_with({"client": { "id": "client3"}, "sub": "client1"}, '0ffe31', '1999-12-31T23:59:59Z')
    handler.finish.assert_called_once_with({'status': 200, 'data': {'id': '0ffe31', 'expires': '1999-12-31T23:59:59Z'}})


@patch("repository.controllers.offers_handler.audit")
@patch("repository.controllers.offers_handler.Offer")
@patch("repository.controllers.offers_handler.DatabaseConnection", return_value=TEST_NAMESPACE)
def test_offers_handler_post(DatabaseConnection, offer, audit):
    # TODO
    offer.new_offer.return_value = make_future('0ffe31')

    handler = PartialMockedOffersHandler()
    handler.request.body = '{"body": "foo"}'
    handler.request.headers = {"Content-Type": "application/ld+json"}

    handler.post(TEST_NAMESPACE).result()

    assert not offer.update.called
    assert offer.new_offer.call_count == 1
    audit.log_added_offer.assert_called_once_with({"client": { "id": "client3"}, "sub": "client1"}, '0ffe31')
    handler.finish.assert_called_once_with({'status': 200, 'data': {'id': '0ffe31'}})
