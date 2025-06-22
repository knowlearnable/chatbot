---
title: "Port Forwarding"
linkTitle: "Port Forwarding"
weight: 21
description: >
  Doing port fowarding on Merge testbeds
---

{{% alert title="Attention" color="warning" %}}

This guide assumes you are using the reference portal at `sphere-testbed.net`. Instructions on this page only apply to that portal.

{{% /alert %}}

# Operating System Requirements

**Linux:** No special requirements

**Mac:** No special requirements

**Windows:** No special requirements, but `mrg` command line utility works better under Linux, so it's recommended to use WSL (Windows Subsystem for Linux), which can be found from the Microsoft Store. Make sure to download Ubuntu as the distribution.

# Application Requirements

The instructions assume you have installed `mrg` utility on your home machine. To do so, please obtain the source (and follow README to compile it) or binary <a href="https://gitlab.com/mergetb/portal/cli/-/releases">from this site</a>.

The instructions also assume that you have <a href="https://mergetb.org/docs/experimentation/getting-started/#configuring-the-api-endpoint">configured your API point</a> (you only have to do this once) and have logged into your merge account by doing `mrg login yourusername -p yourpassword` (you have to do this each time you open a new terminal on your machine).

# Port Forwarding Steps

Make sure that you have realized and materialized your experiment, and that you have set it up.

To do the actual port forwarding between a port `yourport` on your machine and node `yournode` in an experiment within `yourproject` via an XDC named `yourxdc`, you need to SSH with the following command:
```
mrg xdc ssh yourxdc.yourproject -L yourport:yournode:80
```
So, to port forwarding onto 8080 with the `pathname` lab, you would type this:
```
mrg xdc ssh xdc.yourusername -L 8080:pathname:80
```

