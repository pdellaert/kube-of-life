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
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""
Utils
"""

import configparser
import logging
import sys
import threading

THREAD_CONDITION = threading.Condition()
THREAD_API_DATA = []
THREAD_BASE_DATA = []

def default_config():
    """
    Provides a default configuration object
    """
    cfg = configparser.ConfigParser()
    cfg.add_section('LOG')
    cfg.set('LOG', 'directory', '')
    cfg.set('LOG', 'file', '')
    cfg.set('LOG', 'level', 'DEBUG')
    cfg.add_section('GOF')
    cfg.set('GOF', 'size', '10')
    cfg.set('GOF', 'wait', '10')
    cfg.set('GOF', 'steps', '20')
    cfg.set('GOF', 'initiation', 'RANDOM')
    cfg.set('GOF', 'gridfile', '')
    cfg.set('GOF', 'randomness', '90')
    cfg.add_section('K8S')
    cfg.set('K8S', 'kubeconfig', 'YES')
    cfg.set('K8S', 'wait_for_pods', 'YES')
    return cfg

def parse_config(config_file):
    """
    Parses configuration file
    """
    cfg = configparser.ConfigParser()
    cfg.read(config_file)

    # Checking the sections of the config file
    if not cfg.has_section('LOG') or \
            not cfg.has_section('GOF') or \
            not cfg.has_section('K8S'):
        print('Missing section in the configuration file {0:s}, please check the sample configuration'.format(config_file))
        sys.exit(1)
    # Checking the LOG options
    if not cfg.has_option('LOG', 'directory') or \
            not cfg.has_option('LOG', 'file') or \
            not cfg.has_option('LOG', 'level'):
        print('Missing options in the LOG section of configuration file {0:s}, please check the configuration'.format(config_file))
        sys.exit(1)
    if not cfg.has_option('GOF', 'size') or \
            not cfg.has_option('GOF', 'wait') or \
            not (cfg.has_option('GOF', 'initiation') and cfg.get('GOF', 'initiation') in ['RANDOM', 'FILE']) or \
            not cfg.has_option('GOF', 'gridfile') or \
            not cfg.has_option('GOF', 'randomness') or \
            not cfg.has_option('GOF', 'steps'):
        print('Missing options in the GOF section of configuration file {0:s}, please check the configuration'.format(config_file))
        sys.exit(1)
    if not (cfg.has_option('K8S', 'kubeconfig') and cfg.get('K8S', 'kubeconfig') in ['YES', 'NO']) or \
            not (cfg.has_option('K8S', 'wait_for_pods') and cfg.get('K8S', 'wait_for_pods') in ['YES', 'NO']):
        print('Missing options in the LOG section of configuration file {0:s}, please check the configuration'.format(config_file))
        sys.exit(1)
    return cfg

def configure_logging(level, path, name='ASI'):
    """
    Configures the logging environment
    """
    logging.basicConfig(
        filename=path, format='%(asctime)s %(levelname)s - %(name)s - %(message)s', level=level)
    logger = logging.getLogger(name)

    return logger
