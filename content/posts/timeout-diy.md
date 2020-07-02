---
title: "But how *does* Timeout really work?"
date: 2020-06-04T18:21:32+00:00
tags: ['timeout', 'technical']
authors: ["Matias Silva"]
draft: false
---
Do you want to know how Timeout works? Want to contribute? Look no further than this blog post!

<!--more-->

The following is a collection of insights we've gained by developing Timeout over the past month. It's not a getting starting guide. This is ideally meant for someone who has set up their own BigBlueButton server with or without the Greenlight frontend. If not, continue reading as I'll link to some helpful documentation where you can learn more. I've also written this because Timeout has started to grow (yay!) and we need to keep track of things *somewhere*. 

Meet the maintainers of Timeout:

* Matias Silva
* Malcolm Scott
* Edwin Balani
* Charlie Jonas (Ruby on Rails consultant)

Do you want to help? Contribute? Learn? Join us on IRC (#timeout) or [Discord](https://discord.com/invite/et353sv)!

- [A bird's eye view](#a-birds-eye-view)
- [The nitty gritty details](#the-nitty-gritty-details)
  - [Hardware](#hardware)
  - [Software](#software)
- [Useful information](#useful-information)
  - [Recording](#recording)
    - [Motivation](#motivation)
    - [A summary](#a-summary)
    - [Moving to an offloader](#moving-to-an-offloader)
  - [Running the frontend](#running-the-frontend)
  - [Dealing with TURN](#dealing-with-turn)
  - [Using Ansible](#using-ansible)
    - [Where we started](#where-we-started)
    - [Using a vault](#using-a-vault)
    - [The technical details](#the-technical-details)
  - [Customizations](#customizations)
    - [Adding users](#adding-users)

# A bird's eye view

Timeout is a collection of applications working together to make robust, open-source and reliable video conferencing possible. Explained simply, it runs several instances of BigBlueButton with a modified frontend.

The architecture is as follows:
* A pool of BigBlueButton hosts
* A modified version of Greenlight
* A loadbalancer (scalelite) for the hosts
* Two external TURN servers

If any of the above terms seem unfamiliar to you, I suggest you read BigBlueButton's [great and improving documentation](https://docs.bigbluebutton.org).

A brief explanation of each component follows:

**BigBlueButton**

A fully-fledged video conferencing system built in a variety of tools. Its main components are:

* bbb-web => an API to which calls can be made to create, join or query details about meeting.
* bbb-html5 => a meteor (node) app that provides the HTML5 client and talks to a server
* bbb-apps-* => various apps that tie together different open source software such as etherpad, kurento, and FreeSWTICH

BBB uses WebRTC for realtime video and screen capture streaming.

It is built by Blindside Networks and released as open-source software.

**Greenlight**

A front-end that makes the above API calls. It is NOT BigBlueButton. This is a common source of confusion as it is often shipped with BigBlueButton and is displayed on the BBB's demo and test sites. Greenlight allows users to create and start rooms without having to make API calls and generate nasty SHA hashes by hand. Instead, it abstracts the BBB API call behind a nice UI and implements the concept of a "room", as you would expect from other video conferencing platform. This is what makes BBB so powerful. You can integrate it with any front-end, even your own! Other front-end examples include a Moodle integration and a WordPress integration.

It is written in Ruby using the Rails framework and is also built by Blindside Networks.

**Scalelite**

A load balancer for a pool of BBB servers. It interfaces with Greenlight and other front-ends as an API and then allocates a server for a session based on server load.


# The nitty gritty details

## Hardware
The SRCF has several industry-grade servers which it uses to host its services. Most are virtualized with the Xen hypervisor to accommodate a variety of virtual machines but some are dedicated (albeit virtualized) machines as is explained below:

* Ping => BBB host on dedicated machine (8 vCPUs, 32GB RAM)
* Tuit => BBB host on dedicated machine (8 vCPUs 32GB RAM)
* Latency => Recording offloader hosted on our VM cluster (12 vCPUs, 16GB RAM)
* Gateway => Frontend hosted on our VM cluster, thunder (4 vCPUs, 8GB RAM)
* Relay => TURN server for ping (2 vCPUs, 4GB RAM)
* Socket => TURN server for tuit (2 vCPUs, 4GB RAM)

Why *ping* and *tuit*? Well, we tried to ping but we got a timeout and when we wanted to fix it, we said we'd eventually get a round tuit...

## Software

For remote server management, we use Ansible. It's simple and easy to use. I got started with adapting an [existing playbook](https://github.com/stadtulm/a13-ansible) and the rest of the team quickly got to work customizing it. 

BigBlueButton itself uses a wide vaiety of other open-source software such as Etherpad, Meteor and FreeSWITCH which are written in a variety of languages. For the frontend, we use a modified version of Greenlight and Scalelite for the loadbalancing, both released by Blindside Networks, the company behind it all. The TURN servers are set-up using Coturn, which is in turn (heh) installed and managed by our Ansible role. Greenlight and Scalelite run entirely as system services (systemd) on our setup - we didn't like the *dockerize all the things!* approach taken by the devs so I fiddled with and in some cases wrote the `.service` files to run the would-be docker containers as daemons. 

# Useful information

## Recording

### Motivation

Our recording pipeline is perhaps the greatest modification we've made to BigBlueButton. Due to limited physical space, we can't quickly expand our operation if we see a spike in users. We want ping and tuit to be dedicated BBB hosts and not be busy crunching numbers for video encoding and recording processing. Storage is also limited on the machines we used for the BBB hosts so we could not reasonably support any more than a few measly recordings. Therefore, we decided to offload recording processing to a different machine, latency. 

You can check BBB's documentation for slightly out of date information on how recordings work. The major difference is the introduction of a "sanity check" which is not detailed in the documentation.

### A summary

Essentially, the bbb-record package installs a timer (`bbb-record-core.timer`) that fires and runs `bbb-record-core.target`. This then runs 5 record-and-play (rap) workers that either archive, perform a sanity check, process or publish recording files (the odd one out is the events worker, which also hasn't been documented and seems to gather all events separately so that further workflows are enabled, such as podcast and screenshare). Their current status is tracked by the existence of a `.done` file extension in a directory for each stage of the recording pipeline. periodically checks whether any new files have been dumped in the [relevant locations](https://docs.bigbluebutton.org/dev/recording.html#media-storage) for Kurento and FreeSWITCH. 

### Moving to an offloader

Moving this process to an offloader requires a few considerations:

**How do we share files between the hosts and latency?**

Mount all the relevant locations for raw recording on a shared file system (NFS). In our case, this is NetApp that was kindly donated.

**What actually runs on the hosts?**

The archive and sanity check processes need to run on the BBB hosts as otherwise there would be a clash between the hosts. In other words, any time files are dumped onto the mounted (shared) file system, all instances of `bbb-record-core.timer` on every host would fire even if that recording didn't come from that specific host. To overcome this, these two processes are run on the BBB hosts and the archive/ directory is made local to that host.

**And what about the offloader?**

Once the sanity check is done, a `.done` extension is added to the file name (which is the long internal meeting ID). The timer on latency picks this up and starts work on processing the recording. This works because we have masked the `bbb-rap-process-worker` and `bbb-rap-publish-worker` services on the hosts. Equivalently, the `bbb-rap-event-worker`, `bbb-rap-sanity-worker` and `bbb-rap-archive-worker` have been masked and disabled on latency. This means that latency is *technically* also a BBB host -  we didn't want to fiddle about with the packages (which are already a mess) so we just installed BBB on latency and sealed it from the outside world.

**What's a workflow?**

A workflow is essentially a method through which media is presented. The default workflow is "presentation" and this includes all the aspects of the meeting: webcams, screenshare, audio, etc. There are three more known workflows: podcast, notes and screenshare. These are undocumented and are very obscure. They are installed and activated supposedly via some hidden packages which [I've linked to here](https://groups.google.com/forum/#!searchin/bigbluebutton-dev/bbb-playback-notes%7Csort:date/bigbluebutton-dev/xTSmfi9Wbdo/fwumuE84AwAJ) because I know I will forget them myself if I don't.

**How do the users see the recordings?**

Now, we move to configuring scalelite. The first step is to add a post-publishing script that moves the files from one mounted directory to another. Note that latency has `/var/bigbluebutton/`  and `/mnt/scalelite-recordings` mounted to certain volumes on the NFS while gateway has the latter directory mounted to `/var/bigbluebutton/` as a usual host would have. The recording files are moved about a bunch in the following way:

* Raw files are dumped in respective Kurento and FreeSWITCH directories
* Archiving collects them and dumps them in `/var/bigbluebutton/recording` (which is mounted to volume on the NFS)
* Processing and publishing dumps them in `/var/bigbluebutton/published`
* The post-publish script temporarily stores files in `/var/bigbluebutton/recording/scalelite` and then transfers them to `/mnt/scalelite-recordings/var/bigbluebutton/spool`

Then what about the UI? Greenlight can see the recordings and users can see  the entries, but what actually plays them?

For this, we *should have* installed the `bbb-playback-*` packages mentioned above and that is indeed what was outlined in the documentation. However, since those packages are for xenial and run focal, there was an obvious conflict. We ended up copying over the HTML and JS scripts that pieces all the files together in the web recording viewer.

It might seem like a mess, but remember the developers of BBB and Scalelite did not have  storing the raw and published recordings on NFS in mind! We could improve this but it *works* and we don't want to mess about too much with it.

After all this is done, Scalelite polls the spool directory for recordings and then moves them to a directory based on the workflow used (usually presentation). This polling is done via a `systemd` service, which I *undockerized*.

## Running the frontend

The frontend consists of Greenlight and Scalelite and their PostgreSQL databases. Getting the two to run on the same machine was a foreign idea at first: neither of the two playbooks we looked at had support for this. The reason why it hadn't been done was because of an nginx proxy clash.

The solution was to use two `server` blocks in our nginx configs, one pointing to a virtual host with `server_name` timeout.srcf.net and the other to gateway.timeout.srcf.net, which is our Scalelite API endpoint. These configs are copied over by Ansible and updated when needed.

Scalelite is essentially an API to Greenlight. It implements many of the same requests as a BBB host can take and in effect is how it so cunningly integrates with Greenlight by a simple replacement of the API endpoint URL. Scalelite and is polled by Greenlight, which then assigns it to one of the BBB hosts for a call. There are three systemd services that we run for Scalelite: the poller, the API, and the recording transferer. There's a fourth one which I've sort of integrated into our nginx configs (and our dodgy installation of the HTML and JS for recording playback) that was a docker container.

One tiny thing: since we're running Scalelite as a service and not in a docker container, we need to export a few environment variables when using `rake` commands to peek into its status. The command to do so is: `set -o allexport; source .env; set +o allexport; bundle exec ./bin/rake`

## Dealing with TURN

We run two external TURN servers in addition to the internal ones running on each host. Why? Because some schools/networks have very restrictive firewalls, allowing only traffic over SSL/TLS on port 443. However, setting up a TURN server listening on port 443 clashes with nginx when we want to deliver pages securely over HTTPS (this we found out the hard way when we rebooted our machine and nginx wouldn't start up). So instead, the local TURN servers listen on port 3479 and port 5349 for traffic over TLS. This way, we accommodate all possible users, even in the event that their firewall is very restrictive. Installation of these servers is done through Ansible, which installs Coturn. The n0emis BBB role allows us to specify custom ports for coturn servers and additional TURN servers if we want to. Presently, each host has its own external TURN server but this may very well change if we happen to add another host. 

## Using Ansible

### Where we started

Before even starting work on Timeout, we knew the system had to be easily scalable. We didn't want much fussing about with configurations - this just leads to human error and more lost hours in debugging. As I mentioned before, we started by doing some basic research on what was out there. We found two very good Ansible playbooks with roles that were suited to a custom installation of BBB with almost everything that we needed. We ended up forking one called `a13-ansible` which is made by the folks over at Ulm in Germany. They've provided us with some very useful support and Timeout would have been almost impossible without them. We cleared out everything that we didn't need from our fork and began work on building our playbook.

### Using a vault

Everyone has secrets they want to keep from others. After all, if watching Pretty Little Liars in my teenage years taught me anything it's that *"two can keep a secret if one of them is dead"*. Thankfully, nothing so morbid has to happen in the world of computers. 

*Secrets* in this case refers to passwords or special strings of random alphanumeric characters needed by the various software (GL, Scalelite, Coturn) we run to do internal authentication. Our secrets are stored in the `vars.yml` file as encrypted strings. You can encrypt a string like so `ansible-vault encrypt_string --vault-password-file a_password_file 'foobar' --name 'the_secret'`. They are then decrypted on runtime using the `vault_passsword` which is stored locally and not uploaded to GitHub. Therefore, we can safely share files online (GitHub) without ever exposing the real secrets. Neat!

### The technical details

Information on running our playbooks and how to do so can be found on our [GitHub repository for Timeout](https://github.com/srcf/timeout). Ansible is intended to be purposefully easy to read and understand, so picking up on what each instruction is should be easy enough.

## Customizations

### Custom room URLs

You can change the room uid by doing the following with root permissions on gateway:

```
cd /var/www/greenlight
set -o allexport; source .env; set +o allexport; bundle exec rails c
Room.find_by(uid: "CURRENT_ROOM_ID").update_attribute(:uid, "NEW_CUSTOM_ID")
```

<!--Need to add stuff about our custom Greenlight installation-->
