---
title: "Modeling"
linkTitle: "Modeling"
weight: 2
description: >
    How to model your equipment as a Merge facility
---

{{% alert title="Tip" color="info" %}}
This guide assumes a facility software stack based on Mars. See the detailed
discussion on [the design and implementation of Mars](/docs/development/facility_architecture) in
the "Development" documentation.
{{% /alert %}}

The facility model underpins the operation of nearly every aspect of the facility. The model
captures the **capabilities** of each hardware component, the **interconnectivity** of those components, and
the **roles** that those components should play in the operation of the [Mars
based](/docs/development/facility_architecture) testbed.

We will walkthrough the process of developing a fully functional model for a simple facility called
`phobos`. The [phobos facility](https://gitlab.com/mergetb/devops/vte/phobos) was developed by the
Merge team for the purposes of Merge technology development and demonstration, and is often deployed
as a virtual testbed using virtual machine and switch technologies. While the facility is
simple and small scale, its model demonstrates most of the key characteristics of the modeling
process.

<!--This section will also highlight several of the more advanced features we support for modeling
more complex facilities.-->

## Architecture Overview

![](/img/facility/connectivity.png)

We will focus on the minimal Merge `phobos` facility shown in the diagram above. This facility has 1
Operations Server (`ops`), 1 Infrastructure Server (`ifr`), 1 Storage Server (`stor`), 1 Network Emulator
(`emu`), 4 Testbed Nodes / Hypervisors (`x[0-3]`), and separate management (`mgmt`), infranet
(`infra`) and xpnet (`xp`) switches. We highlight several notable characteristics:
- Every server node as well as the `infra` and `xp` switches are connected to the `mgmt` switch
- Every server except for `ops` is connected to the `infra` switch
- `emu` and the nodes `x[0-3]` are connected to the `xp` switch
- `ifr` has an external gateway link to the public Internet 

## XIR

Merge facilities are modeling using a custom library called [XIR](https://gitlab.com/mergetb/xir)
(eXperiment Intermediate model Representation). Models are expressed in the XIR format and
constructed using the [XIR testbed build
library](https://gitlab.com/mergetb/xir/-/tree/main/v0.3/go/build).

## Model Walkthrough

We will now build the facility model in a Go program one step at a time.  If you like, you can jump
ahead and see the [full model in the phobos
repository](https://gitlab.com/mergetb/devops/vte/phobos/-/blob/main/model/topo.go).

We begin with our imports:

### Imports

```go
import (
    "log"

	xir "gitlab.com/mergetb/xir/v0.3/go"
	. "gitlab.com/mergetb/xir/v0.3/go/build"
)
    
```

The "." import tells the go build system to import everything from the "build" library in the XIR
project, which provides a set of convenience functions that ease the modeling of facility resources.
The "xir" import imports the core XIR library itself.

### Builder

The first part of modeling a testbed facility is initializing the builder object:
```go
tb, err := NewBuilder(
	"phobos",
	"phobos.example.com",
	Underlay{
		Subnet:   "10.99.0.0/24",
		AsnBegin: 4200000000,
	},
	Underlay{
		Subnet:   "10.99.1.0/24",
		AsnBegin: 4210000000,
	},
) 
```

In this example we are providing:
- The name of the facility: `"phobos"`
- The fully qualified domain name (FQDN) of the facility: `"phobos.example.com"`
- A pair of BGP underlay subnets and autonomous system numbers (ANSs), one for the facility the
  infranet, and one for the xpnet

### Infrastructure Server

Next we model the Infrastructure Server. The helper function for this and the entities that proceed it
follow a similar format: the first argument is the **name** of the resource, followed by a set of
**hardware characteristics**, followed by a set of **roles** that the resource plays in the
facility. It is also critical to specify the MAC addresses for network interface cards as the
testbed software will identify links based on these addresses:

```go
ifr := tb.Infraserver("ifr",
	Ens(1, Gbps(1), Mgmt()),
	Ens(1, Gbps(1), Infranet()),
	Ens(1, Gbps(1), Gw()),
	Disks(1, Sata3(), SysDisk()),
	Disks(1, Sata3(), EtcdDisk()),
	Disks(1, Sata3(), MinioDisk()),
	RoleAdd(xir.Role_BorderGateway),
	RoleAdd(xir.Role_Gateway),
	RoleAdd(xir.Role_InfrapodServer),
	Raven("172.22.0.1"),
	Product("Qemu", "Infrapod Server", ""),
)
ifr.NICs[0].Ports[0].Mac = "04:70:00:00:00:04"
ifr.NICs[1].Ports[0].Mac = "04:71:00:00:00:04"
ifr.NICs[2].Ports[0].Mac = "04:72:00:00:00:04"
```

Let's go through these options one-by-one:
```go
Ens(1, Gbps(1), Mgmt())
Ens(1, Gbps(1), Infranet())
Ens(1, Gbps(1), Gw())
```
- *Ens(count, modifiers ...)* declares a network interface card (NIC) with *count* ports. The name "Ens" refers to "scheme 2" in the [consistent network device naming scheme](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/configuring_and_managing_networking/consistent-network-interface-device-naming_configuring-and-managing-networking). The builder library keeps track of how many NICs of a certain type have been created and names them according to the convention; that is, these lines declare NICs named `ens1`, `ens2`, and `ens3`
    - Each NIC is declared as having a 1 Gbps port
    - Each NIC has a different role. The first serves as the management link for the server, the second as the infranet link, and the third as the external gateway link

```go
Disks(1, Sata3(), SysDisk())
Disks(1, Sata3(), EtcdDisk())
Disks(1, Sata3(), MinioDisk())
```
- *Disks(count, modifiers ...)* declares *count* disks for the machine. Each of these disks have SATA 3 adapters. As in the NICs example, the disks serve different roles in the testbed:
    - SysDisk(): the disk will be used to store the operating system and system libraries for the machine
    - EtcdDisk(): the disk will be used to store the [etcd](https://etcd.io) database
    - MinioDisk(): the disk will be used to store the [MinIO](https://min.io) database

```go
RoleAdd(xir.Role_BorderGateway)
RoleAdd(xir.Role_Gateway)
RoleAdd(xir.Role_InfrapodServer)
```
- *RoleAdd(role)* declares that the infrapod server will serve a role in the facility.
  These roles include:
    - `xir.Role_BorderGateway`: this machine can route to external hosts outside the testbed
    - `xir.Role_Gateway`: this machine provides a gateway network for local infrapod traffic
	- `xir.Role_InfrapodServer`: this machine can host infrapods 
	- Note that these roles are added on top of the three roles that the builder library declares by
	  default for each `Infraserver` resource:
	    - `xir.Role_InfraServer`: this machine is an infrastructure server
		- `xir.Role_EtcdHost`: this machine hosts the facility's etcd database
		- `xir.Role_MinIOHost`: this machine hosts the facility's MinIO database

```go
Raven("172.22.0.1")
```
- *Raven(host)* declares that the machine can be power controlled through the [Raven](https://gitlab.com/mergetb/tech/raven) virtualization platform at IP address "172.22.0.1"
    - This only applies to hosts in a virtual testbed like `phobos`

```go
Product("Qemu", "Infrapod Server", "")
```
- *Product(Manufacturer, Model, SKU)* declares product information for the resource. This optional
  information is mainly useful for debugging and visualization purposes for tools that operate on the
  model

### Storage Server

Next we model the Storage Server. The approach mimics the infrastructure server piece, with a few
different modifiers:
```go
// Storage Server
stor := tb.StorageServer("stor",
	Ens(1, Gbps(1), Mgmt()),
	Ens(1, Gbps(1), Infranet()),
	Disks(1, Sata3(), SysDisk()),
	Disks(2, GB(20), Sata3(), RallyDisk()),
	RoleAdd(xir.Role_RallyHost),
	Raven("172.22.0.1"),
	Product("Qemu", "Storage Server", ""),
)
stor.NICs[0].Ports[0].Mac = "04:70:00:00:00:05"
stor.NICs[1].Ports[0].Mac = "04:71:00:00:00:05"
```

`stor` has two interfaces, one for the management network and one for the infranet. It has a total
of 3 disks: 1 for the system OS and libraries, and 2 20GB disks that store contents for the Merge
"Rally" service, which provides mass storage for experiment use. The node is declared as
a `xir.Role_RallyHost`.

### Network Emulator

Next comes the Network Emulator:

```go
emu := tb.NetworkEmulator("emu",
	Ens(1, Gbps(1), Mgmt()),
	Ens(1, Gbps(1), Infranet()),
	Ens(1, Gbps(1), Xpnet()),
	Disks(1, Sata3(), SysDisk()),
	Raven("172.22.0.1"),
	Product("Qemu", "Network Emulator", ""),
)
emu.NICs[0].Ports[0].Mac = "04:70:00:00:00:06"
emu.NICs[1].Ports[0].Mac = "04:71:00:00:00:06"
emu.NICs[2].Ports[0].Mac = "04:72:00:00:00:06"
```

`emu` has three network interfaces, one for each of the mgmt, infranet, and xpnets, and has a
single system disk.

### Testbed Nodes / Hypervisors

Next we come to the nodes that host user workloads, the Testbed Nodes and Hypervisors:

```go
nodes := tb.Nodes(4, "x",
	Procs(1, Cores(2)),
	Dimms(1, GB(4)),
	SSDs(2, GB(100)),
	Ens(1, Gbps(1), Mgmt()),
	Ens(1, Gbps(1), Infranet()),
	Ens(1, Gbps(1), Xpnet()),
	RoleAdd(xir.Role_Hypervisor),
	AllocModes(
		xir.AllocMode_Physical,
		xir.AllocMode_Virtual,
	),
	DefaultImage("bullseye"),
	Rootdev("/dev/sda"),
	Uefi(),
	Raven("172.22.0.1"),
	Product("Qemu", "Testbed Node", ""),
)

// mgmt MACs
nodes[0].NICs[0].Ports[0].Mac = "04:70:00:00:00:10"
nodes[1].NICs[0].Ports[0].Mac = "04:70:00:00:00:11"
nodes[2].NICs[0].Ports[0].Mac = "04:70:00:00:00:12"
nodes[3].NICs[0].Ports[0].Mac = "04:70:00:00:00:13"

// infranet MACs
nodes[0].NICs[1].Ports[0].Mac = "04:71:00:00:00:10"
nodes[1].NICs[1].Ports[0].Mac = "04:71:00:00:00:11"
nodes[2].NICs[1].Ports[0].Mac = "04:71:00:00:00:12"
nodes[3].NICs[1].Ports[0].Mac = "04:71:00:00:00:13"

// xpnet MACs
nodes[0].NICs[2].Ports[0].Mac = "04:72:00:00:00:10"
nodes[1].NICs[2].Ports[0].Mac = "04:72:00:00:00:11"
nodes[2].NICs[2].Ports[0].Mac = "04:72:00:00:00:12"
nodes[3].NICs[2].Ports[0].Mac = "04:72:00:00:00:13"
```

`x[0-3]` are declared in a single call to `tb.Nodes()`. As in the previous builder functions, the
first argument to `tb.Nodes()` is the number of nodes to be declared, and the second argument is the
"prefix" to their names. The builder will automatically create names per-resource by appending a
unique ID to the prefix, thereby naming the nodes "x0", "x1", "x2" and "x3".

We see that for testbed nodes, we declare the CPU, memory, and disk configuration: 1 2-core CPU and
1 4GB DIMM, and 2 100 GB SSDs for each node. It is **necessary** to declare these resources for
testbed nodes and hypervisors, as these are used by the Merge realization engine when determining
which testbed resources have enough spare capacity to host a user materialization.

{{% alert title="Tip" color="info" %}}
Note that `tb.Nodes()` is the only place where we declare CPU and memory quantities for the resource. There is
nothing preventing you from declaring these for other resources such as infrastructure servers,
storage servers, and network emulators, and in fact it is good practice to declare everything that
you can for each resource in your facility. 

It happens that Merge currently does not need to be aware of CPU and memory for anything other
than testbed nodes and hypervisors, and so for clarity we omit those declarations for the other resources
in this model.
{{% /alert %}}


There are a number of additional interesting features in this declaration:
- Each of the testbed nodes has a 1 Gbps mgmt, infranet, and xpnet link
- The nodes are all declared as having `xir.Role_Hypervisor`. This role is in addition to the
  `xir.Role_TbNode` that is added by default by the `tb.Nodes()` function. These two roles allow the nodes to function as bare-metal resources or as hypervisors.
- The nodes have two different `AllocModes`: `xir.AllocMode_Physical` and `xir.AllocMode_Virtual`.
  These modes mirror the bare-metal/hypervisor roles but can be toggled by an operator to control
  how the resources are used in a live testbed. For example, a node can have `xir.Role_Hypervisor`,
  but if the `xir.AllocMode_Virtual` is disabled, that node will not be used to host virtual
  machines. More information on testbed operation will be discussed in the [Operation
  section](/docs/facility/operate)
- Each node has a default image set to Debian Bullseye (`"bullseye"`). See the list of [supported Operating
  Systems](/docs/experimentation/model-ref/#supported-operating-systems) for the values that the
  default image can take. Users can request different images in their experiment models; the default
  image is only used when a user does not request any specific image.
- Each node declares that the `/dev/sda` device should be used to host the root filesystem of
  whatever OS is booted on it.
- The nodes have UEFI boot firmware (`Uefi()`), and so should boot UEFI capable images.

### Switches

At this point, we've declared all of the "server" resources in our testbed, so all that is left
are the switches and cables. First, the switches:
```go
mgmt := tb.MgmtLeaf("mgmt",
	Eth(1, Gbps(1), Mgmt()),
	Swp(10, Gbps(1), Mgmt()),
	RoleAdd(xir.Role_Stem),
	Product("Qemu", "Mgmt Leaf", ""),
)

infra := tb.InfraLeaf("infra",
	Eth(1, Gbps(1), Mgmt()),
	Swp(7, Gbps(1), Infranet()),
	RoleAdd(xir.Role_Stem),
	Product("Qemu", "Infra Leaf", ""),
)
infra.NICs[0].Ports[0].Mac = "04:70:00:00:00:01"

xp := tb.XpLeaf("xp",
	Eth(1, Gbps(1), Mgmt()),
	Swp(5, Gbps(1), Xpnet()),
	RoleAdd(xir.Role_Stem),
	Product("Qemu", "Xp Leaf", ""),
)
xp.NICs[0].Ports[0].Mac = "04:70:00:00:00:02"
```

{{% alert title="Tip" color="info" %}}
Unlike for server assets, MAC addresses of switch ports are generally not needed by Merge software.
The one exception for this is for the management ports on the infranet and xpnet switches, which are
needed to allow those switches to receive IP addresses via DHCP on the management network
{{% /alert %}}

`mgmt`, `infra`, and `xp` are each defined as leaf switches on the management, infranet, and xpnet
networks respectively. The switch declarations follow a similar pattern: an Ethernet-named
management port, followed by a number of switch ports. The `mgmt` ports are declared as management
ports, the `infra` ports are declared as infranet ports, and the `xp` ports are declared as xpnet
ports.

Lastly, we note that each switch is declared with `xir.Role_Stem`. The "stem" role indicates that a
switch is VXLAN-capable and thus can provision virtual tunnel endpoints (VTEPs) to implement the
Merge network embedding process. Merge is capable of operating with non-VXLAN capable switches,
for example by using VLAN trunking mechanisms in lieu of VTEPs, but this leads to reduced efficiency
and testbed capacity, so `xir.Role_Stem` should always be set on switches that support VXLAN.

### Cabling

The final step is to declare the cabling:
```go
// mgmt connectivity
swps := mgmt.NICs[1].Ports 
tb.Connect(swps[0], infra.NextEth())
tb.Connect(swps[1], xp.NextEth())
// swps[2] is connected to Ops server, not modeled
tb.Connect(swps[3], ifr.NextEns())
tb.Connect(swps[4], stor.NextEns())
tb.Connect(swps[5], emu.NextEns())
for idx, x := range nodes {
	tb.Connect(swps[6 + idx], x.NextEns())
}

// infra connectivity
tb.Connect(infra.NextSwp(), ifr.NextEns())
tb.Connect(infra.NextSwp(), stor.NextEns())
tb.Connect(infra.NextSwp(), emu.NextEns())
for _, x := range nodes {
	tb.Connect(infra.NextSwp(), x.NextEns())
}

// xp connectivity
tb.Connect(xp.NextSwp(), emu.NextEns())
for _, x := range nodes {
	tb.Connect(xp.NextSwp(), x.NextEns())
}
```

The builder library provides a convenience function `tb.Connect()` that declares a connection
between the two ports passed as arguments. The `infra` and `xp` blocks show an additional family of
convenience functions `NextSwp()`/`NextEns()`, which resolve to the lowest numbered NIC/port of a
given type that is not connected to anything. Repeated calls to this function in calls to
`tb.Connect()` thus resolve to sequentially increasing ports -- e.g., `swp1, swp2, swp3 ...`, and
`ens1, ens2, ens3 ...`.

For the management switch we instead directly index into the NIC object for the switch ports. This
is done because one of the switch ports (`mgmt.NICs[1].Ports[2]`; aka, `swp3`) is connected to the
operations server which is not modeled in the facility model.

### Building an XIR Facility

The purpose of the builder is to construct an XIR `Facility` object. As such, the entire set of
routines should be wrapped in a function that returns the object:
```go
func Topo() *xir.Facility {
	tb, err := NewBuilder(...)
	// construct resources ...
	return tb.Facility()
}
```

## Verifying the Model

At this point we have a library function that produces an XIR based model of a facility that can be
consumed by other testbed software. To turn this into an executable program with a number of useful
functions such as producing cabling specifications, lists of materials and JSON formatted
specifications, consider the [following simple
program](https://gitlab.com/mergetb/devops/vte/phobos/-/blob/main/model/cmd/main.go):
```go
package main

import (
    "gitlab.com/mergetb/devops/vte/phobos/model"
	"gitlab.com/mergetb/xir/v0.3/go/build"
)

func main() {
	build.Run(phobos.Topo())
}
```

### Compiling

Set up a Go module and import the model we built:
```shell
mkdir model
cd model
curl -OL https://gitlab.com/mergetb/devops/vte/phobos/-/raw/main/model/cmd/main.go
go mod init main
go mod tidy
```

Compile the program:
```shell
go build -o phobos main.go
```

And now run it:
```
$ ./phobos
Testbed CAD utility

Usage:
  phobos [command]

Available Commands:
  help        Help about any command
  list        List items in the model
  lom         List of materials
  save        Save the testbed model to XIR
  server      Run model server
  spec        Generate specs

Flags:
  -h, --help   help for phobos

Use "phobos [command] --help" for more information about a command.
```

### Verifying Cabling

The CAD utility provides a number of useful functions. For example, to verify the cabling
specification matches what we expect for our phobos facility: 
```
./phobos spec cabling
[Qemu Infrapod Server] ifr:
  ens1: mgmt.swp4
  ens2: infra.swp1
[Qemu Storage Server] stor:
  ens1: mgmt.swp5
  ens2: infra.swp2
[Qemu Network Emulator] emu:
  ens1: mgmt.swp6
  ens2: infra.swp3
  ens3: xp.swp1
[Qemu Testbed Node] x0:
  ens1: mgmt.swp7
  ens2: infra.swp4
  ens3: xp.swp2
[Qemu Testbed Node] x1:
  ens1: mgmt.swp8
  ens2: infra.swp5
  ens3: xp.swp3
[Qemu Testbed Node] x2:
  ens1: mgmt.swp9
  ens2: infra.swp6
  ens3: xp.swp4
[Qemu Testbed Node] x3:
  ens1: mgmt.swp10
  ens2: infra.swp7
  ens3: xp.swp5
[Qemu Mgmt Leaf] mgmt:
  swp1: infra.eth0
  swp2: xp.eth0
  swp4: ifr.ens1
  swp5: stor.ens1
  swp6: emu.ens1
  swp7: x0.ens1
  swp8: x1.ens1
  swp9: x2.ens1
  swp10: x3.ens1
[Qemu Infra Leaf] infra:
  eth0: mgmt.swp1
  swp1: ifr.ens2
  swp2: stor.ens2
  swp3: emu.ens2
  swp4: x0.ens2
  swp5: x1.ens2
  swp6: x2.ens2
  swp7: x3.ens2
[Qemu Xp Leaf] xp:
  eth0: mgmt.swp2
  swp1: emu.ens3
  swp2: x0.ens3
  swp3: x1.ens3
  swp4: x2.ens3
  swp5: x3.ens3
```

### Saving the Model

XIR models are serialized to a protobuf format and then typically stored in a base64 encoded file
before being fed to other Merge tools and systems that operate on it. To save the model: 
```shell
./phobos save
```

This generates a file named `phobos.xir` which has a base64 encoded XIR protobuf spec. While useful
as an exchange format for component interoperability, this is not terribly readable for a human
operator. In order to see a JSON view of the model, use the `-j` flag:
```shell
./phobos save -j
```

This generates a file named `phobos.json` which can be viewed with any text editor or JSON viewer.

## Advanced Modeling Documentation

We need something like the model ref guide that enumerates all of the XIR builder mechanisms
