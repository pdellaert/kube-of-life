# -*- coding: utf-8 -*-
# Copyright 2018, Philippe Dellaert
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, 
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DuAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""
kube-of-life
============
A Game of Life implementation that uses Kubernetes pods as cells.
"""

import argparse
import os
import threading

from kubeoflife.common import utils
from kubeoflife.backend.gameoflife import GameOfLife
from kubeoflife.frontend.api import API


class KubeOfLife(object):
    """
    Kube of Life
    """

    def __init__(self):
        """
        Handle command to start the app
        """
        utils.THREAD_CONDITION = threading.Condition()
        utils.THREAD_DATA = 0

        # Parsing arguments
        args = self.get_args()

        # Handling configuration file
        if args.config_file:
            cfg = utils.parse_config(args.config_file)
        elif os.path.isfile('{0:s}/.kube-of-life/config.ini'.format(os.path.expanduser('~'))):
            cfg = utils.parse_config('{0:s}/.kube-of-life/config.ini'.format(os.path.expanduser('~')))
        else:
            cfg = utils.default_config()

        # Handling logging
        log_dir = cfg.get('LOG', 'directory')
        log_file = cfg.get('LOG', 'file')
        log_level = cfg.get('LOG', 'level')

        if not log_level:
            log_level = 'ERROR'

        log_path = None
        if log_dir and log_file and os.path.isdir(log_dir) and os.access(log_dir, os.W_OK):
            log_path = os.path.join(log_dir, log_file)

        logger = utils.configure_logging(log_level, log_path)
        logger.debug('Logging initiated')

        # Debug output of args
        logger.debug('Arguments: {0}'.format(args))

        backend = GameOfLife(config=cfg)
        frontend = API(config=config)
        backend.start()
        frontend.start()
        backend.join()
        frontend.join()


    def get_args(self):
        """
        Parses Arguments
        """
        parser = argparse.ArgumentParser(description="Tool to roll up Nuage statistics data stored in Elasticsearch.")
        parser.add_argument(
            '-c',
            '--config-file',
            required=False,
            help='Configuration file to use, if not specified ~/.api-spec-inspector/config.ini is used.',
            dest='config_file',
            type=str
        )
        # Parsing args and returning them
        args, _ = parser.parse_known_args()
        return args

def main():
    """
    Main shell interface
    """
    KubeOfLife()
