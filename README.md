# kube-of-life

Python tool that builds a Game of Life environment using K8s pods as cells. There's several phases to this project, each giving less control to the main code and become more and more a real containerized solution.

## The Story

Kube-of-Life is originally developed as part of the VMworld EU 2018 Hackathon, where the team wanted to implement Game of Life on top of the VMware Kubernetes Engine, where each living cell would be represented by a pod.

The goal was to work in several phases, to see where the team would end up in the limited time of the hackathon.

The story behind this is that there is a God who is experimenting with life and a set of rules on how life grows and dies. The God sets up an eco-system with some basic rules, initiates life randomly, or through a specific pattern of cells.

In the first iteration, the God decides to take full control of the eco-system, it decides to kill a cell, or to create a new cell, according to the rules.

In the second iteration, the God gives more power to life itself, it builds in more logic in life and the cells, so they actually die of starvation or overpopulation. This is building in the rules of Game of Life directly into the cells. The God decides to still remain in control of creating new life, that is to dangerous to give to mere cells.

In the third and final iteration, the God has found a stable solution for life, it decides to give control over reproduction and allows cells to create new cells. The God is now only responsible for kicking off the eco-system and watching it, death and life is now the responsibility of the cells.

* **Phase 1**
  Single God script that performces all of the functionality:
  * Builds the Game of Life grid.
  * Populates it with the cells, random or through import of a grid pattern file.
  * Manages K8s pods, one for each cell that is alive.
  * Implements the Game of Life rules and destroys or creates cells, and subsequently K8s pods, based on the Game of Life rules.
  * Implements a small web server that prints the grid and provides an API to retrieve the state.
  
  Phase 1 was implemented early November 2018 for the VMworld EU Hackathon.

* **Phase 1.5**
  Take the Phase 1 script and allow it to actually run itself as a pod on K8s, using a service account.

* **Phase 2**
  * Make each K8s cell pod itself aware of its neighbors in the grid, and decide wether or not it stays alive or dies.
  * The God pod would only be responsible of creating new cells/pods, and no longer control death.
  * God pod still provides full view of the grid and the API endpoint.

* **Phase 3**
  * Make existing K8s cell pods be responsible of creating new life cells, taking away that responsibility from the God pod.
  * The God pod now only becomes responsible for kicking of the grid and the initial life and reporting on the evolution of life

## Requirements

* Kubernetes environment
* kube config in your environment
  * For Kubernetes itself, make sure you have a working `kubectl` command on the machine this code is to be executed.
  * For VKE:
    * Step 1 - [Install the `vke` CLI tool and authenticate to your cluster](https://docs.vmware.com/en/VMware-Kubernetes-Engine/services/com.vmware.kubernetesengine.getstart.doc/GUID-FF001D2D-66BC-4837-AABF-AD4F9584A8DC.html)
    * Step 2 - [Follow this guide to deploy the `kubectl` cli tool and to set up the kube config environment with `vke`](https://docs.vmware.com/en/VMware-Kubernetes-Engine/services/com.vmware.kubernetesengine.getstart.doc/GUID-C2043E15-DBED-4C9E-8D28-F14BBA7BE13F.html)

## Quick Guide

### Installation

You can install by using pip:

```shell
pip install git+https://github.com/pdellaert/kube-of-life
```

### Execution

You can execute the tool using the following command

```shell
kube-of-life -c config.ini
```

An example `config.ini` can be found in the `samples` folder in this repository.
