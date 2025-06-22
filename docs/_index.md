---
title: "Managing Research Programs and Groups"
linkTitle: "Managing Groups And Programs"
weight: 3
description: >
    Learn how to manage group research activities in Merge
---

{{% alert title="Command Line and Web Based Interfaces" color="info" %}}
This walkthrough demonstrates how to manage organizations and projects using the Merge command line
interface (CLI) `mrg`. We strive to implement equal functionality in the web-based graphical user
interface (GUI), and it should possible to use the GUI rather than the CLI to manage organizations and
projects. If you find that desired management functionality is missing from the GUI, please let us
know by emailing us at:
[contact-project+mergetb-support-email@incoming.gitlab.com](mailto:contact-project+mergetb-support-email@incoming.gitlab.com)
{{% /alert %}}

## Overview

The Merge Portal provides tools to facilitate management of research activities.  This page
discusses these tools and constructs, and gives examples of their intended use for supporting
educational and research endeavors.

## Merge Entities

Before discussing how to manage activities on the Portal, it is important to have a basic
understanding of the key concepts and terminology that Merge uses. The following diagram illustrates the relationships between the core Merge entities:
![](/img/management/portal-entities.png)

| Entity | Description |
| ------ | ----------- |
| __User__  | A user represents a human user of the Portal. Each user has a separate login username/ID, and may have membership in a set of projects and/or organizations.
| __Project__ | A project represents a type of experimental work to be done on a Merge testbed. Projects are often created to organize the activities of research groups. Users are granted membership in projects by creators and maintainers of those projects.
| __Organization__ | Organizations are used to manage a (typically large) group of users. When users join an organization, they delegate the authority to manage their account to the creators and maintainers of the organization. New users on the Portal can request membership in an organization when creating the account; when that happens, the organization's maintainers can authorize the account without requiring approval of a Merge Portal administrator. Projects can also join organizations, which gives the organization's maintainers access to the experiments created in that project.
| __Experiment__ | An experiment represents the target environment that a user wishes to create on the testbed. An experiment consists of a topology with nodes and links and characteristics of the topology, including OS images and link rates. Experiments are created in the context of a specific project.
| __Realization__ | A realization is a logical creation of an experiment on an underlying Merge testbed. When an experiment is successfully realized, the resulting realization is an embedding of the experiment topology on the physical resources of one or more resource substrates managed by the Merge Portal. Resources are reserved for the exclusive use of the realization, until the realization is relinquished by the user.
| __Materialization__ | A materialization is a physical instantiation of a realization on the resource substrates. When a materialization is created, virtual machine and bare metal nodes are imaged with OSes, and virtual networks are synthesized on node and switches to create the requested experiment topology.
| __Testbed Node__ | A testbed node is a physical server or device that is used to run experiment materializations.
| __Resource Pool__ | A resource pool, or simply pool, is a set of testbed nodes. Each project belongs to a pool. When experiments in a project are realized, the Portal realization algorithm may allocate nodes from the pool.  Multiple pools can be created by Merge Portal administrators, thereby partitioning/reserving resources for use in different projects.
| __XDC__ | Experiment Development Containers, or XDCs, are lightweight containers that provide users access to materializations through use of on-demand VPN tunnels. XDCs are created by users in the context of a specific project, and then attached to a materialization, which creates a VPN tunnel between the XDC and the infranet of the materialization. XDCs can themselves be accessed from the user's workstation, either through SSH or via the Launch web GUI.

## Managing Organizations

Organizations are designed to facilitate management of large groups of users (typically tens to
hundreds) by a small privileged set of users called organization maintainers. Organizations can be
created by users with a demonstrated need to manage a large group. Typically organizations are
created to manage large government funded research programs, where a large group of users
collaborating on the same sets of projects are expected to join the Portal.

### Creating an Organization

A new organization can be created via the CLI's `mrg new organization` command:
```
$ mrg new organization -h
Create a new organization

Usage:
  mrg new organization <name> [flags]

Flags:
  -d, --desc string   organization description
  -h, --help          help for organization
  -m, --mode enum     Access mode: one of public, private, protected. Default: public

Global Flags:
  -c, --colorless         Disable color output
  -j, --json              Output JSON
  -l, --loglevel string   Level to log at. One of panic, fatal, error, warning, info, debug, trace (default "info")
  -s, --server string     MergeTB API server address
```

Note the `-d` flag, which provides a description for the organization. This command creates an
organization, but places it a temporary inactive state. This is done because organization
maintainers are considered trusted users, given their ability to directly approve new accounts on
the Portal. Users who believe they have a legitimate use case to run an organization -- e.g., they
lead a large research group -- should reach out to the Merge
Portal operators to have their organization approved and placed in an active state.

### Having Your Organization Activated

Organization maintainers have a high level of privilege: when new members join their organization,
portal accounts for those members are automatically activated, without involvement of Merge portal
operators. This design facilitates quick standup of new organizations and influxes of new members,
but it places a large degree of confidence in organization maintainers, who must be responsible to
only approve membership for users with a need for testbed use, and to freeze accounts of users that
no longer have an authorized need for testbed use -- for example,
for users that violate terms of service or abuse resources.

Once you have created an organization, please send a message to the Merge portal operators
via the support email
[contact-project+mergetb-support-email@incoming.gitlab.com](mailto:contact-project+mergetb-support-email@incoming.gitlab.com),
providing a justification for your organization. If portal operators approve of
your use case, they will activate your organization, at which point you can
admit new members and create projects.

### Requesting Membership

Organization membership starts by a user making a request to join the organization. Typically,
a user's organization membership will be requested by the user itself; however, membership for the
user can also be requested by an existing maintainer on behalf of the user.

Organization membership can be requested through the CLIs' `mrg membership request organization user
<organization> <username>` command:

```
$ mrg membership request organization user -h
Request a user membership in an organization

Usage:
  mrg membership request organization user [organization] [username] [flags]

Flags:
  -h, --help          help for user
  -r, --role string   One of Member, Maintainer, Creator (default "Member")

Global Flags:
  -c, --colorless         Disable color output
  -j, --json              Output JSON
  -l, --loglevel string   Level to log at. One of panic, fatal, error, warning, info, debug, trace (default "info")
  -s, --server string     MergeTB API server address
```

Note the `-r` flag: each user in an organization must be assigned a __Role__. The role determines
what privileges the user has with respect to operations that read or modify organization state, as
described in this table:

| Role | Description |
| ---- | ----------- |
| __Creator__ | The user that created the organization. This user has full privileges to modify the organization and admit members as needed |
| __Maintainer__ | A user that is fully authorized to manage the organization. Maintainers typically have the same privileges as the creator |
| __Member__ | A user that is a member of the organization, thereby having access to its projects, but whom does not have privilege necessary to approve accounts or add/remove members |

By default, requests are made for the `Member` role.

### Confirming or Denying Membership

Organization membership is contingent on approval by _both_ the candidate new user and a maintainer
of the organization. If a user requests their own membership, they tacitly provide approval, meaning
only maintainer approval is needed to confirm membership. Conversely, if a maintainer requests
membership on behalf of a user, they tacitly approve membership, but the user must confirm the
request in order to be added to the organization. Note that these two approvals can happen in either
order. That is, the user can request membership and then be approved by a maintainer, or a
maintainer can add the user, and the user can subsequently approve their addition. The following
state diagram illustrates the process:
![](/img/management/organization-state-machine.png)

{{% alert title="Remember: Organization Membership Requires 2 Approvals" color="warning" %}}
Keep in mind that becoming an `Active` member of an organization requires approval from __both__ (1)
the user being added to the organization, and (2) an organization creator or maintainer. If only one
of the two approves, the user will be in either the `EntityRequested` or `MemberRequested` states,
which are pending states: the user will not be considered a member, will not have access to projects
or other data in the organization, and their account will not be able to be managed by the
organization maintainers.
{{% /alert %}}

To confirm or deny membership, use the CLIs' `mrg membership confirm` or `mrg membership deny`
commands. To confirm:

```
$ mrg membership confirm organization user -h
Confirm a user in an organization

Usage:
  mrg membership confirm organization user <organization> <username> [flags]

Flags:
  -h, --help   help for user

Global Flags:
  -c, --colorless         Disable color output
  -j, --json              Output JSON
  -l, --loglevel string   Level to log at. One of panic, fatal, error, warning, info, debug, trace (default "info")
  -s, --server string     MergeTB API server address
```

To deny:
```
$ mrg membership deny organization user -h
Deny a user membership in an organization

Usage:
  mrg membership deny organization user <organization> <username> [flags]

Flags:
  -h, --help   help for user

Global Flags:
  -c, --colorless         Disable color output
  -j, --json              Output JSON
  -l, --loglevel string   Level to log at. One of panic, fatal, error, warning, info, debug, trace (default "info")
  -s, --server string     MergeTB API server address
```

### Removing Members

After a member has been confirmed, either an organization maintainer or the member themself can
remove the member at any time. Use the same `mrg membership deny` command as above to do so.

### Deactivating Accounts

When an organization maintainer approves a new member, the Merge portal account for the new member
becomes fully activated. In this way, organization maintainers have a very high level of privilege:
the accounts they approve are activated without explicit approval of a Merge portal operator.

When an organization member no longer has an authorized need for testbed use, organization
maintainers should deactivate or "freeze" the member's account. This can be done through the
following CLI command:

```
$ mrg freeze user -h
Freeze a user

Usage:
  mrg freeze user <username> [flags]

Flags:
  -h, --help   help for user

Global Flags:
  -c, --colorless         Disable color output
  -j, --json              Output JSON
  -l, --loglevel string   Level to log at. One of panic, fatal, error, warning, info, debug, trace (default "info")
  -s, --server string     MergeTB API server address
```

If the maintainer wishes, they can then remove the user from the organization.

## Managing Projects

Projects are designed to facilitate management of small groups of users (typically tens or fewer)
that intend to collaborate on a set of experiments. Projects can be created by users with an
authorized need for testbed resources.  Typically, projects are created to manage small research
projects involving a research advisor and a set of students and/or collaborators; however, this is
not a requirement. Any academic research activity with a valid use case can be represented by a
project.

Projects are simpler to manage than organizations. Project creators/maintainers do not admit new
users to the testbed, and do not have authority to activate or freeze accounts. Project maintainers
simply have the authority to add new members that already have portal accounts to the project,
thereby giving those users access to testbed resources via the project, as well as access to
existing experiments already created in the project namespace.

### Creating a Project

A new project can be created via the CLI's `mrg new project` command:
```
$ mrg new project -h
Create a new project

Usage:
  mrg new project <name> <description> [flags]

Flags:
  -h, --help                  help for project
  -o, --organization string   add the project be added to the given organization

Global Flags:
  -c, --colorless         Disable color output
  -j, --json              Output JSON
  -l, --loglevel string   Level to log at. One of panic, fatal, error, warning, info, debug, trace (default "info")
  -s, --server string     MergeTB API server address
```

The project requires both a name and a description as command line arguments. The description is
important, as Merge portal operators will use it to determine whether the project's efforts
constitute a valid use case for the testbed.


### Acquiring Resources

Once a project has been created, you will be able to add members to the project, create experiments,
and realize/materialize those experiments.

However, at this stage, the amount of resources on the testbed that your project can use may be
limited. As discussed in the [Merge Entities](#merge-entities) section, each project is a member of
a resource pool, and by default, projects are placed into a default pool that is usually configured
with a limited number of testbed nodes, sufficient only to create small experiments and play around
with the testbed. To acquire access to more resources, you should open a ticket to request Merge
operators to place you in a larger resource pool. Please send a message to the Merge portal
operators via the support email
[contact-project+mergetb-support-email@incoming.gitlab.com](mailto:contact-project+mergetb-support-email@incoming.gitlab.com),
providing the name of your project in the message.

Note, however, that organization projects are treated differently. If you are a member of an
organization, you can use the `-o` flag for the `mrg new project` command to associate the project
with the organization. When you do this, the project will automatically use any resource pools that
may have been created for the organization. If you do not add your project to an organization, you
will be responsible for getting access to a resource pool, which must be done in consultation
with Merge portal operators as discussed in the previous paragraph.

{{% alert title="Personal Projects" color="warning" %}}
Note that __all__ users have a personal project automatically created for them when their account is
activated on the Merge portal. Personal projects have the same name as the username of the owning
user.  For example, user `bob`'s personal project is named `bob`. Note that personal projects __do
not exist in the context of any organization__, even if the user requests organization membership at
account creation.

Personal projects are meant for simple experimentation and exploration of the testbed. They should
not be used for complex experiments or experiments requiring more than a limited amount of
resources.
{{% /alert %}}

### Adding or Removing Members

Unlike organizations, membership in projects simply requires that an authorized project owner or
maintainer add a valid user account. This is done via the CLI command `mrg new member project`:
```
$ mrg new member project -h
Add a user to a project

Usage:
  mrg new member project <project> <username> [flags]

Flags:
  -h, --help          help for project
  -r, --role string   One of Member, Maintainer, Creator (default "Member")

Global Flags:
  -c, --colorless         Disable color output
  -j, --json              Output JSON
  -l, --loglevel string   Level to log at. One of panic, fatal, error, warning, info, debug, trace (default "info")
  -s, --server string     MergeTB API server address
```

As with organizations, project members are assigned a __Role__ via the `-r` flag:

| Role | Description |
| ---- | ----------- |
| __Creator__ | The user that created the project. This user has full privileges to modify the project and add/remove members as needed |
| __Maintainer__ | A user that is fully authorized to manage the project. Maintainers typically have the same privileges as the creator |
| __Member__ | A user that is a member of the project, thereby having access to its experiments, but whom does not have privilege necessary to manage the project and add/remove members |

## Use Case 1: Small Research Lab

Use case 1 focuses on the activities of a small research lab. In this case, an organization is
overkill. The principal investigator (PI) for the group should instead simply create a project. The
PI can then add students or other members of the lab as Maintainers of the project.  The PI or
project maintainers can then add other collaborators as regular Members. Upon creating the project,
the PI or a maintainer of the project should submit a ticket via the support email
[contact-project+mergetb-support-email@incoming.gitlab.com](mailto:contact-project+mergetb-support-email@incoming.gitlab.com)
to have their project placed into a resource pool with sufficient nodes to support the project
activities.

We summarize the process below:
1. All members from the research group create accounts through the Merge portal. These accounts will
   be approved by Merge portal operators, as there is no governing organization involved.
1. The PI creates a project, adding a ~1 paragraph description of the project's anticipated research
   activities and the types of experiments that will be performed.
1. The PI or a maintainer of the project submits a ticket via the support email to have their
   project placed into a resource pool with sufficient nodes to support the project activities.
1. The PI adds other group members to the project, assigning them each the role of Maintainer or
   Member, depending on the level of privilege desired for each user. See the table in [#Adding or
   Removing Members](#adding-or-removing-members) for a description of project roles. Note that a
   Maintainer may also add additional members to the project.
1. Project members create, realize, and materialize experiments on the testbed.

## Use Case 2: Large Research Program

Our second use case focuses on the activities of a larger scale research program, such as those
involving multiple individually funded research performers working towards a common research
objective. In this case, a designated "program coordinator" (could be the program manager, PI of a
funded project, or a Merge portal operator, etc.) creates the organization and has it approved by
Merge operators. PIs of each individual funded project join the organization as Maintainers, and
create individual projects within the organization to manage the efforts of their team/group.
Individual contributors to each team join the organization as regular Members and are assigned to
the specific project by their project PI. Organizations facilitate a flexible managerial model: the
program coordinator need only create the organization and approve accounts of the project PIs, who
in turn approve accounts of organization members that belong to their team. The activities of each
team are localized to their specific project. Each project can be created with specific permissions
to either allow or disallow access to non-project members.

One example breakdown of roles and activities in a research organization is shown below, involving
three research projects collaborating in a research program.
![](/img/management/organization-program.png)

We summarize the process below:
1. Program coordinator creates an account through the Merge portal. This account will be approved by
   a Merge portal operator.
1. Program coordinator creates an organization for the research program, describing the nature of
   organization as supporting a funded research program, and emails the Merge portal operators to
   request activation.
1. Individual project PIs create accounts on the Merge portal and request membership in the organization,
   selecting the `Maintainer` role, and contact program coordinator to request approval of their
   organization membership.
1. Project PIs create projects for their specific team's work, creating the project in the context
   of the organization.
1. Team members create accounts on the Merge portal and request a regular `Member` roll in the
   organization. Project PIs approve accounts as needed, and add team members to their respective
   projects with the desired role for the project.
1. Project members create, realize, and materialize experiments on the testbed.
