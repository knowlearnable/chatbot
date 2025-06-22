---
title: "Overview"
linkTitle: "Overview"
weight: 1
description: >
  Overview of the MergeTB platform
---


Merge is a testbed platform that's composed of a centralized portal that acts as
an experimentation hub for a distributed system of testbed facilities. **The basic
motivation behind the Merge architecture is to enable rapid experimentation
across vastly different types of devices and networks.** Rapid applies to
both experimenters and resource providers. Experimenters should be able to
quickly and easily express the resource requirements for their experiments,
define experiments based on those requirements - and then allocate, materialize
and execute experiments efficiently. Likewise, resource providers should be able 
to rapidly describe the resources they can provide, and build an experiment 
materialization system around those resources without having to re-invent basic 
testbed functions.

![](/img/concepts/big-picture.png)

Enabling rapid experimentation across a resource base that keeps up with the pace
of technology evolution, requires defining complexity boundaries that allow for
the incorporation of new types of devices and networks while preserving a
consistent and stable interface for experimenters and resource providers. The
first thing the Merge architecture does to address this, is separating the
experiment infrastructure problem into **_experiment space_** and **_resource
space_**. 

Experiment space contains technologies and systems that directly support
experimenters. This includes

- hosting user and project workspaces
- model development libraries for experiment expression
- experiment compilers
- resource discovery and allocation systems
- experiment visualization
- attachment points into live experiments for orchestration and device access experiment control
- APIs for experiment and project management

Resource space contains technologies and systems that directly support resource
providers. This includes a modular set of technologies that can be combined as
needed under an experiment materialization runtime to rapidly create testbed
facilities. The testbed technology stack includes subsystems critical to
operating a testbed such as 

- node imaging
- virtual network synthesis
- container based experiment service provisioning
- secure and isolated external access through experiment VPNs

The experiment space technologies come together as a **_centralized
experimentation portal_**. Experiment facilities register with a portal by
commissioning a set of resources via testbed model exchange with a Merge portal.
The portal is a turn-key open-source system that is freely available and can be
deployed by anyone interested in creating a dedicated testbed ecosystem. We
maintain a reference implementation, which currently resides at `sphere-testbed.net`. Once a portal has been
deployed and at least one testbed facility has commissioned resources, everything
needed for users to start creating experiments is ready. As more facilities
are added, more resource become available but the overall experiment development
process for users does not change.
