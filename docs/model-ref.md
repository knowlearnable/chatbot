---
title: "Experiment Model Reference"
linkTitle: "Experiment Model Reference"
weight: 5
description: >
  Reference guide for the Merge Experiment Model Language
---

## Overview

In Merge, the user defines experiment models in the Python language, making use
of the `mergexp` package. At a high level, an experiment model begins by
creating a network topology object, creating experiment nodes, defining how the
nodes are connected by network links, and finally, executing the model.

For example, consider a simple experiment with two nodes, `A` and `B`, which are
directly connected via a network link. The Python model could be written as:

```python
from mergexp import *

# create the network topology object
net = Network('example network')

# Create nodes and add them to the network
a = net.node('A')
b = net.node('B')

# Connect A and B
link = net.connect([a, b])

# Set IP addresses for A and B
link[a].socket.addrs = ip4('10.0.0.1/24')
link[b].socket.addrs = ip4('10.0.0.2/24')

# Execute the topology
experiment(net)
```

In real-world scenarios, the user will want to create more complex topologies,
and control some of the properties of the experiment nodes and links. These
are called _constraints_ in Merge. The available constraints for each object
type are detailed below.

## Network

The network object represents the experiment model's topology.

A network topology is created with the `Network()` constructor. The constructor
takes a string, which defines the name of the topology, and an optional set of
constraints.

```python
def Network(name, *constraints):
```

| Parameter | Type   | Description                   |
| --------- | ------ | ----------------------------- |
| name      | string | user description of the model |


Network objects can use the following constraints:

| Constraint | Possible Values | Description |
| ---------- | ----------------| ------------|
| routing  | static | automatically configure static routing on the experiment nodes |
| addressing | ipv4 | automatically assign IPv4 addresses to experiment nodes        |
| experimentnetresolution | True,False | whether Merge will resolve hostnames to experiment network addresses. If set to False, node names will resolve to *infranet* IP addresses instead  (default: True) |

{{% alert title="Tip" color="warning" %}}
When using automatic routing or addressing, specific node interfaces can be
excluded by setting a constraint of `layer==2` on the `Link` object. The
automatic modes will only consider links of layer 3 or higher.
{{% /alert %}}

{{% alert title="Example" color="info" %}}

```python
# Define a network with automatic assignment of static routes and
# ipv4 addresses to nodes
net = Network('my topology', routing==static, addressing==ipv4)
```
{{% /alert %}}

{{% alert title="Example" color="info" %}}

```python
# Define a network in which node names do *not* resolve to experiment
# network addresses, instead resolving to infranet addresses
net = Network('my topology', experimentnetresolution==False)

n = net.node("gw-router", proc.cores>=4, metal==True, memory.capacity>=gb(8))
```

Typically, the short name `gw-router` would resolve to the first experiment IP address allocated for the node.
If set as above, the short name `gw-router` will _not_ resolve to any experiment IP addresses, and
will instead resolve to the infranet IP address of the node.
{{% /alert %}}

## Nodes

A new node is created with the `Node()` constructor.

```python
def Node(name, *constraints):
```

| Parameter | Type   | Description                     |
| --------- | ------ | ------------------------------- |
| name      | string | hostname of the experiment node |

If a node in a model needs to meet some criteria, the `Node()` constructor can
be supplied with optional _constraints_ that will be used to control which
physical machine in the facility will be selected. Constraints are specified as
the constraint name, an operator (<=, ==, >=, etc), and a value.

| Name            | Type   | Units | Description                                                                                                                                                                                       |
| --------------- | ------ | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| image           | string |       | specify the OS image to boot on the node (default: `bullseye`)                                                                                                                                    |
| metal           | bool   |       | node should be not be virtualized (True) (default: False)                                                                                                                                         |
| proc.cores      | int    |       | has the specified number of processor cores (default: 1)                                                                                                                                          |
| memory.capacity | int    | bytes | require the memory size (default: 512 MB)                                                                                                                                                         |
| disk.capacity | int | bytes | require the specified disk size |

{{% alert title="Example" color="info" %}}

```python
net = Network("example topology")
n = net.node("gw-router", proc.cores>=4, metal==True, memory.capacity>=gb(8))
```

Creates a node with the hostname `gw-router` which has at least 4 processor cores, runs on bare metal (not virtualized), and has at least 8GB of main memory.
{{% /alert %}}

### Supported Operating Systems

The `image` constraint can specify one of the following values:

| Image Name | OS     | Version  |
| ---------- | ------ | -------- |
| 1804       | Ubuntu | 18.04    |
| 2004       | Ubuntu | 20.04    |
| bullseye   | Debian | bullseye |
| buster     | Debian | buster   |

{{% alert title="Example" color="info" %}}

```python
net = Network("example topology")
n = net.node("gw-router", image == "2004")
```

Creates a node with the hostname `gw-router` which runs the Ubuntu 20.04 operating system.
{{% /alert %}}

### Additional Disk Storage

Experimental VM nodes are allocated with a 32G root file system.  If additional storage is
required, `disk.capacity` constraint can be used:

```python
n = net.node("store", disk.capacity==gb(40))
```

Creates a node with the hostname `store` which has an extra virtual drive `/dev/vdb`.

This virtual drive can be formatted and mounted for storing data:

```shell
# become root
sudo bash

# format the drive and label the file system "data":
mkfs.ext4 -L data /dev/vdb

# create a directory and mount the file system:
mkdir /mnt/data
mount -L data /mnt/data

# if you want to mount it automatically after a reboot, you can add it to /etc/fstab:
echo "LABEL=data    /mnt/data       ext4        defaults        0 0" >>/etc/fstab
systemctl daemon-reload
```

{{% alert title="Tip" color="warning" %}}
All files stored on the virtual drive will disappear after the experiment is dematerialized.
If you need to keep them, please remember to copy them off the experimental node before ending
your realization.
{{% /alert %}}

### Ingresses

Nodes can host services that are accessible from outside the experiment. When a node ingress is created, the testbed 
configures a network path from the experiment node to the site's gateway, allowing external connections to route
through the testbed network to the experiment. 

Ingresses are specified in the model via the `ingress` function on a node.  See the 
[Ingresses documentation](/docs/experimentation/ingresses) for details. 

### Groups

Nodes can be categorized into _groups_, a technique which can be useful when automating experiments
using Ansible (see [Experiment Automation](/docs/experimentation/experiment-automation)). To put
nodes into groups, use a special `properties` field of the `Node` object as follows:

```python {hl_lines=[12,13,14,15]}
from mergexp import *

net = Network('example topology with groups')

a = [net.node('a%d' % i) for i in range(2)]
b = [net.node('b%d' % i) for i in range(3)]
r = net.node('router')

net.connect(a + [r])
net.connect(b + [r])

for n in a:
    n.properties['group'] = ['group_a']
for n in b:
    n.properties['group'] = ['group_b']

experiment(net)
```

Once this model has been successfully realized, you can use the CLI to generate an Ansible inventory
for the model. Assuming a materialization named `r0.groups.murphy`:

```shell
mrg nodes generate inventory r0.groups.murphy
[all]
a0
a1
b0
b1
b2
router

[group_a]
a0
a1

[group_b]
b0
b1
b2
```

## Network Links

Network links are represented by the `Link` object, and are created via the `.connect()` method on a `Network` object.
Creating the link adds it to the network topology. A `Link` is used to model both point-to-point links (2 nodes) and LANs (3 or more nodes).

```python
def connect(node_list, *constraint):
```

| Parameter | Type             | Description                            |
| --------- | ---------------- | -------------------------------------- |
| node_list | sequence of Node | two or more nodes to be interconnected |

The following constraints are defined for `Link` objects:

| Name     | Type  | Units      | Range   | Description                  |
| -------- | ----- | ---------- | ------- | ---------------------------- |
| layer    | int   | number     | 1-3     | network layer                |
| capacity | int   | bits/sec   | >0      | set the max bandwidth        |
| latency  | int   | ns         | >=0     | set the one-way packet delay |
| loss     | float | percentage | 0.0-1.0 | set the packet loss rate     |

{{% alert title="Tip" color="warning" %}}
Avoid setting constraints on links which don't require emulation, because it adds overhead to running the experiment.

The logical operation for the `capacity`, `latency` and `loss` constraints is always ignored. The constraint value is always used
as if the logical operation were equality (`==`).
{{% /alert %}}

{{% alert title="Example" color="info" %}}

```python {hl_lines=[4]}
net = Network('example topology')
a = net.node('a')
b = net.node('b')
net.connect([a, b])
```

{{% /alert %}}

### IP Addresses

IP addresses on experiment nodes are configured via the `Link` object. The
`Link` object can be dereferenced using a `Node` object, and setting the
`.socket.addrs` value, which sets the IP address for that node's interface on
the link. For convenience, the `mergexp` package provides the following utility
function:

```python
# The ip4 function takes one or more strings specifying IPv4 addresses in `address/network`
# format (see https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Network)
def ip4(*addrs):
```

{{% alert title="Example" color="info" %}}

```python {hl_lines=[5]}
net = Network('example topology')
a = net.node('a')
b = net.node('b')
link = net.connect([a, b])
link[a].socket.addrs = ip4('10.0.0.1/24')
```

{{% /alert %}}

## Constraints

Constraints are used by Merge to select physical resources that meet criteria
required by the user. Constraints are specified as a boolean relationship
between the _constraint type_ and the _constraint value_.

{{% alert title="Example" color="info" %}}

```python
metal == True
memory.capacity >= gb(8)
proc.cores > 1
```

{{% /alert %}}

{{% alert title="Tip" color="warning" %}}
When specifying a constraint with equality, always use `==` and not `=`.
{{% /alert %}}

The `mergexp` package defines many units which can be used as constraint values.

### Size

The size constraints are used to specify disk and memory requirements. The base
unit for size constraints is _bytes_. The following convenience constraint values
are defined:

```python
kb()
mb()
gb()
tb()
pb()
eb()
```

### Capacity

The capacity constraints are used to specify link bandwidth. The base unit for capacity constraints
is _bytes/sec_. The following convenience constraint values are defined:

```python
bps()
kbps()
mbps()
gbps()
tbps()
pbps()
epps()
```

### Time

The time constraint is used for setting the one-way link latency. The base unit is
_nanoseconds_. The following convenience constraint values are defined:

```python
ns()
us()
ms()
s()
```
