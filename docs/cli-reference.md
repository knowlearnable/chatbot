---
title: "Command Line Interface Reference"
linkTitle: "CLI Reference"
weight: 4
description: >
  Using the Merge command line interface
---

{{% alert title="Tips" color="primary" %}}

- All commands support **abbreviated syntax**, so the following are equivalent

```sh
mrg list experiments
```

```sh
mrg li e
```

- As of version `v1.1.1`, the `mrg` binary supports self updating via `mrg update binary`.

- Most commands support **rendering as JSON** via the `--json` flag. This is useful
  for tool and script integration.

- All **names have a hierarchical syntax**, so an experiment called `muffins` in the
  project `bakery` is referred to as `muffins.bakery`

- There are **useful help menus** with all commands accessible through the `-h`
  flag.

- **Be sure to login first** `mrg login <username> <password>`, login tokens do
  not last forever and may expire so you may have to login again from time to
  time.
  {{% /alert %}}

## Introduction

The command line interface to Merge, named `mrg`, lets users interact with a single Merge Portal.
To use most commands, users must first login to the testbed and authenticate against an existing active account.
The exception for this is account registration when, of course, one cannot authenticate using an active account
as it does not exist. Once authenticated, the following commands  are available (as of version `v1.1.15`):

```
The MergeTB CLI Tool

Usage:
  mrg [command]

Available Commands:
  activate      Activate a user or organization
  compile       Compile a model. Return success or compile error stack on failure.
  completion    Generate the autocompletion script for the specified shell
  config        Manage CLI configuration
  delete        Delete things
  dematerialize Dematerialize a realization
  email         Email people
  facility      Facility specific commands
  freeze        Freeze a user or organization
  harbor        Harbor management
  help          Help about any command
  init          Initialize a user
  list          List things
  login         Log in to a portal
  logout        Logout the currently logged in user from the portal
  materialize   Materialize a realization
  membership    Membership commands
  new           Make new things
  nodes         Manage experimental nodes
  pools         Pool specific commands
  push          Push a model to the given experiment repository
  realize       Realize an experiment
  register      Register a new identity with the portal
  relinquish    Relinquish a realization
  show          Show information about things
  sudo          Execute a command as a different user
  unregister    Unregister an existing identity from the portal
  update        Update existing things
  whoami        Show the identity of the logged in user
  xdc           XDC tools

Flags:
      --async               Makes cli usage asynchronous (by overriding command wait to 0)
  -c, --colorless           Disable color output
      --disable-progress    Disable progress bars
  -h, --help                help for mrg
  -j, --json                Output JSON
  -l, --loglevel string     Level to log at. One of panic, fatal, error, warning, info, debug, trace (default "info")
  -s, --server string       MergeTB API server address
      --status-depth int    Override the depth of status display (default nil)
      --sync                Makes cli usage synchronous (if your merge configuration is already synchronous, this flag does not do anything, otherwise sets command wait to the default value of 1h)
      --syncwait duration   Makes cli usage synchronous and overrides the command wait to be the specified duration (default nil)
  -v, --version             version for mrg

Use "mrg [command] --help" for more information about a command.

```

All commands support a `-h` or `--help` argument which shows the usage and help for that specific command.

At execution all commands have a policy applied before they are executed. Based on the account privileges of the user
running the command the action will be allowed or denied. Most commands also are aware of the caller's data in the system.
For instance, when listing projects via `mrg list projects`, only the callers projects will be listed. Other data returned from a call
may be filtered to match the security level of the user and the data accessed.

{{% alert title="Note" color="info" %}}
The `Flags` shown above are global flags that can be used for any command. In the usage strings below, they are 
left out for readablilty.
{{% /alert %}}

## Accounts

### Register

To use Merge, an account is needed. To register for an account use the `register` command.

#### Usage
```
Register a new identity with the portal

Usage:
  mrg register <username> <email> <full name> <institution> <category> <country> [flags]

Flags:
  -h, --help                       help for register
  -o, --organization string        request organization membership
  -r, --organization_role string   request organization role (one of Member,Maintainer,Creator) (default "Member")
  -p, --passwd string              user password
      --usstate string             user US state
```

To register an account the following are required: username, full name, user institution, an account category, a password, and the user's country.
(If the user's country is the United States, then a US State is also needed.)

The configured countries, US states, institutions, (user) categories can be listed via the `mrg list portal ...` command. `mrg list portal -h` for specifics. 
The arguments can be any string though. However we recommend using the values given by the `mrg list portal ...` commands. 

#### Example

```
mrg register olive olive@example.com "Olive Oyl" "University of San Francisco" "Graduate student" "United States" --usstate California -p 123abc!
```

If the password is not given, `mrg` will prompt for it.

The list of institutions and user categories are specific to a Merge portal installation. To see the list of available entries, use the commands
`mrg list portal institutions` and `mrg list portal user-categories`. (These commands do not require authentication.)

`Other` is usually configured to be an acceptable argument as well, but it depends on the Merge portal administration configuring it to be so.

Once an account is registered, the Merge portal operators need to approve and active the account.

{{% alert title="Note" color="warning" %}}
This is only relevant for those who script registering accounts.

Registering is an asynchronous call, so operations on the newly registered user may fail unless you check the status or use the synchronous mode.

However, you cannot check status or use the synchronous mode unless you are logged in.
So, if you want to use the synchronous mode of operation while registering accounts, register accounts *while* you're already logged into an account.
{{% /alert %}}

### Login

Logging into a Merge portal is done, as one would think, via the `login` command. This takes the username and password of the account. If
the password is not given, `mrg` will prompt for it. On success, a time-limited token will be granted to the user. While the token is active,
all other commands can be run.

#### Usage
```
$ mrg login --help
Log in to a portal

Usage:
  mrg login <username> [flags]

Flags:
  -h, --help            help for login
      --nokeys          Do not copy merge generated keys and certificate into ~/.ssh
  -p, --passwd string   User password
```

#### Example

```
$ mrg login olive
Enter password for olive:
$
```

No response indicates success.

A failure:
```
$ mrg login olive -p notcorrect
Error:      PermissionDenied
Message:    The provided credentials are invalid, check for spelling mistakes in your password or username, email address, or phone number.
```


## Experiments

### Listing

```
mrg list experiments
```

Example:

```sh
$ mrg list exp
Name.Project          Description    Mode
------------          -----------    ----
experiment.project                   Public
exp.glawler                          Public
bbb.glawler                          Public
eee.glawler                          Public
```

### Showing

```sh
mrg show experiment <name>.<project>
```

Usage:

```sh
Show an experiment

Usage:
  mrg show experiment <experiment>.<project> [flags]

Flags:
  -h, --help          help for experiment
  -m, --with-models   Save models for each revision
  -S, --with-status   Show compilation status for each revision

```

Example:

```sh
$ mrg show experiment experiment.project
Repo: https://git.sphere-testbed.net/project/experiment
Mode: Public
Description:
Creator: glawler
Maintainers:
Realizations:
  Revision                                    Realizations
  --------                                    ------------
  9eabb626da475f542bf4002cc2d9d1c448f6cafa    rlz.experiment.project
  d3da9590bbc8bedcb6c494ca6d84b57edb1aa9d6    (none)
```

### Creating
```
mrg new experiment 
```

Experiments exist within projects so a project must be specified. The 
syntax for referring to an experiment includes the project name. It is 
of the form `experimentname.projectname`. 

Usage:
```
Create a new experiment

Usage:
  mrg new experiment <experiment>.<project> [description] [flags]

Flags:
  -h, --help   help for experiment
```


## Models

A model is an experiment topology and is read from an experiment's git repository. The
model syntax is documented [here]({{<ref "model-ref" >}}).

### Compiling

A model can be compiled before pushing to an experiment repository via the `compile` command.
If successful the compiled model will be printed to standard out. On failure the
compilation errors will.

Note that this does not push the model to the experiment repository. It is just informational.
To push use `mrg push` or `git push`.

```sh
Compile a model. Return success or compile error stack on failure.

Usage:
  mrg compile <model-file> [flags]

Flags:
  -h, --help    help for compile
  -q, --quiet   Do not show the compiled model on success.

```

Successful example (`-q` argument is given to quiet output)

```sh
glawler@river:~$ mrg compile -q model.py
glawler@river:~$ echo $?
0
```

Unsuccessful example:

```sh
glawler@river:~$ mrg compile model.py
Title:        MX failed to compile
Detail:       Compiliation Failure
Evidence:     Exception: 'Network' object has no attribute 'Connect'

Timestamp:     2022-02-14 20:04:11.560308413 +0000 UTC m=+5998.900641627
```

### Pushing

A model can be pushed to an experiment via `git` or `mrg`. To push via `mrg` use the
`mrg push ...` command.

```sh
Push a model to the given experiment repository.

Usage:
  mrg push <model-file> <experiment>.<project> [flags]

Flags:
      --branch string   Repository branch to push the model to. (default "master")
  -h, --help            help for push
      --tag string      Tag the commit with the given tag.
```

For example to push the model in `./model.py` to the master branch in experiment
`hello.murphy`:

```sh
mrg push ./model.py hello.murphy
Push succeeded. Revision: fb90c2aa1a19a07410d39ad373c842e7ee544586
```

If `--tag` is given the revision will be tagged with the given tag:

```sh
mrg push ./model.py hello.murphy --tag v1.2.1
```

This creates a git tag on the revision and can be used to
realize the model.

{{% alert title="Note" color="warning" %}}
Although the `push` usage has a `branch` argument, the command only supports pushing to
the `master` branch. Pushing to a non-master branch will be in a future release.
{{% /alert %}}

## Realizations

### Realizing

```sh
mrg realize <realization>.<experiment>.<project> revision|tag <reference> [flags]
```

Here `<reference>` is the git revision or git tag of the source repository you would like to
realize. For example to create the realization "henry" with a revision tagged "olive" in
the experiment `hello` in the project `murphy`:

```sh
mrg realize henry.hello.murphy tag olive
```

The same but using the revision:

```sh
mrg realize henry.hello.murphy revision bbd67f119672bc0cedc8fd97476e6aeea7458a6c
```

### Listing

To list all realizations you have access to use `list `.

```sh
mrg list realizations
```

Example:

```sh
$ mrg list realizations
Realization               Nodes    Links    Status
-----------               -----    -----    ------
rlz.experiment.project    5        2        Succeeded
```

### Relinquishing

Relinquishing frees all resources held by a realization. If there is an active
materialization associated with the realization it will be dematerialized
before the realization is relinquished.

```sh
mrg relinquish <realization>.<experiment>.<project>
```

### Showing

```sh
mrg show realization <realization>.<experiment>.<project>
```

## Materializations

### Listing

```sh
mrg list materializations
```

### Showing

```sh
mrg show materialization <realization>.<experiment>.<project>
```

### Generating files

`mrg nodes generate` allows you to generate configurations from a realization, including INI style Ansible
inventories and etchosts-style name-to-IP mappings:

```sh
mrg nodes generate inventory <realization>.<experiment>.<project>
```

```sh
mrg nodes generate etchosts -p exp- <realization>.<experiment>.<project>
```

### Rebooting/reimaging nodes

`mrg nodes reboot` allows you to reboot or reimage nodes from a materialization:

```sh
mrg nodes reboot <realization>.<experiment>.<project> [<nodes>...]
```

## XDCs

### Listing

```sh
mrg list xdcs
```

### Attaching

```sh
mrg xdc attach <xdc>.<project> <realization>.<experiment>.<project>
```

### Detaching

```sh
mrg xdc detach <xdc>.<project>
```

## Sending Email

A Merge portal supports sending email to users, project members, and organization members. In general, this ability 
is limited by policy - both user and project, organization policy. Project and organization maintainers and creators
can send email to all members of a project or organization. User can send email directly to others users only
if they have the ability to update that user's inforamation. So this is limited to Organization maintainers or
creators. 

Usage:
```sh
Email people

Usage:
  mrg email [command]

Available Commands:
  delete       Delete an existing email request. The ID is found in the request status. Rerun the send command with -S to see it
  organization Email all users in an organization. Content is path to file or "-" for stdin.
  project      Email all users in a project. Content is path to file or "-" for stdin.
  users        Email a list of users. Content is path to file or "-" for stdin.

Flags:
      --contentType string   Repository branch to push the model to. (default "text/plain")
  -h, --help                 help for email
```

{{% alert title="Tip" color="primary" %}}

When sending emails, the content flag is a path to a file or a single dash (`-`). If a dash 
is given `mrg` will read the email content from standard in. 

{{% /alert %}}

### Sending 

Syntax for sending to a project, organization, or user is the same, but for the command name. 

Project Usage:
```
Email all users in a project. Content is path to file or "-" for stdin.

Usage:
  mrg email project <project name> <subject> <content> [flags]

Flags:
  -h, --help          help for project
  -S, --with-status   Show task status of sending email
```

Example:
```
$ mrg email project mailtest "Welcome to the Mailtest Project" ./welcome.txt
Name                                                   Desc                          Status     Creation                        Last Updated
EMail: PwmEBveZ+ImiqL840QplborymOopJcUyZUHRSEmHO8c=    EMail To: Project mailtest    Success    Thu Jan 30 17:34:37 UTC 2025    Thu Jan 30 17:34:38 UTC 2025
```

Organization usage:
```
Email all users in an organization. Content is path to file or "-" for stdin.

Usage:
  mrg email organization <organization name> <subject> <content> [flags]

Flags:
  -h, --help          help for organization
  -S, --with-status   Show task status of sending email
```

Sending to users is slightly different as you list one or more users. The subject and content is the same. 

Send to users usage:
```
Email a list of users. Content is path to file or "-" for stdin.

Usage:
  mrg email users <username 1> <username 2> ... <username N> <subject> <content> [flags]

Flags:
  -h, --help          help for users
  -S, --with-status   Show task status of sending email
```

{{% alert title="Content Type" color="info" %}}

Use the `--content-type` argument to specify the email type. If sending plain text (the default) you do not
need to specify the type. If the content is HTML, use "text/html". 

{{% /alert %}}

### Delete

Usage:
```sh
Delete an existing email request. The ID is found in the request status. Rerun the send command with -S to see it

Usage:
  mrg email delete <id> [flags]

Flags:
  -h, --help   help for delete
```

If email fails to end for whatever reason, the command will show an error. The error contains a hash value in the 
`EMail: ...` field.  The portal will continue to try to resend the email periodically. If you wish to cancel the email,
use the hash given in the status to delete the email task. 

Example:
```sh
$ mrg email project mailtest "Welcome to the Mailtest Project" ./welcome.txt
Name                                                   Desc                          Status    Creation                        Last Updated
EMail: PwmEBveZ+ImiqL840QplborymOopJcUyZUHRSEmHO8c=    EMail To: Project mailtest    Error     Thu Jan 30 17:27:34 UTC 2025    Thu Jan 30 17:27:34 UTC 2025
$
$ mrg email delete PwmEBveZ+ImiqL840QplborymOopJcUyZUHRSEmHO8c=
```

## Configuration

### Server/Port

```
mrg config set port $PORT
mrg config set server $SERVER
```

### Status-Depth

This is relevant to versions of `mrg` of `v1.3.0+`.

In Merge, there is a status tree associated with high level tasks (like creating a materialization, an XDC, etc.),
as they rely on a number of subtasks to be complete before the high level task is complete.

The status of a level is equal to the "worst" status of its children,
so viewing the tree at a high level provides a summary of what's going on,
while viewing the tree at a low level specifically tells you what went wrong.

An example is that if everything except for your nodes in a materialization do not come up,
then your materialization is not considered successful until all of your nodes come up.

This displays very nicely in the Webgui as you can click to see more information but is a little trickier to display in the cli.

To emulate this behavior in the cli, you can configure the cli to print at depth that you want to see.
Negative numbers wrap around from the end, so `-1` means the tasks at the bottom of the tree.

This means that the default value of `0` will act as a summary of the entire object,
while something like `-1` allows you to see the status of actual specific tasks.

Note that if you use negative numbers other than `-1`, then you have escape the argument as a flag by doing the following:
`mrg config set status-depth -- -2`.

You can also override it for a specific command with `--status-depth`.

You can set it with:
```
# only works if it's positive
mrg config set status-depth $INTEGER

# will work if it's positive or negative
mrg config set status-depth -- $INTEGER
```

### Sync and Async
As of versions of `mrg` of `v1.3.0+`, the cli operates synchronously by default.

You can change this configuration by using the following commands:
```
mrg config set sync
mrg config set async
```

You can also override this configuration value on a per-command basis by using the following global flags:
```
--sync
--async
```

### Command Wait

This is relevant to versions of `mrg` of `v1.3.0+`.

When operating synchronously, the cli has a limit on how long it waits, the default is `1h`.
The default is `1h`, valid time units are `ms`, `s`, `m`, `h`.

When the command completes or the specified time elapses, it will print the latest received status.
The command is only successful if it completed within the specified amount of time.

When operating asynchronously, this value is set to `0`.

You can also override it for a specific command with `--syncwait`.

You can set it with:
```
mrg config set command-wait $DURATION
```
