---
title: "Overview"
linkTitle: "Overview"
weight: 1
description: >
    So you want to operate a Merge testbed facility?
---

You've come to the right place! This page overviews the core components and network architecture of
a typical Merge facility.  Once you understand the basic design, head on over to these
pages for detailed instructions on:
- [How to model your equipment as a Merge facility](model.md)
- [How to install Merge on your facility](install.md)
- [How to operate your Merge facility](operate.md)
- [How facility networks work](networking.md)

## High Level Design

A testbed facility houses the equipment that materializes experiments. A facility
typically consists of at least the following assets:

- A set of testbed nodes that host experiment nodes. Testbed nodes either operate as
  *hypervisors* (supporting many materialization nodes concurrently through virtual machine
  technology) or as *bare-metal* machines (supporting one materialization node at a time)
- Infrastructure servers that host testbed services such as DHCP, DNS, and node imaging for
  experiment materializations
- Storage servers that host data stores for the testbed's core services as well as provide mass
  storage for experiment use 
- An operations server that functions as central point of command and control for a human operator
- A set of physical networks:
  - a "management" network through which an operator can connect to and control facility assets
  - an "infrastructure" network which supports the aforementioned services (DHCP, DNS, etc.)
  - an "experiment" network on which virtual networks for experiment materializations are embedded

## Canonical Facility Architecture

The following is a generalized view of how a Merge testbed facility is typically configured: 

![](/img/facility/overview.png)

{{% alert title="Note" color="info" %}}
The management network topology is not shown in this image. Every server, infranet, and xpnet switch
needs to be on the management network, but the architecture is not particularly important, as the
network does not transit large amounts of data and does not run any Merge services.

The operations server is also not shown in the image, as it is typically only connected to the
management network
{{% /alert %}}

### Testbed Nodes & Hypervisors

These machines host experiment nodes for materializations as described by user [experiment
models](/docs/experimentation/model-ref). Experiment nodes can either be deployed as virtual
machines on top of the Merge hypervisor stack, or can be deployed on a bare-metal server. Each
individual testbed node in the facility can alternate between bare-metal operation and hypervisor
operation throughout its lifetime. Any transitioning of modes that occurs is entirely automated by
Merge software.

### Network Emulators

These are special purpose machines that precisely control the performance characteristics of network
links in user materializations. When a user requests [precise link
emulation](/docs/experimentation/emulation) in a materialization, the embedding for that link is
done such that the link traverses a network emulation server in the facility. Currently, emulation
servers run a modified version of the [Fastclick]( https://github.com/tbarbette/fastclick) system to
control capacity, delay, and loss rates on emulated links. Because link emulation can be a resource
intensive workload, a recommended architectural model is to include a number of dedicated emulation
servers that do not host any user experiment nodes or other testbed services.

### Infrastructure Servers

Infrastructure servers host "infrapods", which are per-materialization
["pods"](https://docs.podman.io/en/latest/markdown/podman-pod.1.html) that provide services to the
materialization, including DHCP, DNS, and an experiment VPN access point for secure external
connectivity. A separate infrapod is allocated for each materialization, which means that these
services are confined to the namespace of a single materialization.

### Storage Servers

Storage servers host the etcd and MinIO data stores that support the core services of the facility,
as well as mass storage for experiment use. 

### Networks

The canonical facility architecture includes a distinct infrastructure network ("infranet") and
experiment network ("xpnet"). The infranet and xpnet serve conceptually distinct purposes and are
often deployed in entirely disjoint network fabrics, though it is possible for these networks to
share switches.

The infranet supports testbed services such as DHCP, DNS, node imaging, and mass storage. These
services support efficient testbed operation but are not designed to transit user experiment
traffic, which is instead supported by the xpnet. The xpnet is the underlying substrate over which
network links are embedded to provide the desired topological connectivity and link performance
characteristics requested by the materialization. 

{{% alert title="Note" color="info" %}}
There is no required network architecture for the infranet or xpnet. A facility operator only needs
to reflect the physical cabling and document the capabilities of each switch (e.g., whether it
supports VXLAN) in the [facility model](model.md). As long as the model reflects the physical
capabilities and connectivity accurately, Merge will figure out how to embed links to provide
infranet and xpnet connectivity to the materialization.

With that said, we recommend that infrapod servers and storage servers have high bandwidth
connectivity to the infranet, as node imaging and mass storage are bandwidth intensive services that
can easily become bottlenecked by a low bandwidth link to the infranet fabric. The image above thus
depicts these servers as being connected directly to an infranet "spine" switch. 
{{% /alert %}}

## Data Stores

Etcd
MinIO
