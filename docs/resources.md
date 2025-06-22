---
title: "Resources"
linkTitle: "Resources"
weight: 3
description: >
  Modeling a collection of resources as a MergeTB facility
---

_This page covers the basic concepts involved in creating a Merge site.

## Testbed Model

Providing resources as a Merge testbed site starts by creating a model. In this
example we're going to model a simple 4 node testbed that has physically
disjoint experiment and infrastructure networks.

![](/img/concepts/tb.png)

The Golang implementation of the Merge XIR SDK contains a layered set of libraries for describing
testbed sites. From the bottom up, these layers are

| Library | Description |
|---|---|
|[hw](https://pkg.go.dev/gitlab.com/mergetb/xir/lang/go/v0.2/hw?tab=doc)| Model the hardware that comprises the testbed in detail. |
|[sys](https://pkg.go.dev/gitlab.com/mergetb/xir/lang/go/v0.2/sys?tab=doc)| Model operating system and network level configurations in terms of hardware components. |
|[tb](https://pkg.go.dev/gitlab.com/mergetb/xir/lang/go/v0.2/tb?tab=doc)| Model testbed resources in terms of system level components. Testbed resources include additional properties such as allocation mode and testbed role that determine how the Merge testbed software manages these resources. |

The code below describes the testbed topology depicted in the diagram above.

```go
package main

import (
  "gitlab.com/mergetb/xir/lang/go/v0.2/build"
  "gitlab.com/mergetb/xir/lang/go/v0.2/hw"
  "gitlab.com/mergetb/xir/lang/go/v0.2/tb"
)

func main() {
  testbed := CreateSpineleaf()
  build.Run(tb.ToXir(testbed, "spineleaf"))
}

// The structure of our testbed
type Testbed struct {
  Infraserver *tb.Resource
  XSpine      *tb.Resource
  ISpine      *tb.Resource
  ILeaf       []*tb.Resource
  XLeaf       []*tb.Resource
  Servers     []*tb.Resource
  Cables      []*hw.Cable
}

func CreateSpineleaf() *Testbed {
  // Define the components of the testbed
  t := &Testbed{
    Infraserver: tb.LargeServer("infra", "04:70:00:01:99:99", ""),
    // name, BGP address, radix, gbps
    ISpine: tb.GenericFabric(tb.InfraSwitch, tb.Spine, "ispine", "10.99.0.1", 3, 100),
    // name, BGP address, radix, gbps
    XSpine: tb.GenericFabric(tb.XpSwitch, tb.Spine, "xspine", "10.99.1.1", 7, 100),
    ILeaf: []*tb.Resource{
      // name, radix, gbps
      tb.GenericLeaf(tb.InfraSwitch, "ileaf0", 5, 100),
      tb.GenericLeaf(tb.InfraSwitch, "ileaf1", 5, 100),
    },
    XLeaf: []*tb.Resource{
      // name, radix, gbps
      tb.GenericLeaf(tb.XpSwitch, "xleaf0", 5, 100),
      tb.GenericLeaf(tb.XpSwitch, "xleaf1", 5, 100),
    },
    Servers: []*tb.Resource{
      // name, infranet mac, experiment net mac
      tb.SmallServer("n0", "04:70:00:01:70:1A", "04:70:11:01:70:1A", "*"),
      tb.MediumServer("n2", "04:70:00:01:70:1C", "04:70:11:01:70:1C", "*"),
      tb.MediumServer("n6", "04:70:00:01:70:11", "04:70:11:01:70:11", "*"),
      tb.LargeServer("n3", "04:70:00:01:70:1D", "04:70:11:01:70:1D", "*"),
    },
  }

  // Interconnect the components of the testbed

  // infraserver - ispine
  t.Cable().Connect(t.ISpine.Swp(0), t.Infraserver.Eth(0))

  // ileaf - ispine
  t.Cable().Connect(t.ISpine.Swp(1), t.ILeaf[0].Swp(4))
  t.Cable().Connect(t.ISpine.Swp(2), t.ILeaf[1].Swp(4))

  // xleaf - xspine
  t.Cable().Connect(t.XSpine.Swp(0), t.XLeaf[0].Swp(4))
  t.Cable().Connect(t.XSpine.Swp(1), t.XLeaf[1].Swp(4))

  // server - ileaf
  t.Cable().Connect(t.Servers[0].Eth(1), t.ILeaf[0].Swp(0))
  t.Cable().Connect(t.Servers[1].Eth(1), t.ILeaf[0].Swp(1))
  t.Cable().Connect(t.Servers[2].Eth(1), t.ILeaf[0].Swp(2))
  t.Cable().Connect(t.Servers[3].Eth(1), t.ILeaf[0].Swp(3))

  // server - xleaf
  t.Cable().Connect(t.Servers[0].Eth(2), t.XLeaf[0].Swp(0))
  t.Cable().Connect(t.Servers[1].Eth(2), t.XLeaf[0].Swp(1))
  t.Cable().Connect(t.Servers[2].Eth(2), t.XLeaf[0].Swp(2))
  t.Cable().Connect(t.Servers[3].Eth(2), t.XLeaf[0].Swp(3))

  return t
}

// Implement the components interface to automatically generate XIR (tb.ToXir)
func (t *Testbed) Components() ([]*tb.Resource, []*hw.Cable) {
  rs := []*tb.Resource{t.XSpine, t.ISpine, t.Infraserver}
  rs = append(rs, t.ILeaf...)
  rs = append(rs, t.XLeaf...)
  rs = append(rs, t.Servers...)

  return rs, t.Cables
}

// Describe the provisional resrouces provided by this testbed facility.

func (t *Testbed) Provisional() map[string]map[string]interface{} {
  return map[string]map[string]interface{}{
    "*": {
      "image": []string{"debian:11", "ubuntu:2004"},
    },
  }
}

// Cable creates a new cable and add it to the testbed
func (t *Testbed) Cable() *hw.Cable {
  cable := hw.GenericCable(hw.Gbps(100))
  t.Cables = append(t.Cables, cable)
  return cable
}
```

## Key Modeling Concepts

### Resources

Network testbeds are made up of interconnected nodes. In the model above we
define these nodes as Resources using the testbed modeling library. Filling in
relevant details such as name, MAC addresses and tags that link to [provisional
resources](#provisional-resources). 

This example abstracts away specific hardware details about the resources in an
effort to create a simple presentation. However, the Merge [hardware modeling
library](https://pkg.go.dev/gitlab.com/mergetb/xir/lang/go/v0.2/hw?tab=doc)
provides extensive support for modeling resources in great detail. Consider the
following example of modeling a network emulation server taken from a current
Merge testbed facility

```go

import (
	"gitlab.com/mergetb/xir/lang/go/v0.2/hw"
	"gitlab.com/mergetb/xir/lang/go/v0.2/hw/components"
	"gitlab.com/mergetb/xir/lang/go/v0.2/hw/switches"
)

func Moa1000() *hw.Device {

	i350 := components.I350DA4()
	i350.Kind = hw.Onboard

	cx4 := components.ConnectX4_2x100()
	cx4.Kind = "enp33s0f"

	lx100 := components.NetronomeLX100()
	lx100.Kind = hw.Peripheral

	d := &hw.Device{
		Base: hw.Base{
			Model:        "Moa1000",
			Manufacturer: "Silicon Mechanics",
			SKU:          "Moa1000",
		},
		Procs: []hw.Proc{
			components.Epyc7351(),
		},
		Nics: []hw.Nic{
			i350,
			cx4,
			lx100,
			lx100,
		},
	}

	for i := 0; i < 32; i++ {
		d.Memory = append(d.Memory,
			components.GenericDimm(hw.Gb(16), hw.MHz(2667), hw.DDR4))
	}

	return d

}
```

### Cables

Cables can be deceptively complex. From optical breakouts, with differing
polarity configurations, to multi-lane DAC trunks and a dizzying array of small
pluggable form factor transceivers for both copper and optics that support a
complex matrix of protocol stacks testbed cabling can get very complicated in a
hurry.

The [cable modeling
library](https://pkg.go.dev/gitlab.com/mergetb/xir@v0.2.11/lang/go/v0.2/hw/cables?tab=doc)
provides support for capturing all the details about cables that are needed to
operate a testbed facility. This library grows rather organically based on the
needs of facility operators. Contributions to this and all of the XIR libraries
are more than welcome.


### Provisional Resource Properties

Provisional resource properties are properties of resources that can be
provisioned by the testbed facility. A common example is operating system
images. OS images are not an intrinsic property of a particular resource, they
are provisioned by the testbed facility. Typically a testbed facility will have
a range of resources and a range of OS images and a compatibility matrix that
provides a relationship between the two.

Supporting provisional resources in a testbed facility is done in two parts.
First, there is a provisional resource property map that is a top level property
of the testbed model. This is a multi level property map where:

- The first level is a key defined by a property tag. In the example above we
  used `*` as all the nodes in our example reference this property set. However,
  there could be a more specific property set that only applies to a specific
  type of hardware. For example the `minnow` key could provide a set of
  provisional properties for MinnowBoard embedded computers in a testbed
  facility.

- Below the first level is a generic dictionary of properties keyed by string.
  As the example above shows, the `image` property maps onto an array of strings
  that define the available images. When users create models with OS image
  requirements, the `image` property map will be used to determine if the nodes
  in this testbed satisfy the experimental requirements of the user.

The second part is in the provisional tags carried by each resource. In the
example above, the provisional tags were supplied as the final argument to the
`SmallServer`, `MediumServer` and `LargeServer` respectively. The provisional
tags, typically referred to as `ptags` bind a resource to a provisional property
set of the testbed facility.

## Deployment

Once the testbed model has been created, it can be used to generate
configurations for every component in the testbed.

Deployment of a Merge testbed site includes the following steps.

- Deploying the testbed XIR model to infrapod nodes.
- Installing the Merge commander on infrapod nodes.
- Installing the Cogs automation system on infrapod nodes.
- Installing Canopy on switches and provisioning the base Merge configuration.
- Setting up nodes to network boot if needed.

Each of these steps is outlined in more detail below.

### Testbed model deployment

The testbed XIR model (the JSON generated from our program above) must be
installed at the path `/etc/cogs/tb-xir.json` at each infrapod server. Once the
testbed automation software is installed on these nodes, it will use the testbed
model to perform materialization operations.

### Installing the Merge commander

The Merge commander is responsible for receiving materialization commands from a
Merge portal and forwarding them to the appropriate driver. In this example, the
driver is a part of the Cogs automation software and there is only one infrapod.
In more sophisticated setups the commander may be run on a dedicated node and
load balance requests to a replicated set of drivers running across a set of
infraserver nodes.

All communication between the Merge portal and a Merge commander is encrypted
and require TLS client authentication. This means for each commander, a
certificate TLS certificate must be generated and provided to the portal. This
cert must be placed at `/etc/merge/cmdr.pem` on all servers running the
commander daemon. 