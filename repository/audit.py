# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import logging

from koi.configure import log_formatter
from tornado.options import options

AUDIT_LOG = 'opp.audit'
logger = logging.getLogger(AUDIT_LOG)


def configure_logging():
    logger.setLevel(logging.INFO)
    handler = logging.handlers.TimedRotatingFileHandler(
        filename=getattr(options, 'audit_log_file_prefix', 'audit.log'),
        when='midnight',
        backupCount=10)
    handler.setFormatter(log_formatter())
    logger.addHandler(handler)


def log_added_set(set_id, token=None):
    """
    Log set added to the repository

    :param set_id: the id of the set added
    :param token: JWT access token used to make request

    """
    if token:
        msg = u'Service {service} added set {set_id}'.format(service=token['sub'], set_id=set_id)
    else:
        msg = u'Set {set_id} added'.format(set_id=set_id)
    logger.info(msg)


def log_added_assets(assets, token=None, repository_id=None):
    """
    Log assets added to the repository

    :param assets: the data stored in the repository
    :param token: JWT access token used to make request
    :param repository_id: the repository ID
    """
    if token:
        service = token['sub']
        original_service = token['client']['id']

        if original_service and original_service != service:
            on_behalf_of = '(on behalf of Service {}) '.format(original_service)
        else:
            on_behalf_of = ''

        msg = 'Service {service} {on_behalf_of}added {count} assets'.format(
            service=service,
            count=len(assets),
            on_behalf_of=on_behalf_of)
    else:
        msg = '{count} assets added'

    if repository_id:
        msg += ' to repository {repository_id}'.format(repository_id=repository_id)

    logger.info(msg)

def log_deleted_assets(assets, token=None, repository_id=None):
    """
    Log assets deleted from the repository

    :param assets: the data stored in the repository
    :param token: JWT access token used to make request
    :param repository_id: the repository ID
    """
    if token:
        service = token['sub']
        original_service = token['client']['id']

        if original_service and original_service != service:
            on_behalf_of = '(on behalf of Service {}) '.format(original_service)
        else:
            on_behalf_of = ''

        msg = 'Service {service} {on_behalf_of} deleted {assets}'.format(
            service=service,
            assets=assets,
            on_behalf_of=on_behalf_of)
    else:
        msg = '{count} assets deleted'

    if repository_id:
        msg += ' from repository {repository_id}'.format(repository_id=repository_id)

    logger.info(msg)

def log_asset_ids(entity_id, ids, token=None):
    def _to_unicode(i):
        return u'({})'.format(u', '.join(map(unicode, i.values())))

    if token:
        msg = u'Service {} added asset IDs to {}: [\n\t{}\n]'.format(
            token['sub'],
            entity_id,
            u'\n\t'.join([_to_unicode(i) for i in ids])
        )
    else:
        msg = u'Asset IDs added to {}: [\n\t{}\n]'.format(
            entity_id,
            u'\n\t'.join([_to_unicode(i) for i in ids])
        )
    logger.info(msg)


def log_added_offer(offer_id, token=None):
    if token:
        msg = u'Service {service} added offer {offer_id}'.format(
                    service=token['sub'],
                    offer_id=offer_id
                )
    else:
        msg = u'Offer {offer_id} added'.format(offer_id=offer_id)
    logger.info(msg)


def log_update_offer_expiry(offer_id, expires, token=None):
    if token:
        msg = u'Service {service} updated offer {offer_id} to expire at {expires}'.format(
                    service=token['sub'],
                    offer_id=offer_id,
                    expires=expires
                )
    else:
        msg = u'Offer {offer_id} updated to expire at {expires}'.format(
                    offer_id=offer_id,
                    expires=expires
                )

    logger.info(msg)
