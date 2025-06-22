---
title: "Operation"
linkTitle: "Operation"
weight: 4
description: >
    How to operate your Merge facility
---

{{% pageinfo %}}
This is a placeholder for giving a high level overview of a Merge testbed
facility
{{% /pageinfo %}}

## Modeling

{{% pageinfo %}}
This is a placeholder for facility modeling
{{% /pageinfo %}}

## Commissioning a new facility

Commissioning is the process by which a facility is made available to users
through a Merge portal. To commission a testbed facility using, you will need
your saved facility model on hand.


```shell
mrg new facility <facility-name> <facility-fqdn> <facility.xir> <facility-api-certificate>
```

Here `facility-fqdn` is the fully qualified domain name of the facility, 
`facility.xir` is the output of the `save` command from the
[modeling](#modeling) section, and `facility-api-certificate` is the `apiserver.pem` 
generated during the [install](/docs/facility/install/#running-the-installer).


## MARS command line interface

MARS (Merge Automated Resource Space) is the system that governs the operation of the testbed
facility. MARS is a collection of microservices that execute on different assets of the facility,
including infrastructure servers, emulation nodes, hypervisor nodes, and switches.

MARS runs an apiserver on each infrastructure server that implements the Merge facility API. The
Merge portal uses this API to materialize and dematerialize experiments.

MARS has an advanced configuration system through which an operator can customize the installation
and operation of the facility. This is done through the `mrs` command line interface (CLI) tool.
This tool should be run from an operations node in the facility itself. Specifically, it must have
network access to the infrastructure server machine(s) on which `etcd` and `minio` containers for the
facility are running.

```shell
[root@ops rvn]$ mrs --help
The Mars CLI admin tool

Usage:
  mrs [command]

Available Commands:
  clear         Clear reconciler errors
  completion    generate the autocompletion script for the specified shell
  config        Manage Facility Configuration
  deinit        Deinitialize things
  dematerialize dematerialize an experiment
  emu           Configure network emulation
  help          Help about any command
  init          Initialize things
  list          List things
  materialize   materialize a topology on this testbed
  portal        commands that act on the facility's portal
  show          Show things
  update        Update things

Flags:
  -s, --apiserver string   The hostname or address of the apiserver to contact (default "apiserver")
  -h, --help               help for mrs
  -j, --json               Output as JSON
  -m, --model string       The XIR model of the testbed to use (default "/etc/tbxir.pbuf")
  -v, --verbose            Enable verbose output

Use "mrs [command] --help" for more information about a command.
```

### Bootstrapping the facility

Once you have an operations machine up and running and connected to the infrastructure servers, you
will need to use the MARS CLI tool to bootstrap the facility.

1. Download the CLI:
```shell
curl -OL https://gitlab.com/mergetb/facility/mars/-/jobs/artifacts/v1-staging/raw/build/mrs?job=make
sudo mv mrs /usr/local/bin/mrs
```

2. Bootstrap the Minio datastore:
```shell
mrs init minio
```

**Note**:You need the following environment variables to be set for this command to succeed
- `export MINIO_ROOT_USER=<user>`
- `export MINIO_ROOT_PASSWORD=<password>`

The default credentials are `mars/muffins!`; however, these can be specified as
part of the `facility-install` process, and can be viewed in the
`mars-config.yml` file that it generates under the `services.infrapod.minio.credentials` entry:

```shell
services:
    infrapod:
		...	
        minio:
            address: minio
            credentials:
                username: mars
                password: muffins!
                token: ""
```

3. Initialize facility configuration system
```shell
mrs init config
```

**Note**: `mrs init config` will initialize the configuration using default settings in the
`mars-config.yml` generated as part of the `facility-install` process. This file is typically placed
in `/etc/mars-config.yml`, but if located elsewhere, use `mrs init config [path-to-config.yml]`

**Note**: `mrs config` subcommand shows how to view and modify the facility configuration. Most settings
can typically be left as is, however, things like container registries can be viewed and modified


4. Establish connection with the Merge portal and initialize the facility
```shell
$ mrs config get | grep Portal
Services.Portal.Address                                       grpc.mergetb.example.net
Services.Portal.Port                                          443
Services.Portal.TLS.Cacert                                    
Services.Portal.TLS.Cert                                      
Services.Portal.TLS.Key                                       
Services.Portal.Credentials.Username                          murphy
Services.Portal.Credentials.Password                          mergetb
Services.Portal.Credentials.Token                             
```

The MARS configuration needs to include several options in order to reach the Merge portal
- `Services.Portal.Address`: Public network address for the GRPC portal endpoint
- `Services.Portal.Port`: 443
- `Services.Portal.Credentials.Username`: Username of the account that commissioned the facility
- `Services.Portal.Credentials.Password`: Password of the account that commissioned the facility

These values can be changed through `mrs config set <key> <value>`. Once these settings are
configured, initialize the facility with a special facility-wide materialization called the "Harbor"

```shell
mrs init harbor
```

5. Populate images

Load images into the facility minio datastore:
```shell
mrs init images -c 5
```

## Infrastructure servers

Infrastructure servers run [Fedora CoreOS](https://getfedora.org/en/coreos) (FCOS).
FCOS is a lightweight Fedora distribution designed for running containerized
workloads. Infrastructure servers run the following containerized services.

- **frr**: manages routing configuration for infrapod server.
- **canopy**: manages network interfaces on an infrapod server.
- **infrapod**: manages per-experiment infrastructure pods.
- **metal**: manages bare metal power state
- **apiserver**: implements the Mars API and presides over testbed facility
                 target state

Each of these services runs as a podman container whose lifetime is managed by a
systemd service.

To see the pods

```shell
podman ps
```
which should show something like
```
CONTAINER ID  IMAGE                                                       COMMAND               CREATED       STATUS           PORTS   NAMES
83041490e27c  quay.io/mergetb/frr:solovni                                                       23 hours ago  Up 23 hours ago          cranky_lichterman
2713cecced51  quay.io/coreos/etcd:v3.4.14                                 /usr/local/bin/et...  23 hours ago  Up 23 hours ago          eloquent_black
06eb55d018c6  docker.io/minio/minio:RELEASE.2021-01-16T02-19-44Z          minio server /min...  23 hours ago  Up 23 hours ago          adoring_aryabhata
3e4103e9b447  registry.gitlab.com/mergetb/facility/mars/canopy:latest                           5 hours ago   Up 5 hours ago           affectionate_haslett
02e2d4b2754a  registry.gitlab.com/mergetb/facility/mars/infrapod:latest   /bin/sh -c /usr/b...  5 hours ago   Up 5 hours ago           magical_albattani
76f1d6db07f1  registry.gitlab.com/mergetb/facility/mars/metal:latest      /bin/sh -c /usr/b...  5 hours ago   Up 5 hours ago           intelligent_gauss
c375f79b8b2c  registry.gitlab.com/mergetb/facility/mars/apiserver:latest  /bin/sh -c /usr/b...  5 hours ago   Up 5 hours ago           clever_hermann
```

each one of these containers has a parent systemd service with the name
`mars-<service-name>`. For example

```shell
systemctl status mars-apiserver.service
```
```
● mars-apiserver.service - mars-apiserver
     Loaded: loaded (/etc/systemd/system/mars-apiserver.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2021-05-02 19:27:00 UTC; 1 day 2h ago
    Process: 200335 ExecStartPre=/usr/bin/podman pull --tls-verify=false registry.gitlab.com/mergetb/facility/mars/apiserver:latest (code=exited, status=0/SUCCESS)
    Process: 201040 ExecStartPre=/usr/bin/rm -f //run/mars-apiserver.service-pid //run/mars-apiserver.service-cid (code=exited, status=0/SUCCESS)
    Process: 201041 ExecStart=/usr/bin/podman run --conmon-pidfile //run/mars-apiserver.service-pid --cidfile //run/mars-apiserver.service-cid --network=host --privileged -v /var/vol/certs:/certs:Z -e MINIO_ROOT_USER=mars -e MINIO_ROOT_PASSWORD=mYQi9N7jT0o6eOsaUA1cRxqt3v5M84u2 -d registry.gitlab.com/mergetb/facility/mars/apiserver:latest (code=exited, status=0/SUCCESS)
   Main PID: 201174 (conmon)
      Tasks: 2 (limit: 4611)
     Memory: 26.8M
        CPU: 1.187s
     CGroup: /system.slice/mars-apiserver.service
             └─201174 /usr/bin/conmon --api-version 1 -c c375f79b8b2cb18fa6f27455bd1967fd79e66f84f5ae8d1429f556f269bb5fd6 -u c375f79b8b2cb18fa6f27455bd1967fd79e66f84f5ae8d1429f556f269b…

```

### Updating Containers

The systemd service that runs each infrastructure service automatically tries to
pull the latest version of the installed container at each start. To restart services, 
`sudo systemctl restart mars-<service-name>`

### Changing Container Registries/Tags

The `mrs` CLI can be used to change container registries or tags. For example, if you have a special
`testing` tag for the apiserver, you can run this from the ops machine:
```shell
mrs config set Images.Infraserver.Apiserver.Tag testing
```

The Apiserver container will automatically restart using the container specified

### Updating facility model

You can update the testbed model as the facility sees it as follows.

```
mrs update model <model.xir>
```

This will update the testbed model in the data store and new requests from
components to read the model will automatically pick up the new model,
independent of their location in the testbed cluster. However, some components
do cache the model in memory such as the `apiserver`. If you are seeing
unexpected behavior after a model update, consider restarting the component so
it will pick up the new model.

### Fetching facility model

To fetch the current facility model from a Merge portal use

```
mrg show fac -m <facility-name> -x
```

this will save the facility model as `<facility-name>.xir`. The `-j` flag can
also be used to get a JSON representation that is human readable.
