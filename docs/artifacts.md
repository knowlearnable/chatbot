---
title: "Artifacts"
linkTitle: "Artifacts"
weight: 10
description: >
  Experimental Artifacts on Merge Testbed
---

{{% alert title="Attention" color="warning" %}}

This guide assumes you are using the reference portal at `sphere-testbed.net`. Instructions on this page only apply to that portal.

{{% /alert %}}

# What are experimental artifacts?

Experimental artifacts in a narrow sense can be thought of as "canned" MERGE experiments.  It can include the information needed to set up, run, collect data, 
calculate statistics, validate results and so on.  All of it is packaged as a binary blob, such as a tar-ball, with metadata  that gets stored in the portal 
and can be shared among researchers.

Tighter integration with the portal is work in progress, at the moment artifacts can only be used for documenting and sharing experiments' scripts and data.

# Artifact Life-Cycle

Artifacts can be created, modified, shared, and removed.  These operations are shown below.

## Creating an artifact

Suppose you assembled all your experiment data in a single directory and created a tarball `/tmp/myexperiment.tar.gz`.  It should be accompanied by a 
readme-file (`README.md`, or it can be a URL) with the documentation explaining in detail what the experiment is about and what needs to be done to successfully
run it.  We can create a new artifact and upload it to the portal by running:

```
mrg artifact new --description "short description of the artifact" --keywords test,hello,hello-world  --readme README.md /tmp/myexperiment.tar.gz 
calculating checksum 100% [==========] (24/24 kB, 389 MB/s)
uploading artifact   100% [==========] (24/24 kB, 184 MB/s)
INFO uploaded artifact id: af8d55d7-dec5-4fe6-912b-167f5f576435 
```

We can see that the artifact has been successfully created and assigned id `af8d55d7-dec5-4fe6-912b-167f5f576435`.  This id will be used to reference this artifact for
other commands.

Now we can list all available to us artifacts (i.e., the artifacts that we have access to) and make sure it's in the catalog:

```
mrg artifact list
Id                                      Name                   Description                            Mode       Readme       Project    Organization    Keywords                        Creator    Size
af8d55d7-dec5-4fe6-912b-167f5f576435    myexperiment.tar.gz    short description of the artifact      Public     README.md                               test,hello,hello-world,world    olive      23 KiB
```

## Modifying an existing artifact

This example shows how we can change the description and keywords of an existing artifact:

```
mrg artifact update --description "hello-world experiment" --keywords hello,hello-world,world af8d55d7-dec5-4fe6-912b-167f5f576435
```

Listing the artifacts will show the change (note that in this example we can list artifacts that match a particular keyword):

```
mrg artifact list -k hello-world
Id                                      Name                   Description                            Mode       Readme       Project    Organization    Keywords                   Creator    Size
af8d55d7-dec5-4fe6-912b-167f5f576435    myexperiment.tar.gz    hello-world experiment                 Public     README.md                               hello,hello-world,world    olive      23 KiB
```
 
## Viewing an artifact details

Artifacts can be large in size and before downloading it, users need to make certain they are getting what they want.

To see the readme you can type:

```
mrg artifact readme af8d55d7-dec5-4fe6-912b-167f5f576435
...
```

The above commands shows the readme on the standard output.  Since the readme can be large, it's recommended either to use
a pager program, such as `less`:

```
mrg artifact readme af8d55d7-dec5-4fe6-912b-167f5f576435 | less
```

Or save it to a file by redirecting standard output:

```
mrg artifact readme af8d55d7-dec5-4fe6-912b-167f5f576435 > /tmp/readme-copy
```

If you just need to see artifact's metadata, you can use `mrg artifact meta` command:

```
mrg artifact meta af8d55d7-dec5-4fe6-912b-167f5f576435
Id:             af8d55d7-dec5-4fe6-912b-167f5f576435
Name:           myexperiment.tar.gz
Creator:        olive
AccessMode:     Public
Readme:         README.md
Size:           23461
Checksum:       SHA1:67c68b9a488a2acbdd27c23a1185ba958b46732f
Description:    hello-world experiment
Project:
Organization:
Keywords:       hello,hello-world,world
```

## Downloading an artifact

An artifact can be downloaded to a local sub-directory of you current working directory:

```
mrg artifact get af8d55d7-dec5-4fe6-912b-167f5f576435
INFO saving artifact to ./af8d55d7-dec5-4fe6-912b-167f5f576435/myexperiment.tar.gz 
downloading artifact 100% [==========] (24/24 kB, 17 MB/s) 
calculating checksum 100% [==========] (24/24 kB, 259 MB/s)
INFO validated checksum of af8d55d7-dec5-4fe6-912b-167f5f576435/myexperiment.tar.gz 
INFO saving artifact readme to ./af8d55d7-dec5-4fe6-912b-167f5f576435/README.md 
INFO saving artifact metadata to ./af8d55d7-dec5-4fe6-912b-167f5f576435/metadata.json 
```

Now we can confirm that the artifact is available locally:

```
ls af8d55d7-dec5-4fe6-912b-167f5f576435
metadata.json  myexperiment.tar.gz  README.md
```

## Deploying an artifact on the testbed

Artifacts can be directly downloaded (deployed) on the testbed.  The following command
demonstrates an XDC type of deployment, where it downloads and untars the specified artifact 
id in the user's portal home directory available on any of the user's XDC under 
`$HOME/artifacts/<artifact_id>`:

```
mrg artifact deploy --type xdc af8d55d7-dec5-4fe6-912b-167f5f576435
```

Currently only `--type xdc` deployments are supported.


## Deleting an artifact

An artifact can be deleted with a delete command:

```
mrg artifact delete af8d55d7-dec5-4fe6-912b-167f5f576435
```


# Artifact Access Control

Artifact sharing can be restricted if so desired.  First, the artifact has access mode used in other
MERGE access operations: `Public`, `Protected`, and `Private`.  A `Public` artifact can be viewed and
downloaded by anyone.  `Protected` and `Private` artifacts are restricted.  If an artifact is associated with
a particular organization or project, `Protected` and `Private` artifacts are made available to the other 
members of the same organization or project.

# Artifact Quotas

Users are given a limited quota (128GiB by default).  The current usage be viewed as:

```
mrg art quota
Username    Usage     Capacity    Available
olive       23 KiB    128 GiB     128 GiB
```

Admins can use artifact quota command to adjust the quota for a particular user and list quotas for current artifact users.
