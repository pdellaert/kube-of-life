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
import copy
import logging
import os
import random
import threading
import time
from kubernetes import client, config
from kubeoflife.common import utils

class GameOfLife(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self)
        self.config = config
        self.old_gof_pods = [[False for i in range(int(self.config.get('GOF', 'size')))] for k in range(int(self.config.get('GOF', 'size')))]
        self.new_gof_pods = copy.deepcopy(self.old_gof_pods)

    def run(self):
        # Init
        if self.config.get('GOF', 'initiation') == 'RANDOM':
            self.randomize_grid()
        elif self.config.get('GOF', 'initiation') == 'FILE':
            self.import_grid()
        
        if self.config.get('K8S', 'kubeconfig') == 'YES':
            config.load_kube_config()
        self.create_ns()
        self.execute_k8s_actions()
        if self.config.get('K8S', 'wait_for_pods') == 'YES':
            self.wait_for_pods()
        self.set_output()

        for step in range(int(self.config.get('GOF', 'steps'))):
            time.sleep(int(self.config.get('GOF', 'wait')))
            # run game logic
            self.old_gof_pods = self.new_gof_pods.copy()
            self.new_gof_pods = [[False for i in range(int(self.config.get('GOF', 'size')))] for k in range(int(self.config.get('GOF', 'size')))]
            for i in range(len(self.new_gof_pods)):
                for j in range(len(self.new_gof_pods[i])):
                    live_neighbors = self.get_live_neighbors(x=i, y=j)
                    logging.debug("GOF - {0}x{1} has {2} neighbors".format(i, j, live_neighbors))
                    if self.old_gof_pods[i][j] and live_neighbors in [2, 3]:
                        # Normal life
                        logging.info("GOF - {0}x{1} stays alive".format(i, j))
                        self.new_gof_pods[i][j] = True
                    elif not self.old_gof_pods[i][j] and live_neighbors == 3:
                        logging.info("GOF - {0}x{1} becomes alive".format(i, j))
                        # Become alive
                        self.new_gof_pods[i][j] = True
                    elif self.old_gof_pods[i][j] and live_neighbors < 2:
                        # Dies from starvation - DEFAULT SETTING, leaving for clarity
                        logging.info("GOF - {0}x{1} dies from starvation".format(i, j))
                        self.new_gof_pods[i][j] = False 
                    elif self.old_gof_pods[i][j] and live_neighbors > 3:
                        # Dies from overpopulation - DEFAULT SETTING, leaving for clarity
                        logging.info("GOF - {0}x{1} dies from overpopulation".format(i, j))
                        self.new_gof_pods[i][j] = False
            logging.info("GOF - {0} - Configuring pods".format(step))
            self.execute_k8s_actions()
            if self.config.get('K8S', 'wait_for_pods') == 'YES':
                self.wait_for_pods()
            logging.info("GOF - {0} - Updating output".format(step))
            self.set_output()
            self.old_gof_pods = copy.deepcopy(self.new_gof_pods)

    def get_live_neighbors(self, x, y):
        live_neighbors = 0
        for i in [x-1, x, x+1]:
            if i < 0 or i >= int(self.config.get('GOF', 'size')):
                continue
            for j in [y-1, y, y+1]:
                if j < 0 or j >= int(self.config.get('GOF', 'size')):
                    continue
                elif i == x and j == y:
                    continue
                elif self.old_gof_pods[i][j]:
                    live_neighbors += 1
        return live_neighbors

    def execute_k8s_actions(self):
        logging.info("GOF - Starting K8s actions")
        for i in range(len(self.new_gof_pods)):
            for j in range(len(self.new_gof_pods[i])):
                if self.old_gof_pods[i][j] and not self.new_gof_pods[i][j]:
                    self.delete_pod(name="{0}x{1}".format(i, j))
                elif not self.old_gof_pods[i][j] and self.new_gof_pods[i][j]:
                    self.create_pod(name="{0}x{1}".format(i, j))

    def randomize_grid(self):
        for i in range(len(self.new_gof_pods)):
            for j in range(len(self.new_gof_pods[i])):
                if random.randint(0, 100) < (100-int(self.config.get("GOF", "randomness", fallback="90"))):
                    self.new_gof_pods[i][j] = True

    def import_grid(self):
        logging.debug("GOF - Checking if file {0} exists".format(self.config.get("GOF", "gridfile")))
        if self.config.get("GOF", "initiation") == "FILE" and os.path.isfile(self.config.get("GOF", "gridfile")):
            grid = []
            with open(self.config.get("GOF", "gridfile")) as inputfile:
                for line in inputfile:
                    grid.append(line)
            logging.debug("GOF - Imported grid: {0}".format(grid))
            for i in range(len(self.new_gof_pods)):
                if i >= len(grid):
                    continue
                for j in range(len(self.new_gof_pods[i])):
                    if j >= len(grid[i]):
                        continue
                    self.new_gof_pods[i][j] = True if grid[i][j] == "#" else False

    def set_output(self):
        logging.info("GOF - Handling output for Flask thread")
        output = []
        for i in range(len(self.new_gof_pods)):
            for j in range(len(self.new_gof_pods[i])):
                output.append({
                    "x": i,
                    "y": j,
                    "alive": self.new_gof_pods[i][j],
                    "color": "green" if self.new_gof_pods[i][j] else "grey"
                })
        utils.THREAD_CONDITION.acquire()
        utils.THREAD_API_DATA = output
        utils.THREAD_BASE_DATA = self.new_gof_pods
        utils.THREAD_CONDITION.notify_all()
        utils.THREAD_CONDITION.release()

    def create_ns(self):
        # Check if the game-of-life namespace exists
        namespace_client = client.CoreV1Api()
        if len(namespace_client.list_namespace(field_selector="metadata.name=game-of-life").items) == 0:
            logging.info("GOF - No game-of-life namespace, creating it")
            metadata = client.V1ObjectMeta(name="game-of-life")
            ns = client.V1Namespace(metadata=metadata)
            namespace_client.create_namespace(ns)

    def delete_ns(self):
        namespace_client = client.CoreV1Api()
        namespaces = namespace_client.list_namespace(field_selector="metadata.name=game-of-life").items
        if len(namespaces) == 1:
            logging.info("GOF - Found game-of-life namespace, deleting it")
            namespace_client.delete_namespace(name="game-of-life", body=namespaces[0])


    def create_pod(self, name):
        pod_client = client.CoreV1Api()
        if len(pod_client.list_namespaced_pod(namespace="game-of-life", field_selector="metadata.name={0:s}".format(name)).items) == 0:
            logging.info("GOF - No Pod named {0:s} found, creating it".format(name))
            container = client.V1Container(name=name, image="busybox", args=["sleep", "3600"])
            spec = client.V1PodSpec(containers=[container])
            metadata = client.V1ObjectMeta(name=name)
            pod = client.V1Pod(metadata=metadata, spec=spec)
            pod_client.create_namespaced_pod(namespace="game-of-life", body=pod)

    def delete_pod(self, name):
        pod_client = client.CoreV1Api()
        pods = pod_client.list_namespaced_pod(namespace="game-of-life", field_selector="metadata.name={0:s}".format(name)).items
        if len(pods) == 1:
            logging.info("GOF - Pod named {0:s} found, deleting it".format(name))
            pod_client.delete_namespaced_pod(namespace="game-of-life", name=name, body=pods[0], grace_period_seconds=int(round(int(self.config.get('GOF', 'wait'))/2, 0)+1))

    def wait_for_pods(self):
        pod_client = client.CoreV1Api()
        stabilized = False
        logging.info("GOF - Waiting for the pods to stabilize")
        while not stabilized:
            time.sleep(1)
            pods = pod_client.list_namespaced_pod(namespace="game-of-life").items
            running_pods = pod_client.list_namespaced_pod(namespace="game-of-life", field_selector="status.phase=Running").items
            pending_pods = pod_client.list_namespaced_pod(namespace="game-of-life", field_selector="status.phase=Pending").items
            if len(pods) == len(running_pods) and len(pending_pods) == 0:
                stabilized = True
            else:
                logging.debug("GOF - {0} pods, {1} running pods, {2} pending pods".format(len(pods), len(running_pods), len(pending_pods)))
