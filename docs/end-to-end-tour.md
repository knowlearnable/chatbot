---
title: "End to End Tour"
linkTitle: "End to End Tour"
weight: 1
description: >
    A guided tour of everything involved in creating, realizing and
    materializing an experiment on Merge.
---

## Core Concepts

To get a sense for how Merge works, and in particular how experiments are
defined, realized and materialized, we need to go over a few core architectural
features of Merge that are pervasive throughout the platform.

### Model Driven Design

At the end of the day Merge is all about models. When a resource provider
commissions a new testbed facility, they do that by providing a _model_ of the
facility to a Merge portal. When a user creates a new revision of an experiment,
they do so by pushing a commit of their experiment model to a Git repository
that is tracked by a Merge portal. When a user goes to realize an experiment,
the Merge portal takes their experiment model, takes all the models it has of
registered testbed facilities and creates an aggregate interconnected testbed
model called the _resource internet_ and then computes an embedding of the users
experiment model onto the resource internet model.

### Reconcilers

Both the Merge portal and the Mars testbed kernel are built around a reconciler
architecture. Both have well defined API and an API server. When requests are
made to the API, the API server translates a request into desired state. For
both the Portal and Mars there are a collection of reconcilers running that
monitor desired state, and drive actual state toward the target state. As a
concrete example every Merge experiment comes with a Git repository. When a user
creates a new experiment through the CLI, the `mrg` CLI tool calls the Merge
Portal API which is implemented by the portal API server. The API server
translates that new experiment request into a set of desired states. One piece
of state in that set is having a Git repository associated with the new
experiment. The API server places the parameters of that Git repository in the
Portal's etcd data store. The Git reconciler running in the portal is monitoring
etcd for state updates pertaining to Git repos. When it sees this new state it
ensures that the Git repo is present and ready to go for that users experiment.
The same process happens when an experiment is deleted, except the Git
reconciler is now observing the removal of a target state and thus removes the
associated Git repository.

## Setting Up A Testing Environment

There are two major systems to set up for running an end to end test.

1. A Merge Portal appliance.
2. A virtual Merge testbed running Mars. In this tutorial we'll be using the
   Phobos virtual testbed environment.

### Portal Appliance

The Portal appliance is a libvirt packaged virtual machine with a pre-installed
Merge portal system. It can be stood up as follows

```
curl -L https://gitlab.com/mergetb/portal/appliance/-/raw/master/launch-appliance.sh | bash
```

### Facility commissioning

The first thing we need to do on the portal is set up a facility.

Grab the latest version of the
[mrg](https://gitlab.com/mergetb/portal/cli/-/jobs/artifacts/v1-staging/raw/mrg?job=build) CLI tool.

Point `mrg` at your appliance
```
mrg config set server grpc.mergetb.example.net
```

Login using the credentials the `launch-appliance.sh` script downloaded into
your working directory.
```
pw=`cat portal-genconf* | grep opspw | awk '{print $2}'`
mrg login ops $pw --nokeys
```

{{% alert title="Note" color="info" %}}
If you get an error here like
```
ry@ryzen2 v0.7]$ mrg login ops $pw --nokeys
FATA logout: rpc error: code = Unavailable desc = connection error: desc = "transport: Error while dialing dial tcp 192.168.126.10:443: connect: connection refused"
```
This probably means that you have some pending CSRs that need to be signed.

To solve list and approve pending CSRs.
```
[root@ryzen2 v0.7]# oc get csr
NAME        AGE    SIGNERNAME                                    REQUESTOR                                                                   CONDITION
csr-xlxrs   9m2s   kubernetes.io/kube-apiserver-client-kubelet   system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
```
```
[root@ryzen2 v0.7]# oc adm certificate approve csr-xlxrs
certificatesigningrequest.certificates.k8s.io/csr-xlxrs approved
```

**You may have to do this multiple times as CSR approvals can lead to more CSR
requests**

When all the needed CSRs have been approved it will take a few moments for all
the OpenShift services to pick this up. To check OpenShift service availablity
use `oc get co`.

{{% /alert %}}

Create a user and initialize a user that represents a testbed operator.

```
mrg logout
mrg register olive olive@mergetb.org muffins1701

mrg login ops $pw --nokeys
mrg init olive
mrg activate olive
mrg logout
```

Login as the testbed operator and commission the Phobos testbed facility.

```
mrg login olive muffins1701
curl -OL https://gitlab.com/mergetb/devops/vte/phobos/-/raw/master/model/cmd/phobos.xir
mrg new fac phobos phobos.example.com phobos.xir
```

Verify you can see the new facility
```
[ry@ryzen2 v0.7]$ mrg list fac
NAME      ADDRESS               DESCRIPTION    MODE
phobos    phobos.example.com                   Public
```

Now download the comissioned version of this model.

```
rm phobos.xir
mrg show fac phobos -mx
```

This will download version of the phobos facility that has routing and
addressing information assigned to it by the portal that can be used to
initialize the Phobos virtual testbed facility.

Logout

```
mrg logout
```

More detailed instructions on the use and operation of the Merge portal
appliance are available
[here](https://gitlab.com/mergetb/portal/appliance/-/blob/master/USING.md).

### Phobos

```
rvn build
rvn deploy
rvn pingwait ops mgmt
rvn status
rvn configure
ansible-playbook -i .rvn/ansible-hosts -i ansible-interpreters bootstrap.yml
rvn reboot ifr

# !!!
# !!! Wait for ifr to provision (watch VM console)
# !!!
# !!! help-wanted: detect when ifr is ready
# !!!
```

```
eval $(rvn ssh ops)
sudo su
mrs init minio
mrs init images
```

update your testbed model with one that has been comissioned with a your portal
appliance and was downloaded in the `mrg show fac` step above.

```
mrs update model <phobos.xir>
```

In a seprate terminal **as root**
```
rvn apiserver
```

Then continue with the setup

```
# initialize the harbor
mrs init harbor


# check network status,
mrs list net

# You should be able to rest one of the nodes (say x0) and successfully enter sled.
# Bring x0 up in virt-manager, set the view mode to serial console and force reset
# the node. You should get all the way into sled on reboot.
```


More detailed instructions for setting up and running Phobos are
[here](https://gitlab.com/mergetb/devops/vte/phobos).

### Interconnection

Once the Appliance and Phobos are up, we need to make sure they can talk to each
other from the host machine.

Setup your local firewall rules to allow the Appliance and Phobos to talk

1. Lookup what interface phobos is on

```
virsh net-list
```

Locate the entry with the form `phobos_<n>_raven-infra` where `<n>` is an
integer. Display that network

```
virsh net-dumpxml phobos_<d>_raven-infra
```

this will contain an entry that looks like this
```
<bridge name='virbr<m>' stp='on' delay='0'/>
```
where `<m>` is an integer.

2. Add iptables forwarding rules.

```
sudo iptables -I FORWARD -o tt0 -i virbr<m> -j ACCEPT
sudo iptables -I FORWARD -i tt0 -o virbr<m> -j ACCEPT
```

3. Add a /etc/hosts entry on your local workstation

Look up the 172.22.x.x address on the `ops` host and add it to your workstation
`/etc/hosts` as follows.

```
172.22.x.x phobos.example.com
```

Then flush the dnsmasq cache so the portal can find phobos through libvirt dns

```
sudo killall -HUP dnsmasq
```

## Testing

Now that we have a Merge portal and Mars-based facility running virtually on our
workstation, we can begin doing things through the Merge API using the `mrg`
command line tool.

First setup your `mrg` client to point at your Portal appliance

```
mrg config set server grpc.mergetb.example.net
```

Login using the credentials from the configuration that came with the appliance.

```
pw=`cat portal-genconf* | grep opspw | awk '{print $2}'`
mrg login ops $pw --nokeys
```


### Experimentation

Create a user and initialize a user that represents a testbed user.

```
mrg logout
mrg register murphy murphy@mergetb.org muffins1701

mrg login ops $pw --nokeys
mrg init murphy
mrg activate murphy
mrg logout
```

{{% alert title="Note" color="info" %}}
To follow the hello world example linked below, You'll need to set the 
environment variable `GIT_SSL_NO_VERIFY=1` when working with git repositories
in the base portal appliance.
{{% /alert %}}


{{% alert title="Note" color="info" %}}
There are still some issues with the Git interfaces that are being tracked
[here](https://gitlab.com/mergetb/portal/services/-/issues/225). As a result you
may need to attempt to `git push` a few times as the following console log
shows.

```
[ry@ryzen2 hello-world]$ mrg whoami -t
bjETE3uBjOBgcVZqwh6DrsjftVEGUMLv
```
```
[ry@ryzen2 hello-world]$ git push
fatal: Authentication failed for 'https://git.mergetb.example.net/murphy/hello/'
```
```
[ry@ryzen2 hello-world]$ git push
Username for 'https://git.mergetb.example.net': bjETE3uBjOBgcVZqwh6DrsjftVEGUMLv
Password for 'https://bjETE3uBjOBgcVZqwh6DrsjftVEGUMLv@git.mergetb.example.net':
Enumerating objects: 10, done.
Counting objects: 100% (10/10), done.
Delta compression using up to 128 threads
Compressing objects: 100% (9/9), done.
Writing objects: 100% (10/10), 1.07 KiB | 1.07 MiB/s, done.
Total 10 (delta 2), reused 3 (delta 0), pack-reused 0
To https://git.mergetb.example.net/murphy/hello
 * [new branch]      master -> master

```
{{% /alert %}}

Login as the testbed user and follow the 
[hello world](/docs/experimentation/hello-world)
example.



Modify the experiment source to use bare-metal resources.

```python
from mergexp import *

# Create a netwok topology object.
net = Network('hello-world')

# Create two nodes.
a,b = [net.node(name, metal == True) for name in ['a', 'b']]

# Create a link connecting the two nodes.
link = net.connect([a,b])

# Give IP addresses to the nodes on the link just created.
link[a].socket.addrs = ip4('10.0.0.1/24')
link[b].socket.addrs = ip4('10.0.0.2/24')

# Make this file a runnable experiment based on our two node topology.
experiment(net)
```

Push an update to the experiment git repo, relinquish (`mrg relinquish` from the
CLI) the current realization and create a new one. 

Now it's time to materialize

```
mrg materialize world.hello.murphy
```

This will kick off a materialization on the Phobos site. If you open up a
console to the Raven virtual machines that have been allocated by the
realization engine (`x0` and `x1` usually chosen in my experience) using the
`virt-manager` tool available on fedora, you will see that these nodes have been
rebooted and they will go through the imaging process.

Once the nodes come up in the default Debian based operating system, you can
login with the credentials user=test password=test. You can then setup addresses
on the experiment interfaces of the nodes and the should be able to ping each
other. At the time of writing the system that configures the nodes called
Foundry is not yet fully integrated, so things like user accounts and automatic
experiment network setup for things like addresses and routes is not there yet.
