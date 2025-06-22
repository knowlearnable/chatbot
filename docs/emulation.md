---
title: "Network Emulation"
linkTitle: "Network Emulation"
weight: 6
description: >
    Using the Moa network emulation subsystem
---

## General

Merge supports link emulation support, known as the Moa subsystem.  Link
parameters are added to your model, and may be dynamically changed after the
experiment is materialized.

The following link parameters are supported:

 * capacity - specify the maximum network bandwidth the link will support
 * latency - specify the one-way packet delay of packets transmitted on a link
 * loss - specify the average packet loss for a link

Note: it is not possible to add link emulation to a link after an experiment is
materialized. All emulated links must be present in the experiment model.

## Marking Emulated Links in Your Model

In order to use network emulation on a link in your model, you need to add constraints to the link. Constraints are specified in the `.connect()`
method as additional arguments.  The supported constraints are: `capacity`, `latency` and `loss`.  For example, to create a link with a 1Mbps bandwidth and a 10ms delay, you
would put in your model:

```python
net = Network("two")
a = net.node('a')
b = net.node('b')
link = net.connect([a,b], capacity==mbps(1), latency==ms(10))
```

### Units

For link capacity, the following units are supported: `kbps`, `mbps`, `gbps`.

For link latency, the supported units are: `ns`, `ms` (millisecond), `us` (microsecond), and `s`.

For link loss, the value is a floating point number in the range `0.0-1.0`, specifying the percentage of packet loss.


## Dynamic Update of Network Emulation Parameters

### Naming Links in Your Model

Moa supports the dynamic update of network emulation parameters after an experiment is materialized.  In order for you to specify which link(s) you want to change,
links in your model can be labeled with tags, which are arbitrary strings of your choosing, which allows for grouping of multiple links to be changed at the same time.  Tags are configured by adding to the `.properties` of the link object in your model.  Multiple tags for each link are supported.

```python
link.properties["tags"] = ( "a_b", "gw", "wan" )
```

In this example, you've added three tags to the link object connecting nodes `a` and `b`, and this link may be referenced by using any one of them.

### Dyamically Updating Links

After materialization, network link emulation is updated by using the `moacmd` CLI tool available in your XDC.

```
moacmd set <tag> <property> <value> [ <property> <value> ...]
```

For example, to change the link latency on your example from above, the syntax is:
```
moacmd set a_b latency 50ms
```

Multiple properties can be set at the same time:
```
moacmd set a_b latency 50ms capacity 100mbps
```

You can display the current link emulation parameters for your materialiation with:
```
moacmd show
```
