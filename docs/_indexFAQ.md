---
title: "Frequently Asked Questions"
linkTitle: "Frequently Asked Questions (FAQ)"
weight: 99
description: Questions and their answers.
---

{{% pageinfo %}}
This section is under construction.
{{% /pageinfo %}}

## Launch GUI/Browser issues

### no access token provided

You may see an error message like this when using the Merge launch/browser interface:

```
{
    "code": 5,
    "message": "no access token provided",
    "details": [],
    "url": "https://api.sphere-testbed.net/users"
}
```

This is a known issue and we are working to track it down. Something causes expired or invalid login
tokens to remain cached in the browser. The workaround to fix this is to logout and "hard-refresh"
the webpage. On firefox or chrome, you do this via CTRL-<F5>

Anecdotally, most users seem to find firefox to be the friendlist browser, though we have not done a
systematic analysis of browser and OS compatibility at this time.

## Other issues

### EFI variable error on apt upgrade

When upgrading a node via apt, you see an error like the following:

```
grub-install: warning: Cannot set EFI variable Boot0009.
grub-install: warning: efivarfs_set_variable: failed to open /sys/firmware/efi/efivars/Boot0009-8be4df61-93ca-11d2-aa0d-00e098032b8c for writing: Read-only file system.
grub-install: warning: _efi_set_variable_mode: ops->set_variable() failed: Read-only file system.
grub-install: error: failed to register the EFI boot entry: Read-only file system.
```

Merge nodes do not permit modifying EFI variables. The Merge infrastructure needs to preserve these so that we can provide a reliable boot procedure. When using ansible for experiment automation, you can workaround this limitation through the following:

```yaml
# hold back kernel/grub updates
- name: Holdback kernel and grub-efi packages
  ansible.builtin.dpkg_selections:
    name: "{{ item }}"
    selection: hold
  with_items:
    - linux-generic
    - grub-efi
    - grub-efi-amd64
```

This is akin to apt-mark hold on debian/ubuntu systems, which you can use if you are running commands on nodes directly. Once this is done, `apt upgrade` will no longer try to upgrade packages that try to modify EFI variables.

## XDC issues/FAQs

### Troubleshooting XDC Attachments

#### Intro - what to look for

A healthy XDC attachment will have two things on the XDC itself, a wireguard interface and an `/etc/resolv.conf` that contains the materialization DNS server and search string. The wireguard interface will always start with `wg` and will not be `DOWN`, but `UNKNOWN`. This is fine. 

An attached XDC will have an interface whose name starts with `wg`, To view the interfaces, use the `ip` command. 

```
root@xdc:/# ip -br -c link                                                         
lo               UNKNOWN        00:00:00:00:00:00 <LOOPBACK,UP,LOWER_UP>           
eth0@if151       UP             8a:0b:47:29:5c:a1 <BROADCAST,MULTICAST,UP,LOWER_UP>
wgdcgwo          UNKNOWN        <POINTOPOINT,NOARP,UP,LOWER_UP>                    
root@xdc:/#                                                                        
```

In this instance the wireguard interface is named `wgdcgwo`.

An unattached XDC interface list does not have an iinterface whose name start with `wg`. The list will look something like this:
```
root@xdc:/# ip -br -c link                                                         
lo               UNKNOWN        00:00:00:00:00:00 <LOOPBACK,UP,LOWER_UP>           
eth0@if11        UP             0e:d7:40:30:74:7b <BROADCAST,MULTICAST,UP,LOWER_UP>
root@xdc:/#                                                                        
```

An attached XDC will have two servers and an extra search string in  `/etc/resolv.conf`:
```
root@xdc:/# cat /etc/resolv.conf                                                                                   
search infra.real.intro.project1 mergev1-xdc.svc.cluster.local svc.cluster.local cluster.local mgmt.mdr.sphere-testbed.net
nameserver 172.30.0.1                                                                                              
nameserver 10.2.0.10                                                                                               
options ndots:5                                                                          
root@xdc:/#               
```

The experiment DNS server is always `172.30.0.1`. The first `search` entry will be the domain of the materialization the XDC is attached to.

On an unattached XDC, `/etc/resolv.conf` will look something like this:
```
root@xdc:/# cat /etc/resolv.conf                                                         
search mergev1-xdc.svc.cluster.local svc.cluster.local cluster.local mgmt.mdr.sphere-testbed.net
nameserver 10.2.0.10                                                                     
options ndots:5                                                                          
root@xdc:/#                                                                              
```

Note there is only one `nameserver` and there is no materialization specific search string,

If there *is* a problem with an XDC attachment, you will likely not be able to use `mrg` to fix the problem directly. On an attached XDC, DNS goes through the tunnel. With a broken tunnel, DNS is not likely to work well. You will need to use `launch` or `mrg` on another machine. 

#### Problem: wireguard interface is `DOWN`

1) If the wireguard interface is `DOWN`. When you run `ip -br -c link` you will see the `wg...` interface is `DOWN`. To fix this, detach then reattach the XDC. You will likely not be able to do this on the XDC itself as the tunnel is down and DNS goes over the tunnel. So use `launch` (the GUI) or the command line client `mrg` on any machine except the problematic XDC. If the xdc is `xdc.project1` and the materialization is `rlz.intro.project1` you would do:

```
# assumes you are logged into merge via `mrg login ...`
$ mrg xdc detach xdc.project1
$ mrg xdc attach xdc.project1 rlz.intro.project1
```

After this confirm the attachment is OK by looking at the wireguard interface and confirming it is no longer `DOWN`. (It will also have a new name as it has been recreated by Merge.)

#### Problem: incorrectly formatted `/etc/resolv.conf` file

The `/etc/resolv.conf` is mangled in someway. Merge will edit the file in place during attach/detach. Occasionally this goes wrong and the file is incorrect. If the XDC is attached, the file should have the format above with two `nameserver` entries and a materialization-specific `search` string. If you to do not see that, edit the file and add them. The `nameserver` will always be `172.30.0.1`. The `search` string will be the name of the attached materialization prepended with `infra.`.   

### Ansible error: "Message: Cannot write to ControlPath $HOME/.ansible/cp."

Check to make sure the `.ansible` directory exists in your home
directory, and that its owner and group is you (not root):

```bash
# check if the directory exists and its ownership
$ ls -ald ~/.ansible

# create the directory if it does not exist
$ mkdir ~/.ansible

# change the user and group ownership of directory to yourself
$ sudo chown -R $(id -u):$(id -g) ~/.ansible
```

### what xdc am i on?

```bash
export XDC=$(uname -a | cut -d' ' -f2 | cut -d'-' -f1)
echo ${XDC}
≈ç```

### what materialization is my xdc connected to? (lighthouse)

```bash
export MERGE_MATERIALIZATION=$(head -1 /etc/resolv.conf | cut -d' ' -f2 | grep -Ev "cluster.local|test-cluster.redhat.com")
echo ${MERGE_MATERIALIZATION}
```

Result will be empty if your XDC is not connected to a materialization.

