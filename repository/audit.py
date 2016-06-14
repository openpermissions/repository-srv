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


def log_added_set(token, set_id):
    """
    Log set added to the repository

    :param token: JWT access token used to make request
    :param set_id: the id of the set added
    """
    logger.info(u'Service {service} added set {set_id}'.format(
        service=token['sub'],
        set_id=set_id))


def log_added_assets(token, assets, repository_id=None):
    """
    Log assets added to the repository

    :param token: JWT access token used to make request
    :param assets: the data stored in the repository
    :param repository_id: the repository ID
    """
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

    if repository_id:
        msg += ' to repository {repository_id}'.format(repository_id=repository_id)

    logger.info(msg)


def log_asset_ids(token, entity_id, ids):
    def _to_unicode(i):
        return u'({})'.format(u', '.join(map(unicode, i.values())))


    logger.info(u'Service {} added asset IDs to {}: [\n\t{}\n]'.format(
        token['sub'],
        entity_id,
        u'\n\t'.join([_to_unicode(i) for i in ids])
    ))


def log_added_offer(token, offer_id):
    logger.info(u'Service {service} added offer {offer_id}'.format(
        service=token['sub'],
        offer_id=offer_id))


def log_update_offer_expiry(token, offer_id, expires):
    logger.info(u'Service {service} updated offer '
                '{offer_id} to expire at {expires}'.format(
                    service=token['sub'],
                    offer_id=offer_id,
                    expires=expires
                ))
