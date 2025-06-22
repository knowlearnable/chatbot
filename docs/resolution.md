---
title: "Node Resolution and Naming"
linkTitle: "Node Resolution and Naming"
weight: 7
description: >
    Using and configuring node resolution services
---

## tl;dr

The following table demonstrates how names resolve to addresses in Merge testbeds:
| Name | Type | Resolution |
| ---- | ---- | ---------- |
| `[name].exp.[realization].[experiment].[project]` | Experiment FQDN | Resolves to experiment network address of [name] |
| `[name].exp` | Experiment qualified short name | Resolves to experiment network address of [name]
| `[name]` | Short name | Resolves to experiment network address of [name]
| `[name].infra.[realization].[experiment].[project]` | Infranet FQDN| Resolves to infranet address of [name] |
| `[name].infra` | Infranet qualified short name | Resolves to infranet address of [name] |

For example, assume a node `a` from materialization `line.hello.murphy`, with experiment address
`10.0.0.1/24` and infranet address `172.30.0.11/16`:
| Name | Address |
| ---- | ------- |
| `a.exp.line.hello.murphy` | `10.0.0.1` |
| `a.exp` | `10.0.0.1` |
| `a` | `10.0.0.1` |
| `a.infra.line.hello.murphy` | `172.30.0.11` |
| `a.infra` | `172.30.0.11` |


## Fundamentals of Merge Networks

Each materialization has 2 completely separate networks: (1) the "experiment network" (aka, "xpnet")
which is configured based on the [experiment model](../model-ref/), and (2) a dedicated control or
"infrastructure network" (aka, "infranet"). Each xpnet has the layer 2 topology described by the user
model. Conversely, the infranet is created automatically by Merge. Every node in the materialization
has a dedicated network interface card with an IP address on the infranet which allows all nodes to
communicate directly through the infranet.

The infranet provides a variety of network services for each experiment. These include:
- DHCP: each node in your materialization receives its infranet IP address via DHCP
- DNS: each node has DNS entries registered through a nameserver that allow for name based network access
- VPN: each node can be accessed from the Merge portal via SSH traffic which is passed through a VPN tunnel
- External gateway: the infranet is your route to reaching the Internet. Each node has its default
  route set to the infranet gateway (typically 172.30.0.1), which masquerades and forwards traffic
  through the testbed facility's public IP address.

![](/img/concepts/infranet.png)

The image above showcases the network architecture for an example materialization. Each experiment node
has a set of solid lines depicting connectivity on the xpnet and a single dotted line showing
connectivity to the infranet. The aforementioned network services are deployed in a
per-materialization container pod called the "infrapod" which is accessible through the infranet.

In addition to these services, because it is an isolated control plane, the infranet is often used
to configure machines, either by SSHing to them and running scripts or using advanced tools like
[Ansible](../experiment-automation). Using the infranet this way prevents control traffic from
transiting the xpnet, which could introduce interference or anomalies to your experiment workloads.

## Resolution

Merge provides a DNS server for each materialization. Merge always registers DNS entries for
infranet addresses. By default, it also registers entries for any known experiment network
addresses.

Assume an experiment model as follows:
```python
from mergexp import *

net = Network('hello', routing == static)
a = net.node('a')
r = net.node('r')
b = net.node('b')

link0 = net.connect([a, r])
link1 = net.connect([b, r])

link0[a].socket.addrs = ip4('10.0.0.1/24')
link0[r].socket.addrs = ip4('10.0.0.2/24')
link1[r].socket.addrs = ip4('10.0.1.2/24')
link1[b].socket.addrs = ip4('10.0.1.1/24')

experiment(net)
```

This simple model defines 2 nodes "a" and "b" connected by a router "r" with IPv4 addresses manually
assigned to each link.

Assume that the above experiment model has been compiled, realized, and materialized on a testbed
with the materialization ID: `line.hello.murphy` (i.e., realization name: `line`, experiment: `hello`, project: `murphy`).The fully qualified materialization name `line.hello.murphy` is also referred to as the materialization ID, or "mzid" for short.
Furthermore, assume that Merge has allocated infranet addresses as follows:
| Node | Infranet Address |
| ---- | ---------------- |
| `a` | `172.30.0.11/16` |
| `r` | `172.30.0.12/16` |
| `b` | `172.30.0.13/16` |

### DNS Entries

In this example, Merge registers DNS entries for each node in your experiment as follows:

| Name | Address |
| ---- | ------- |
| `a.exp.line.hello.murphy` | `10.0.0.1` |
| `r.exp.line.hello.murphy` | `10.0.0.2` |
| `b.exp.line.hello.murphy` | `10.0.1.1` |
| `a.infra.line.hello.murphy` | `172.30.0.11` |
| `r.infra.line.hello.murphy` | `172.30.0.12` |
| `b.infra.line.hello.murphy` | `172.30.0.13` |

As the table shows, names for both the experiment network and infranet are registered in the DNS
server for the materialization. Commands that reference nodes via either of their fully qualified
domain names will resolve to the appropriate address.

### Search Domains

The above indicates the presence of subdomains in the experiment. Indeed, when Merge assigns
infranet addresses via DHCP, the DHCP advertises network search domains so that local experiment
node resolvers query subdomains when attempting node resolutions. By default, these are:

| Search Domain | Example |
| ------------- | ------- |
| `exp.<mzid>` | `exp.line.hello.murphy` |
| `<mzid>` | `line.hello.murphy`


### Shortnames

Based on the above DNS entries and search domains, users can access their nodes via "short names"
simply by using the names specified in the model (i.e., "a" "r" or "b" in our example). When
attempting to access nodes like this, the local machine's resolver will prepend the name to a search
domain and send a DNS query to the nameserver. For example, consider the command:
```shell
murphy@a:~$ ping -c 1 b
PING b.exp.line.hello.murphy (10.0.1.1) 56(84) bytes of data.
64 bytes from 10.0.1.1 (10.0.1.1): icmp_seq=1 ttl=64 time=0.730 ms

--- b.exp.line.hello.murphy ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.730/0.730/0.730/0.000 ms
```

The local machine "a" will send a DNS query with the short name "b" prepended to the first search
domain, `exp.line.hello.murphy`. This will return a record for `10.0.1.1/24`, and so the resolution is
complete.

If, instead, the user wanted to reach node "b" on the infranet, they could
type:
```shell
murphy@a:~$ ping -c 1 b.infra
PING b.infra.line.hello.murphy (172.30.0.13) 56(84) bytes of data.
64 bytes from 172.30.0.13 (172.30.0.13): icmp_seq=1 ttl=64 time=0.367 ms

--- b.infra.line.hello.murphy ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.367/0.367/0.367/0.000 ms
```

The local machine will first send a DNS query for `b.infra.exp.line.hello.murphy`. Because there is no
record for this name, the DNS server will return no record. The local resolver will then send a
query on the next search domain, with the name prepended as `b.infra.line.hello.murphy`. This will
return a record for `172.30.0.13/16`, and so the resolution is complete.

{{% alert title="Note" color="info" %}}
Infranet addresses cannot be manually allocated and may vary from one realization of the same
experiment to another. Always use `[name].infra` to reach nodes via their infranet addresses
{{% /alert %}}


## Infranet-only Resolution

While Merge will always register infranet qualified DNS entries for each node, it is possible to
disable experiment network resolution. This may be desired, for example, for experiments that wish to
run their own manually provisioned DNS server, or run their own DHCP server and thus experiment
addresses are not known at the time the network is compiled in Merge.

To disable DNS for experiment addresses, set the [experimentnetresolution constraint](../model-ref/#network)
to `False` in your model as follows:

```python
from mergexp import *

net = Network('hello', routing == static, experimentnetresolution == False)
a = net.node('a')
r = net.node('r')
b = net.node('b')

link0 = net.connect([a, r])
link1 = net.connect([b, r])

link0[a].socket.addrs = ip4('10.0.0.1/24')
link0[r].socket.addrs = ip4('10.0.0.2/24')
link1[r].socket.addrs = ip4('10.0.1.2/24')
link1[b].socket.addrs = ip4('10.0.1.1/24')

experiment(net)
```

### DNS Entries

In this example, Merge registers DNS entries only for infranet addresses:
| Name | Address |
| ---- | ------- |
| `a.infra.line.hello.murphy` | `172.30.0.11` |
| `r.infra.line.hello.murphy` | `172.30.0.12` |
| `b.infra.line.hello.murphy` | `172.30.0.13` |

### Search Domains

Without experiment resolution, a different set of search domains are advertised:
| Search Domain | Example |
| ------------- | ------- |
| `infra.<mzid>` | `infra.line.hello.murphy` |
| `<mzid>` | `line.hello.murphy`

### Shortnames

Based on the above DNS entries and search domains, **short names now resolve to the infranet**:
```
murphy@a:~$ ping -c 1 b
PING b.infra.line.hello.murphy (172.30.0.13) 56(84) bytes of data.
64 bytes from 172.30.0.13 (172.30.0.13): icmp_seq=1 ttl=64 time=0.367 ms

--- b.infra.line.hello.murphy ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.367/0.367/0.367/0.000 ms
```

Note that because `infra.<mzid>` is also registered, the infranet qualified short name can still be
used to resolve nodes:
```shell
murphy@a:~$ ping -c 1 b.infra
PING b.infra.line.hello.murphy (172.30.0.13) 56(84) bytes of data.
64 bytes from 172.30.0.13 (172.30.0.13): icmp_seq=1 ttl=64 time=0.367 ms

--- b.infra.line.hello.murphy ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.367/0.367/0.367/0.000 ms
```

## Hostnames

Each node has its infranet qualified name set as its hostname. This is true regardless of whether or
not experiment net resolution is enabled. For example:
| Node | Hostname |
| ---- | -------- |
| `a` | `a.infra.line.hello.murphy` |
| `r` | `r.infra.line.hello.murphy` |
| `b` | `b.infra.line.hello.murphy` |

This can be seen by reading `/etc/hostname` on a machine:
```shell
murphy@a:~$ cat /etc/hostname
a.infra.line.hello.murphy
```

