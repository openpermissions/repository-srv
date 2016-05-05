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


def log(organisation_id, msg, *args, **kwargs):
    level = kwargs.pop("level", "info")
    getattr(logger, level)(msg, *args, **kwargs)


def log_added_assets(organisation_id, assets, repository_id=None, on_behalf_of=None):
    """
    Log assets added to the repository

    :param organisation_id: the client's organisation ID
    :param assets: the data stored in the repository
    :param repository_id: the repository ID
    """
    if on_behalf_of and on_behalf_of != organisation_id:
        on_behalf_of = '(on behalf of {}) '.format(on_behalf_of)
    else:
        on_behalf_of = ''

    msg = '{organisation_id} {on_behalf_of}added {count} assets'.format(
        organisation_id=organisation_id,
        count=len(assets),
        on_behalf_of=on_behalf_of)

    if repository_id:
        msg += ' to repository {repository_id}'.format(repository_id=repository_id)

    logger.info(msg)


def log_asset_ids(organisation_id, entity_id, ids):
    def _to_unicode(i):
        return u'({})'.format(u', '.join(map(unicode, i.values())))

    logger.info(u'{} added asset IDs to {}: [\n\t{}\n]'.format(
        organisation_id,
        entity_id,
        u'\n\t'.join([_to_unicode(i) for i in ids])
    ))


def log_added_offer(organisation_id, offer_id):
    logger.info(u'{} added offer {}'.format(organisation_id, offer_id))


def log_update_offer_expiry(organisation_id, offer_id, expires):
    logger.info(u'{organisation_id} updated offer '
                '{offer_id} to expire at {expires}'.format(
                    organisation_id=organisation_id,
                    offer_id=offer_id,
                    expires=expires
                ))
