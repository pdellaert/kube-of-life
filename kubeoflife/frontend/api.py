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
import threading
import logging
from flask import Flask, render_template, jsonify
from kubeoflife.common import utils

class API(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self)
        self.config = config

    def run(self):
        app = Flask(__name__)

        @app.route('/')
        @app.route('/index')
        def index():
            utils.THREAD_CONDITION.acquire()
            output = utils.THREAD_BASE_DATA
            utils.THREAD_CONDITION.release()
            return render_template("index.j2", output=output)

        @app.route('/json')
        def api():
            utils.THREAD_CONDITION.acquire()
            output = utils.THREAD_API_DATA
            utils.THREAD_CONDITION.release()
            return jsonify(output)
        
        @app.route('/config')
        def config():
            config = {
                "grid_size_x": self.config.get('GOL', 'size_x'),
                "grid_size_y": self.config.get('GOL', 'size_y'),
                "step_wait": self.config.get('GOL', 'wait'),
            }
            return jsonify(config)
        
        app.run(host='0.0.0.0')
