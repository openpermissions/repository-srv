# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Configures and starts up the Repository Service."""
import os.path

import tornado.ioloop
import tornado.httpserver
from tornado.options import options
import koi

from .controllers import (
    agreements_handler, assets_handler, capabilities_handler,
    offers_handler, sets_handler, root_handler)

from . import __version__
from . import audit


# directory containing the config files
CONF_DIR = os.path.join(os.path.dirname(__file__), '../config')

APPLICATION_URLS = [
    (r"", root_handler.RootHandler, {'version': __version__}),
    (r"/capabilities", capabilities_handler.CapabilitiesHandler),
    (r"/repositories/{repository_id}/assets/identifiers$", assets_handler.IdentifiersHandler),
    (r"/repositories/{repository_id}/assets/{entity_id}/ids$", assets_handler.AssetIDHandler),
    (r"/repositories/{repository_id}/assets$", assets_handler.AssetsHandler),
    (r"/repositories/{repository_id}/assets/{asset_id}$", assets_handler.AssetHandler),
    (r"/repositories/{repository_id}/sets/{set_id}/assets$", sets_handler.SetAssetsHandler),
    (r"/repositories/{repository_id}/sets/{set_id}/assets/{asset_id}$", sets_handler.SetAssetHandler),
    (r"/repositories/{repository_id}/sets/{set_id}$", sets_handler.SetHandler),
    (r"/repositories/{repository_id}/sets$", sets_handler.SetsHandler),
    (r"/repositories/{repository_id}/offers$", offers_handler.OffersHandler),
    (r"/repositories/{repository_id}/offers/{offer_id}$", offers_handler.OfferHandler),
    (r"/repositories/{repository_id}/agreements$", agreements_handler.AgreementsHandler),
    (r"/repositories/{repository_id}/agreements/{agreement_id}$", agreements_handler.AgreementHandler),
    (r"/repositories/{repository_id}/agreements/{agreement_id}/coverage$", agreements_handler.AgreementCoverageHandler),
    (r"/repositories/{repository_id}/search/offers$", assets_handler.BulkOfferHandler),
]


def main():
    """
    The entry point for the service.
    This will load the configuration files and start a Tornado webservice
    with one or more sub processes.

    NOTES:
    tornado.options.parse_command_line(final=True)
    Allows you to run the service with custom options.

    Examples:
        Change the logging level to debug:
            + python repository --logging=DEBUG
            + python repository --logging=debug

        Configure custom syslog server:
            + python repository --syslog_host=54.77.151.169
    """
    koi.load_config(CONF_DIR)
    app = koi.make_application(
        __version__,
        options.service_type,
        APPLICATION_URLS)
    server = koi.make_server(app)

    audit.configure_logging()

    # Forks multiple sub-processes, one for each core
    server.start(int(options.processes))

    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':  # pragma: no cover
    main()  # pragma: no cover
