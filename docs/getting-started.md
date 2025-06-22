---
title: "Accounts"
linkTitle: "Accounts"
weight: 1
description: >
  Getting setup to use Merge
---

This guide covers the basic things you need to do to get started with Merge.

{{% alert title="Attention" color="warning" %}}
This guide assumes you are using the reference portal at `sphere-testbed.net`. If you are using a
different portal, substitute addresses in this document that reference `sphere-testbed.net` accordingly.
Consult your project leader if you are not sure of the portal address.
{{% /alert %}}

{{% alert title="Tip" color="info" %}}
The Merge Portal uses its own identity server to manage user identities. This is much like having
a Google or Gitlab account, but in a server created for Merge Portals. This identity server manages
your identity data and authenticates your communications to the Merge Portal. Note that the account
made here is _not_ a Merge Portal account. It is an identity account. Later in this walk-through
portal admins will use this identity information to create a portal account.

In the future Merge will support third-party identity allowing merge accounts to be created using,
for example, github or google identities.
{{% /alert %}}

## Account Setup


The first step to experimenting on a Merge testbed is to create an account on the Merge portal.
Follow the instructions either <a href="#account-creation-through-launch">using "Launch"</a> (the graphical
web interface) or through the <a href="#account-creation-through-the-cli">Merge command line
interface (CLI)</a>.

### Account Creation through Launch

Navigate to the Merge "Launch" GUI at <a
href="https://launch.sphere-testbed.net">https://launch.sphere-testbed.net</a>. You'll be greeted with a page
that looks much like this

![](../hello-world-gui/01-login.png)

Click the `Sign up` link to load the account registration page.

![](../hello-world-gui/02-new-account.png)

Fill in your account details:

- `Email Address` - the email address for the new account.
- `Password` - the account password. The password will be rejected with a reason if it is not strong enough.
- `Password Confirmation` - the account password again to confirm it has been typed correctly
- `Username` - the account username. This username is used to login to the portal and on all testbed nodes.
- `Affliation` - institution to which you belong.
- `Position` - your position within your institution.
- `Name` - your full name.
- `Testbed Organization` - an existing organization in the merge portal you want to join. 

{{% alert title="Note" color="info" %}}
The password you choose will be used to login to Launch _and_ the Merge command line utility `mrg`.
If you do not use a command line aware password manager, you may want to choose an easier-to-type
password as you may be typing it in on the command line.
{{% /alert %}}

![](../hello-world-gui/03-new-murphy-account.png)

Once done, click `Sign Up`.

### Activate Your Merge Portal Account

Send a notification to the Merge portal administrators to have your account created and activated. If you joined an organization while registering for a new account, contact that organization's administrators.  They will use the Identity account created above to create an account for you on the Merge Portal. Speak with your project leader for up-to-date information on how best to contact them.

Until your account is activated, you'll see that you do not have access to any information on the portal. You can login, but you will not have access to any information within the portal. So pages in Launch will show nothing, or an access error.

![](../hello-world-gui/04-no-access.png)

Once your account has been activated, your data will load and you are ready to start using Merge!

### Account Creation through the CLI

First, download the Merge CLI `mrg` for the operating system and CPU
architecture of your machine at the <a href="https://gitlab.com/mergetb/portal/cli/-/releases/permalink/latest">latest release page</a>.

### Configuring the API endpoint

The `mrg` CLI needs to be configured to know how to communicate with the portal. This is done by telling `mrg` the `server` of the portal.
The server address can usually be constructed by prepending "grpc." to the portal fully-qualified name (in the case of SPHERE testbed, this is `sphere-testbed.net`; e.g.,:

```shell
mrg config set server grpc.sphere-testbed.net
```

As noted above, consult your project leader for the appropriate portal address.

## Register account

Then, register your account using the `mrg register` command. The fields used to  register on the command line are the same as above in Launch. 
For example, to create a user named "murphy" with email "murphy@random.org", affiliation "USC", position "Research Programmer", and password "muffins1701":

```shell
mrg register murphy murphy@random.org USC 'Research Programmer' -p muffins1701 
```

If you are joining a testbed organization, you specify that via the `--organization [name]` argument. 

```shell
mrg register murphy murphy@random.org USC 'Research Programmer' -p muffins1701 --organization 'USC201`
```

`mrg` has a built in help system. You can add `--help` to any command to get more information about that command:

```shell
$ mrg register --help                                                              
Register a new identity with the portal                                                                            
                                                                                                                   
Usage:                                                                                                             
  mrg register <username> <email> <affiliation> <position> [flags]                                                 
                                                                                                                   
Flags:                                                                                                             
  -h, --help                  help for register                                                                    
      --name string           user full name                                                                       
      --organization string   request organization membership                                                      
  -p, --passwd string         user password                                                                        
                                                                                                                   
Global Flags:                                                                                                      
  -c, --colorless         Disable color output                                                                     
  -j, --json              Output JSON                                                                              
  -l, --loglevel string   Level to log at. One of panic, fatal, error, warning, info, debug, trace (default "info")
  -s, --server string     MergeTB API server address                                                               
```

## Account Approval

Once you have created an account using either the web interface or the CLI, you should send a
notification to the Merge portal or your organization administrators to have your account approved. Speak with your
project leader for up-to-date information on how best to contact them.

Once your account has been approved, you are ready to start using Merge!
