---
title: "Closure of the SRCF Desktop service"
date: 2017-07-01T22:11:07+00:00
authors: ["Malcolm Scott"]
---
_Note: this post has been migrated from our previous wiki documentation._

The sysadmins have decided to retire the SRCF Desktop service permanently on 29th July 2017 due the service being in urgent need of substantial development work, which due to steadily declining usage would not be the best use of limited sysadmin time.

We apologise for any inconvenience caused to the remaining users of this service. We are of course happy for you to run graphical applications on the main SRCF shell server, shell.srcf.net, via VNC and/or SSH; we offer some [suggestions on how to use VNC on the shell server](https://wiki.srcf.net/VirtualDesktop).

<!--more-->

## Background

The reason that the service needs urgent development work is that it is based on an obsolete and abandoned software platform -- NoMachine's NX 3, -- with no direct upgrade path. We are currently prevented from upgrading the server's operating system without breaking the service, and cannot make any improvements to the service without substantially reimplementing it.

We are also aware that the client-side software works increasingly badly on modern systems, relying by default on deprecated and insecure technology such as in-browser Java applets, but both the NoMachine client and the OpenNX third-party client have been abandoned by their developers.

(If you are interested in helping us to maintain a desktop service or our other systems, please consider joining the sysadmin team; email sysadmins@srcf.net if interested.)
