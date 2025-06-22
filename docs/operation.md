---
title: "Operation"
linkTitle: "Operation"
description: >
    How to operate a Merge portal
---


## Identity

A Merge portal has distinct concepts of identities and users. An identity
associates an email address to a set of access credentials. 

### Getting Identity Info

Portal administrators can list identities with

```
mrg list ids
```

which will show something like
```
USERNAME    EMAIL                      ADMIN
ry          ry@goo.com                 false
ops         ops@mergetb.example.net    true
```

### Creating Identities

A new identity can be created through the `mrg` command line tool.

```
mrg register <username> <email> <password>
```

This command is typically called directly by a user to register with a Merge
portal. It may also be used by administrators or project leaders with temporary
passwords for automatic onboarding of team members.


## Users

A user account references an identity and includes the following

- A home directory on the Merge portal file system (MergeFS).
- A set of projects the user is a member of and is authorized to access.
- A set of certificate-based SSH keys for accessing XDCs and experiment nodes.

### Getting User Info

Users can be listed as follows

```
mrg list users
```

Which will show something like

```
USERNAME    NAME    STATE     MODE      UID     GID
ry                  NotSet    Public    1000    1000
```

### Creating users

To create a new user from an identity, an administrator can do the following.

```
mrg init <username>
```

### Activating Users

When a user account is first created. It is not active, and must be activated by
an administrator.

```
mrg activate <username>
```

When a user is activate, you will see the following from `mrg list users`

```
USERNAME    NAME    STATE     MODE      UID     GID
ry                  Active    Public    1000    1000
```

## Policy

What a user can and cannot do is defined by portal policy. Portal policy is a
declarative set of rules that map entities such as experiments, projects and
user accounts onto a set of properties that a caller must satisfy in order to
manipulate those entities.

For example, consider the following policy fragment.

```yaml
experiment:
  public:
    create: [Project.Member]
    read:   [Any.Any]
    update: [Experiment.Maintainer, Project.Maintainer]
    delete: [Experiment.Creator, Project.Maintainer]

  protected:
    create: [Project.Member]
    read:   [Project.Member]
    update: [Experiment.Maintainer, Project.Maintainer]
    delete: [Experiment.Creator, Project.Maintainer]

  private:
    create: [Project.Member]
    read:   [Experiment.Maintainer, Project.Creator]
    update: [Experiment.Maintainer, Project.Creator]
    delete: [Experiment.Creator, Project.Creator]
```

This policy states that public experiments can be read by anyone, protected
experiments can be read by project members and private experiments can only be
read by maintainers or the project creator of the project the experiment belongs
to.

### Default

The full default policy is available
[here](https://gitlab.com/mergetb/portal/services/-/blob/v1-staging/pkg/policy/policy.yml).

### Updating

The active policy in the Merge portal exists as a Kubernetes
[ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/). To
change the current policy configuration, you can use the following 
[OpenShift CLI](https://docs.okd.io/latest/cli_reference/openshift_cli/getting-started-cli.html)
client `oc`.

```shell
oc create configmap policy --from-file=<path-to-policy.yml> --dry-run=client -o yaml -n merge | oc apply -f -
```

In order for the updated policy to take effect, you will need to restart your
API servers. You can do this without disruption as follows.

```
oc rollout restart deployment/apiserver -n merge
```
