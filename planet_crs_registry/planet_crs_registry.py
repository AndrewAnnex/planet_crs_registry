# -*- coding: utf-8 -*-
# Planet CRS Registry - The coordinates reference system registry for solar bodies
# Copyright (C) 2021-2022 - CNES (Jean-Christophe Malapert for PDSSP)
#
# This file is part of Planet CRS Registry.
#
# Planet CRS Registry is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License v3  as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Planet CRS Registry is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License v3  for more details.
#
# You should have received a copy of the GNU Lesser General Public License v3
# along with Planet CRS Registry.  If not, see <https://www.gnu.org/licenses/>.
"""This module contains the library."""
import configparser
import logging.config
import os
import ssl

import uvicorn  # type: ignore
from fastapi import FastAPI

from ._version import __name_soft__
from .config import openapi_config
from .initializer import init

logger = logging.getLogger(__name__)


class PlanetCrsRegistryLib:
    """The library"""

    def __init__(self, path_to_conf: str, *args, **kwargs):
        # pylint: disable=unused-argument
        if "level" in kwargs:
            PlanetCrsRegistryLib._parse_level(kwargs["level"])
        self.__path_to_conf = os.path.abspath(path_to_conf)
        self.__dir_conf = os.path.dirname(self.__path_to_conf)
        self.__config = configparser.ConfigParser()
        self.__config.optionxform = str  # type: ignore
        logger.info(
            "Reading the configuration file from %s", self.__path_to_conf
        )
        self.__config.read(self.__path_to_conf)
        self.__app = FastAPI(
            title=openapi_config.name,
            version=openapi_config.version,
            description=openapi_config.description,
        )

    @staticmethod
    def _parse_level(level: str):
        """Parse level name and set the rigt level for the logger.
        If the level is not known, the INFO level is set

        Args:
            level (str): level name
        """
        logger_main = logging.getLogger(__name_soft__)
        if level == "INFO":
            logger_main.setLevel(logging.INFO)
        elif level == "DEBUG":
            logger_main.setLevel(logging.DEBUG)
        elif level == "WARNING":
            logger_main.setLevel(logging.WARNING)
        elif level == "ERROR":
            logger_main.setLevel(logging.ERROR)
        elif level == "CRITICAL":
            logger_main.setLevel(logging.CRITICAL)
        elif level == "TRACE":
            logger_main.setLevel(logging.TRACE)  # type: ignore # pylint: disable=no-member
        else:
            logger_main.warning(
                "Unknown level name : %s - setting level to INFO", level
            )
            logger_main.setLevel(logging.INFO)

    @property
    def config(self) -> configparser.ConfigParser:
        """The configuration file.

        :getter: Returns the configuration file
        :type: configparser.ConfigParser
        """
        return self.__config

    @property
    def path_to_conf(self) -> str:
        """The path of the configuration file.

        :getter: Returns the path of the configuration file
        :type: str
        """
        return self.__path_to_conf

    @property
    def dir_conf(self) -> str:
        """The directory of the configuration file.

        :getter: Returns the directory of the configuration file
        :type: str
        """
        return self.__dir_conf

    @property
    def app(self) -> FastAPI:
        """The fast API app.

        :getter: Returns the Fast API app
        :type: FastAPI
        """
        return self.__app

    def start_https(self):
        """Starts the https server."""
        logger.info("Starting application initialization with Https...")
        init(self.app)
        logger.info("Successfully initialized with https!")
        host: str = self.config["HTTPS"]["host"]
        port: int = int(self.__config["HTTPS"]["port"])
        ssl_keyfile: str = self.config["HTTPS"]["ssl_keyfile"]
        ssl_keyfile = (
            ssl_keyfile
            if ssl_keyfile.startswith("/")
            else os.path.join(self.dir_conf, ssl_keyfile)
        )
        ssl_certfile: str = self.config["HTTPS"]["ssl_certfile"]
        ssl_certfile = (
            ssl_certfile
            if ssl_certfile.startswith("/")
            else os.path.join(self.dir_conf, ssl_certfile)
        )
        logger.info(  # pylint: disable=W1203
            f"SSL keyfile: {os.path.abspath(ssl_keyfile)}"
        )  # pylint: disable=W1203
        logger.info(
            f"SSL certfile: {os.path.abspath(ssl_certfile)}"
        )  # pylint: disable=W1203
        try:
            uvicorn.run(
                self.app,
                host=host,
                port=port,
                ssl_version=ssl.PROTOCOL_SSLv23,
                ssl_cert_reqs=ssl.CERT_OPTIONAL,
                ssl_keyfile=ssl_keyfile,
                ssl_certfile=ssl_certfile,
            )
        except Exception as error:  # pylint: disable=W0703
            logger.error(
                f"Cannot start the Https server: {error}"
            )  # pylint: disable=W1203

    def start_http(self):
        """Starts the Http server."""
        logger.info("Starting application initialization with Http...")
        init(self.app)
        logger.info("Successfully initialized with http!")
        host: str = self.config["HTTP"]["host"]
        port: int = int(self.__config["HTTP"]["port"])
        try:
            uvicorn.run(self.app, host=host, port=port)
        except Exception as error:  # pylint: disable=W0703
            logger.error(
                f"Cannot start the Http server: {error}"
            )  # pylint: disable=W1203
