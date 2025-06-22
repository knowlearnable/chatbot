---
title: "Hello World (Command Line Interface)"
linkTitle: "Hello World (Command Line Interface)"
weight: 2
description: >
    A hello world experiment in Merge using the command line interface
---

{{% alert title="Attention" color="warning" %}}
Welcome to your guided tour of networked system experimentation in Merge.  Start by following the
["Getting Started"](/docs/experimentation/getting-started) instructions to create your account and
have it approved, download the `mrg` CLI to your local system, and configure the CLI based on the
address of the portal.

This guide assumes you are using the reference portal at `sphere-testbed.net`. If you are using a
different portal, substitute addresses in this document that reference `sphere-testbed.net` accordingly.

Consult your project leader if you are not sure of the portal address.

Now let's dive in.
{{% /alert %}}

{{% alert title="Tip" color="info" %}}
This guide assumes the username `murphy`. Adjust for your username accordingly.
{{% /alert %}}

## Create Experiment Walk-through

### Create an Experiment

To get started we'll create an experiment

```shell
mrg new experiment hello.murphy 'My first experiment'
```

Every experiment is a part of a project. In the command above, `hello.murphy`
follows the form `<experiment>.<project>`. Every user has a _personal project_
that is automatically created when they first join a Merge portal. The personal
project has the same name as the user. Here we are using `murphy`'s personal
project for the home of our `hello` experiment.

{{% alert title="Tip" color="info" %}}
Dot delineated hierarchical naming is pervasive in the `mrg` command line tool. All objects are
referenced using this form.
{{% /alert %}}


### Assessing Experiment Status

Now that our experiment is created, we can see it in Merge in a few ways. The
most basic is asking merge for a list of experiments.

```shell
mrg list experiments
```
```
Name.Project    Description            Mode
------------    -----------            ----
hello.murphy    My first experiment    Public
```

More detailed information about the experiment is available through the `show`
command.

```shell
mrg show experiment hello.murphy
```
```
Repo: https://git.sphere-testbed.net/murphy/hello
Mode: Public
Description: My first experiment
Realizations:
  Revision    Realizations
  --------    ------------
```

In addition to the information we've already seen, this display shows us two new
things.

1. An address for a Merge-hosted Git repository for our experiment

   `https://git.sphere-testbed.net/murphy/hello`

2. The [realizations](#realizing-an-experiment) associated with this experiment.

{{% alert title="Tip" color="info" %}}
You can use prefixes for any `mrg` command to avoid excessive typing. For
example, the following two commands are equivalent:
```shell
mrg list experiments
mrg li e
```
{{% /alert %}}


### Pushing Experiment Source

Without any source, an experiment is just an empty shell. We add source by
pushing to the Git repository associated with our experiment. We identified this
repository in the previous step as `https://git.sphere-testbed.net/murphy/hello`.


There are two ways to access an experiment's git repository: using standard git
tools or the `mrg` CLI

#### Adding model revisions to an experiment via git

First let's look at using standard git tools.
Start by grabbing an existing experiment from the official Merge examples
on GitLab.com.

```shell
git clone https://gitlab.com/mergetb/examples/hello-world
cd hello-world
```

This is a very basic hello world experiment with two nodes interconnected by a
link.

```python
from mergexp import *

# Create a network topology object.
net = Network('hello-world')

# Create two nodes.
a,b = [net.node(name) for name in ['a', 'b']]

# Create a link connecting the two nodes.
link = net.connect([a,b])

# Give IP addresses to the nodes on the link just created.
link[a].socket.addrs = ip4('10.0.0.1/24')
link[b].socket.addrs = ip4('10.0.0.2/24')

# Make this file a runnable experiment based on our two node topology.
experiment(net)
```

{{% alert title="Tip" color="info" %}} More details on topology modeling can be found in the <a
href="../model-ref/">"Experiment Model Reference"</a> section.  {{% /alert %}}

**The important thing to note about source repositories is that there is a
requirement about where the experiment topology file lives:**

- For Python sources, the main topology file must be `model.py`
- For Go sources, the main topology file must be `model.go`

Now that we have the source in a local Git repository, let's push it to Merge.
Start by adding a new remote to the repository.
```
git remote add mergetb https://git.sphere-testbed.net/murphy/hello
```

Before continuing we need to make sure we are ready to enter authentication
information. Only experiment or project members can push sources to Merge
experiment Git repos. Git authentication in Merge works through tokens, to
access your token do the following.

```
mrg whoami -t
```

This will display a glob of text, that is your access token. Now let's push some
source to our experiment.

```
git push -u mergetb
```

This will ask you for a username and password. **For the username enter the
token, leave the password blank**. If the push was successful, your experiment
now has source.

#### Adding model revisions to an experiment via `mrg`

The `mrg` utility supports adding a model to an experiment as well. It essentially does
the above, but in a single command. It uses the authentication token generated
during a `mrg login ...` to push a model to the experiment git repostory on your
behalf. The command is `mrg push` and the abbrivated usage is:

```
Push a model to the given experiment repository.

Usage:
  mrg push <model-file> <experiment>.<project> [flags]

Flags:
      --branch string   Repository branch to push the model to. (default "master")
  -h, --help            help for push
      --tag string      Tag the commit with the given tag.
```

Assuming the model at `./model.py` is a valid model file, you can push it to the `master`
branch of the experiment repository via:

```
mrg push ./model.py hello.murphy
```

If you now fetch the repository you will see that the system has pushed a new
revision on your behalf:

```
commit bbd67f119672bc0cedc8fd97476e6aeea7458a6c
Author: ...
Date:   Mon Feb 14 17:37:53 2022 +0000

    merge model auto-commit
```

You can also push with a git tag. This will make it easier to realize the model
later as you do not have to know the revision string, just the tag. To push with
a tag give the `--tag` argument:

```
mrg push ./model.py hello.murphy --tag olive
```

This pushes the model and creates the given git tag. The log will look like this:

```
commit 37bd4776dc458182290a9d4106ffb1b47797760c (tag: olive)
Author: ...
Date:   Mon Feb 14 17:39:17 2022 +0000

    merge model auto-commit

```

{{% alert title="Note" color="warning" %}}
The `mrg push` command only currently supports tagging on the master
branch. It does not support pushing to a non-master branch.
{{% /alert %}}


### Confirming Realization Model Compilation

For a realization to work, the model you pushed must compile correctly. The compilation
status is displayed via the optional argument `--with-status` given to the
`mrg show experiment` command.

This command shows the compilation status of all model revisions pushed to the
experiment's git repository. Since we've only pushed one revision only one
will be listed. (Note the `revision` is the git revision. This can be seen
by looking at the newest git log, `git log -1`.)

```
mrg show experiment hello.murphy --with-status
```

```

Repo: https://git.sphere-testbed.net/murphy/hello

Mode: Public
Description:
Revisions:
  Revision                                    Compilation Status
  --------                                    ------------------
  000cf5171f4248dfc71d222468a4abe83a6912df    success
Realizations:
  Revision    Realizations
  --------    ------------
```

Confirm the status is `success`. If not, the compilation error is shown.

### Realizing an Experiment

The next step toward creating a working experiment is realization. Realization
is the act of finding a suitable set of resources for your experiment, and
allocating those resources for your experiment's exclusive use.

A realization is based on a specific `revision of an experiment`. Let's use
`git` to look at the latest revision for our experiment.

```
git log -1
```
```
commit 000cf5171f4248dfc71d222468a4abe83a6912df (HEAD -> master, origin/master, origin/HEAD)
Author: Ryan Goodfellow <rgoodfel@isi.edu>
Date:   Tue Dec 29 08:58:24 2020 -0800

    initial

    Signed-off-by: Ryan Goodfellow <rgoodfel@isi.edu>
```

Here we see the latest revision has the identifier
`000cf5171f4248dfc71d222468a4abe83a6912df`. So let's go ahead and create a
realization for that version of our source called `world`.

```
mrg realize world.hello.murphy revision 000cf5171f4248dfc71d222468a4abe83a6912df
```

If the revision has a git tag associated with with it (created using
`mrg push ... --tag` or `git tag ...`) you can reference the tag instead of the
revision string:

```
mrg realize world.hello.murphy tag olive
```

### Assessing Realization Status

Now we can take a look at our realization in pretty much the same way as we did
for our experiment. Start by listing your realizations.

```
mrg list realizations
```
```
Realization           Nodes    Links    Status
-----------           -----    -----    ------
world.hello.murphy    2        1        Succeeded
```

This display tells us that we have 1 realization with two nodes and 1 link that
was successful. To find out more information, show the realization.

```
mrg show realization world.hello.murphy
```
```
Nodes:
a -> osprey0 (VirtualMachine)
b -> osprey0 (VirtualMachine)
Links:
a.0~b.0
  ENDPOINTS:
  WAYPOINTS:
```

This display shows us how our experiment was mapped onto testbed resources. In
this case both of our nodes were mapped to virtual machines running on the same
physical host named `osprey0`. We see a link that has no endpoints or waypoints,
which is expected in this case as both VMs reside on the same machine so there
is no actual physical link connecting them.

### Materializing the Realization

[Materialization](/docs/concepts/experimentation/#materialization) is the process of taking the resources reserved by your realization and making them exist in the world. Nodes (bare metal nodes and/or virtual machines) in the experiment are turned on, imaged with the correct operating system and configured according to experiment specifications. The network to implement the experiment topology is created (along with an command and control “infrastructure” network that the portal uses for node management).

To materialize your realization, do
```
mrg mat world.hello.murphy
```

This will start the materialization process, you'll need to wait for it to complete.
If the command terminates early while in progress, you can check it with:
```
mrg show mat world.hello.murphy -S
```

### Create an XDC

The entry point to your experiment is an [eXperiment Development Container (XDC)](/docs/experimentation/xdc). This container runs inside the Portal and serves as a home base for experiment development, configuration, and analysis. The container exists in a project space and can "attach" to any materialization in the same project that it is in. The attach process creates a tunnel from the XDC to the "infrapod" inside your experiment. From there, you can connect and interact with nodes in your experiment.

XDC's and their command line interface are here [on this page](/docs/experimentation/xdc) and will guide you to

### Configuring and using the Experiment Materializations

Please see the [documentation on Experiment Automation](/docs/experimentation/experiment-automation).

### Rebooting or Reimaging Nodes of a Materialization

After an experiment has materialized, you can reboot or reimage nodes at any time. Nodes can be warm rebooted, in which the node OS attempts to gracefully shutdown and restart, or hard reset through a power cycle operation. Nodes can also be reimaged, which corresponds to a power cycle operation plus resetting the node to its base image specified in your experiment model.

To do so via the CLI, use
```
mrg nodes reboot <realization>.<experiment>.<project> [<nodes>...] -m $REBOOT_TYPE
```

where `$REBOOT_TYPE` is one of `[Reboot, Cycle, Reimage]`

## Experiment Cleanup

Once you're done using the your experiment, you should free the resources for others. Merge is smart about experiment clean up and will free and relinquish all resources when an experiment is deleted. We go through the steps here though for informational purposes and in case you ever need to partially cleanup an experiment. Knowing these steps are useful.

### Detach XDCs

To detach an XDC, use:
```
mrg xdc detach <xdc>.<project>
```

### Dematerialize the Experiment

Dematerializing an experiment does the opposite of materialization. The nodes are reimaged and the experiment networks are torn down. Note that this *does not* free the resources for use to others. The realization is resource reservation. We'll relinquish the resources in the next step.

To do so, use:
```
mrg demat <realization>.<experiment>.<project>
```

### Relinquish the Resources

Now we'll free the resources you've reserved with your realization:

```
mrg relinquish <realization>.<experiment>.<project>
```

## Running Multiple Versions of the Same Experiment

Now let's say we have a slightly different version of this experiment in a
different branch of our repository. In this version of the experiment, we want
bare-metal nodes instead of virtual machines. Let's check out that branch and
take a look at the difference from our master branch.

```
git checkout metal
git diff master
```
```diff
diff --git a/model.py b/model.py
index 2e0b578..748c285 100644
--- a/model.py
+++ b/model.py
@@ -4,7 +4,7 @@ from mergexp import *
 net = Network('hello-world')

 # Create two nodes.
-a,b = [net.node(name) for name in ['a', 'b']]
+a,b = [net.node(name, metal==True) for name in ['a', 'b']]

 # Create a link connecting the two nodes.
 link = net.connect([a,b])
```

This shows us there is a single change, to specify the `metal` property for each
node. This ensures that we will get bare metal nodes for `a` and `b`.

Let's push this branch to our experiment source repo.

```
git push -u mergetb metal
```

Now let's determine the latest commit in this branch,

```
git log -1
```
```
commit 8dd799637047e3bf845a5a16f44228d24d10f6ff (HEAD -> metal, origin/metal, mergetb/metal)
Author: Ryan Goodfellow <rgoodfel@isi.edu>
Date:   Thu Dec 31 13:35:03 2020 -0800
...
```
and create a realization from that revision of the source
```
mrg realize metal.hello.murphy revision 8dd799637047e3bf845a5a16f44228d24d10f6ff
```
which yields
```
mrg show realization metal.hello.murphy
```
```
Nodes:
a -> finch0 (BareMetal)
b -> finch1 (BareMetal)
Links:
a.0~b.0
  ENDPOINTS:
  [1000] a@finch0 &{Phy:name:"eno1"}
  [1000] b@finch1 &{Phy:name:"eno1"}
  WAYPOINTS:
  [1000] xfleaf0: &{Access:port:"swp0"  vid:47}
  [1000] xfleaf0: &{Access:port:"swp1"  vid:47}
```

This time we see that our experiment has mapped onto bare-metal nodes with
physical links interconnecting them.
