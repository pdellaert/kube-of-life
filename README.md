# kube-of-life

Python tool that builds a Game of Life environment using K8s pods as cells

## Requirements

* Kubernetes environment
* kube config in your environment 
  * For VKE:
    * Step 1 - Install the `vke` CLI tool and authenticate to your cluster: https://docs.vmware.com/en/VMware-Kubernetes-Engine/services/com.vmware.kubernetesengine.getstart.doc/GUID-FF001D2D-66BC-4837-AABF-AD4F9584A8DC.html
    * Step 2 - Follow this guide to deploy the `kubectl` cli tool and to set up the kube config environment with `vke` https://docs.vmware.com/en/VMware-Kubernetes-Engine/services/com.vmware.kubernetesengine.getstart.doc/GUID-C2043E15-DBED-4C9E-8D28-F14BBA7BE13F.html

## Quick Guide

### Installation

You can install by using pip:

```
pip install git+https://github.com/pdellaert/kube-of-life
```

### Execution

You can execute the tool using the following command

```
kube-of-life -c config.ini
```

An example `config.ini` can be found in the `samples` folder in this repository.