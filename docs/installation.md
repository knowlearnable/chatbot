---
title: "Installation"
linkTitle: "Installation"
description: >
    How to install a Merge portal.
---

This document will cover the preparation steps needed for a Merge Portal
install.

The process of installing a Merge portal happens in 3 phases
- Installation of OpenShift or OKD
- Preparing OpenShift or OKD for Merge installation
- Installing merge

## OpenShift vs OKD Considerations

The Merge portal runs on either [OpenShift](https://www.openshift.com/) or
[OKD](https://www.okd.io/). You will need to install one of these onto the
cluster of servers you plan to run a Merge portal on. These projects are related
in the sense that OpenShift a commercially supported version of OKD. OKD is a
distribution of [Kubernetes](https://www.k8s.io/). **_For teams that do not have
experience running Kubernetes systems, leveraging OpenShift that comes with a
support contract and extremely high quality end user documentation and support
materials is highly recommended._**

Both OpenShift and OKD have install documentation of their own

- <a href="https://docs.okd.io/latest/installing/installing_bare_metal/installing-bare-metal.html" target="_blank">
    OKD: Installing a Cluster On Bare Metal
  </a>
- <a href="https://cloud.redhat.com/openshift/install/metal" target="_blank">
    Install OpenShift Container Platform 4: Bare Metal
  </a> (<i>requires RedHat account</i>)

The [Bare Metal Provisioning](#bare-metal-provisioning) section of this document
covers a streamlined way to install OKD using Merge provided tooling.


## Bare Metal Provisioning

This section describes how to use the [Ground Control](https://gitlab.com/mergetb/ops/ground-control)
tool to install OKD on a bare metal system.

## Kubernetes Provisioning

### Persistent Volumes

The Merge portal installer requires 5 persistent volumes to be created.

| Purpose | Minimum Size | Recommended Size | [Access Mode](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes) |
|:---|:---|:---|:---|
| [Etcd](https://www.etcd.io/) data store | 2GB | 10GB | RWO |
| MergeFS file system | 100GB | 1TB+ | RWX |
| [Kratos](https://www.ory.sh/kratos/) DB | 1GB | 10GB | RWO |
| [Git](https://git-scm.com/) | 1GB | 1TB+ | RWX |
| [MinIO](https://www.min.io/) | 10GB | 1TB+ | RWO |
| [StepCA](https://smallstep.com/docs/step-ca) | 1GB | 5GB | RWO |

Documentation for setting up persistent volumes on OKD and OpenShift can be
found at the following links.

- <a href="https://docs.okd.io/latest/storage/understanding-persistent-storage.html" target="_blank">
    OKD: Understanding Persistent Storage
  </a>
- <a href="https://docs.openshift.com/dedicated/4/storage/understanding-persistent-storage.html" target="_blank">
    OpenShift: Understanding Persistent Storage
  </a>


## Merge Portal Installation
