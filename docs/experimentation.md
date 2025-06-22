---
title: "Experimentation"
linkTitle: "Experimentation"
weight: 2
description: >
  Building experiments on a MergeTB testbed
---


Here we cover the core concepts in the experimentation workflow supported by
Merge.

## Expression

Expressing an experiment is the first step in creating an experiment. We
encourage a workflow that starts with programmatic expression and works in
analysis, visualization and reticulation tools along the way. This workflow
allows you to focus on the core expression of your experiment and call on tools
to sanity check, ensure correctness and dynamically generate subsystems or
preserve experiment characteristics as needed.

To make things concrete let's start with a simple example. Two local area
networks (LAN) interconnected by a router.

```python
from mergexp import *

# create a network topology and call it dumbbell
net = Network('dumbbell')

# create network devices (nodes) for two lans 'a' and 'b'
a = [net.node(name) for name in ['a0', 'a1', 'a2']]
b = [net.node(name) for name in ['b0', 'b1']]

# create a router
r = net.node('r')

# create the 'a' and 'b' LANs with the router as a common node
net.connect(a + [r])
net.connect(b + [r])

experiment(net)
```

This code is relatively straightforward. However, it's not immediately apparent that the topology we
have coded up represents the connectivity model we have in mind. To this end, the Merge portal
provides <!--[visualization capabilities](/docs/web/#materialization-walk-through) --> visualization
capabilities. The portal web interface can render experiment topologies with the click of a button.
The code above results in the following visualization.

![](/img/concepts/dumbbell.png)

This visualization confirms that the topology we have coded up conforms to our
intent. The visualization capabilities of the portal provide many other useful
features including being able to selectively color and group nodes - which can
be very useful for sanity checking topology code.

## Constraints

The example in the previous section defined a topological structure for an
experiment. However, it did not specify any characteristics for the nodes in the
topology or the links that interconnect them. The validity of experiments often
depends on the capabilities of nodes and links in an experiment. Consider for
example an experiment whose purpose is to demonstrate a new routing algorithm
that is meant to run on embedded or IoT hardware. Using server grade nodes
for the experiment does no one any good. Furthermore it's important for
experiment reproducibility to specify the domain of validity for experiment
elements. By default, the Merge allocation systems will use the most abundant
resources it can find with the highest degree of locality. If we run our
experiment as above, without constraints - and someone else comes along to try
and reproduce it, they may get completely different resources allocated and thus
get different results.

To address both the experiment validity and reproducibility problems, Merge has
a notion of constraints that can be applied to nodes and links in an experiment.
Consider the following augmented version of our previous experiment.

```python
from mergexp import *

# create a topology and call it dumbbell
net = Network('dumbbell')

# create devices for two lans 'a' and 'b'
a = [net.node(name, memory.capacity == gb(1)) for name in ['a0', 'a1', 'a2']]
b = [net.node(name, memory.capacity == gb(2)) for name in ['b0', 'b1']]

# create a router
r = net.node('r', proc.cores == 4, memory.capacity == gb(4))

# create the 'a' and 'b' LANs with the router as a common node
net.connect(a + [r], capacity == mbps(100))
net.connect(b + [r], capacity == mbps(100))

experiment(net)
```

In this version of the experiment we have expressed what the
requirements are for the nodes and links in order for the experiment to be
valid. This also aids reproducibility in that the allocation of resources for
this experiment on any Merge testbed system, whether it's the same Portal the
experiment originated on - or an entirely different Merge testbed ecosystem with
vastly different resources the constraints enforce the same validity domain.

## Addressing and Routing

Another thing our topology is missing is addresses and some form of routing
setup. If we were to materialize this experiment as-is, we would get the
topology with the link-level topology we want. However, the nodes would not be
able to talk to each other as they would have no addresses or routing setup.

We can input this information directly into the model in several ways. The
example below extends the topology above to include routing and addressing
directives.

```python
from mergexp import *

# create a topology and call it dumbbell
net = Network('dumbbell', addressing == ipv4, routing == static)

# create devices for two lans 'a' and 'b'
a = [net.node(name, memory.capacity == gb(1)) for name in ['a0', 'a1', 'a2']]
b = [net.node(name, memory.capacity == gb(2)) for name in ['b0', 'b1']]

# create a router
r = net.device('r', proc.cores == 4, memory.capacity == gb(4))

# create the 'a' and 'b' LANs with the router as a common node
net.connect(a + [r], capacity == mbps(100))
net.connect(b + [r], capacity == mbps(100))
  
experiment(net)
```

In this example we have specified static routing and ipv4 addressing as constraints on the overall
topology. When we realize this experiment, these constraints will cause Merge to launch something
called reticulators to (1) allocate IPv4 addresses for each experiment interface, and (2) calculate
a complete set of routes for our experiment. This augmented model with addresses and routes will
then be fed to the realization and materialization steps, removing the need for the user to do
address allocation and route installation in their experiment manually.


<!--
Storage not yet implemented

## Experiment storage

We can also define filesystems where we can store experiment data and artifacts.
There is currently one type of storage (filesystems), with two types of
longevity (storage lifetime): experiment and site.  Experiment storage lives for
the duration of the experiment, and site storage lives for the lifetime of a
site.  These will be explained further in later sections, but for now, let us
look at an example of creating an experiment using storage in our experiment
description.

```python
import mergexp as mx
from mergexp.unit import gb

# create a topology named storage
net = mx.Topology('storage')

# create a definition for a filesystem (fs) storage with a 10GB quota
siteAsset = mx.Storage(kind="fs", size=gb(10), name="staticAsset")

# create three nodes: a, b, and c and connect them on a LAN
nodes = [net.device(name) for name in ['a', 'b', 'c']]
lan = net.connect(nodes)

# statically assign each node with an ip address
for i,e in enumerate(lan.endpoints, 1):
  e.ip.addrs = ['10.0.0.%d/24' % i]

# mount our filesystem on each node under /mnt directory
# mount takes 2 arguments: where to mount, and the object to mount
for node in nodes:
  node.mount("/mnt/%s" % siteAsset.name, siteAsset)

mx.experiment(net)
```

In this example we've created a 3 node experiment, with each node mounting
the storage at /mnt/staticAsset.  Each node will have access to the network
storage, creating an ideal situtation for sharing large amounts of data between
nodes.
-->

## Realization

Realization is the process calculating a minimum cost embedding of an
experiment network into the overall resource network and performing allocations
on the resources selected. The Merge realization engine operates on a localized 
abundance principal meaning that the most abundant and closest together
resources that can be found are used.

![](/img/concepts/realization.png)

A realization attempt may or may not succeed. If there are not a set of resources that satisfy the
topology and constraints in an experiment model, the realization will fail. When this happens, a
version of the experiment with relaxed constraints may need to be created to allocate sufficient
resources. If the realization does succeed, the resources are allocated for the exclusive use of
your experiment, and do not go back into the resource pool for others to use until you relinquish
the realization.

## Materialization

Once a realization has completed, an experiment instance can be materialized. Materialization is the
process in which the nodes (bare metal nodes and/or virtual machines) in the experiment are turned
on, imaged with the correct operating system and configured according to experiment specifications.
Materialization also creates the experiment network according to the links described in the topology
model.  Finally the experiment infrastructure network (infranet) is set up. The infranet consists of
a flat network that interconnects all nodes in an experiment to each other and to basic
infrastructure services including DHCP/DNS for name resolution, an experiment VPN access point, a
node configuration daemon and a node instrumentation collection service. All of these experiment
infrastructure services run as a pod of containers called an infrapod. Each materialization gets its
own dedicated infrapod.

![](/img/concepts/infranet.png)

Materializations are typically very fast (less than 1 minute) when virtualized nodes are in use, but
can take up to a few minutes to complete if bare-metal nodes are used, depending on the speed of the
hardware in the Merge facility. The Merge API provides a status endpoint to query the status of node
and link materialization that is available through the web interface and the command line client.

For any given realization there can only be one materialization at a time, as a realization
is a mapping of experiment elements to resources, so once they are materialized they cannot be
materialized again. However, you can dematerialize and re-materialize a realization as many times as
you want. This can be useful for restarting experiments from a clean slate. If you require multiple
instances of an experiment simultaneously, it's as simple as creating multiple realizations of the
same experiment. This will give you a disjoint set of resources for each realization that can be
materialized concurrently.

## Execution

Execution is the process of provisioning experiment nodes with the software systems under test,
configuring those systems and kicking off an experiment run.  In order to do this you'll need access
to the infranet of your experiment from a place that has everything needed to provision, configure
and run your experiment. To this end the Merge portal features a capability called experiment
development containers (XDC). These are Linux containers that can be launched on demand, are
remotely accessible and can be attached to the infranet of your experiment.

![](/img/concepts/xdc.png)

XDCs are accessible through a jump host on the Merge portal. The address will vary depending on the
portal you are using. There is a special `attach` command that is used to attach the XDC to the
infranet of an experiment. Once attached you can access nodes in the experiment by name. This
provides the connectivity needed for provisioning, configuration and experiment orchestration. For a
complete example on automating a simple experiment execution see our [experiment automation
guide](/docs/experimentation/experiment-automation).

## Getting Started

The following set of links will help guide you through the process of creating
Merge experiments.

<!--- [Beginner Walk-through via the Web Interface](/docs/web):
  The complete experimentation using the web interface.
-->
- [Getting Started](/docs/experimentation/getting-started)
  Download the Merge CLI and/or navigate to the graphical interface on the web.
- [Hello World](/docs/experimentation/hello-world):
  End-to-end walkthrough of building an experiment, realizing it, and materializing it on a Merge
  testbed.
- [Managing Experiments through the CLI](/docs/experimentation/cli-reference):
  A guided tour of using the command line interface to interact with merge.
- [Experiment Automation Guide](/docs/experimentation/experiment-automation):
  How to automate experiment scenarios once an experiment has been materialized.
