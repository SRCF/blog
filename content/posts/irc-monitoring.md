---
title: "IRC and monitoring"
date: 2020-10-05T06:40:00+00:00
tags: ['monitoring', 'irc']
authors: ["Dexter Chua"]
---
The SRCF has recently been plagued by a variety of hardware issues. To keep an
eye on our services, we employ a variety of monitoring software such as
[Icinga](https://icinga.com) and [Munin](http://munin-monitoring.org/).

Monitoring is only useful if we get notified when we encounter problems. In the
past, we relied on email and SMS notifications. For better or for worse, some
of the sysadmins check IRC more frequently than their email. Recently, we
started making Icinga and Munin send their notifications to a dedicated IRC
channel: `#alerts:irc.srcf.net`.

<!--more-->

# The set up
The set up is fairly simple. Icinga and Munin's notification systems let us
specify an arbitrary command to run whenever it wants to send out a
notification. To make use of this, we write a simple script that

 1. Joins an IRC channel
 2. Listens to a port
 3. Forwards all messages sent to the port to IRC.

The code is fairly straightforward and can be found on
[GitHub](https://github.com/SRCF/irc-forward/blob/master/irc-forward.js). It
will be discussed further in the next section.

On the IRC side, the `#alerts` channel only allows voiced users to speak. This
ensures the messages in the channels are genuinely alerts and not some other
users chatting. Our script automatically authenticates with `NickServ` and is
then auto-voiced by `ChanServ`.

# On IRC bots
In this section, I'll go over the IRC part of the script, just to emphasise how
easy it is to write IRC bots. The code here is a mildly simplified version of
the actual script.

To connect to an IRC server, we first initiate a TCP connection to
`irc.srcf.net:6667`:
```js
const net = require("net");
const client = net.connect({
    host: "irc.srcf.net",
    port: "6667",
});
```
Before we receive any messages from the server, we must first identify ourselves:
```js
client.write('NICK icinga2\r\n');
client.write('USER icinga2 0 * :icinga2\r\n');
```
This sends two commands to the IRC server, which are terminated by `\r\n`. The
first one tells the server what we want our nick to be, and the second sets
some user properties, whose values are not important for us (but must be set).
Once these are sent, we are now all set to interact with the IRC server.

> **Remark**: For those more familiar with web development, as a somewhat
> backwards analogy, a TCP connection works like a websocket, except the data
> isn't chunked into "messages"; there is a continuous stream of data going in
> both directions. A protocol (e.g.  IRC) has to pick its own way of separating
> the data into individual messages. For IRC, messages are delimited by `\r\n`.
> (Of course, websockets are in fact TCP connections with a specified way of
> delimiting messages)

We begin by joining the alerts channel:
```js
client.write('JOIN #alerts\r\n');
```
We would now receive any messages that are sent to the #alerts channel.
Messages will come in lines that look like
```
:sending_user PRIVMSG #alerts :the message
```
Our bot's job is to send messages to the channel, so it shall just ignore all
such lines from the server.

The only messages we have to respond to are the `PING` messages. These are sent
by the server to ensure the client is still around; if we fail to respond to
them in a timely manner, then the IRC server will drop our client. The messages
will come in the form
```
PING :irc.srcf.net
```
We then have to respond with a message
```
PONG :irc.srcf.net
```
Our code then looks like
```js
// For every line we receive via the socket
if (line.startsWith('PING :')) {
    client.write(`PONG ${line.slice(5)}\r\n`);
}
```
This is all we need for the purpose of having an IRC client that does nothing. If we want to send a message to the channel `#alerts`, we simply send
```js
client.write('PRIVMSG #alerts :the message\r\n');
```

# On JavaScript
As someone who would normally prefer to write Python, I initially tried to
write the script in python. However, I very soon discovered that Python is not
really well-suited for the task. The script has two tasks &mdash; to listen and
respond to `PING` requests from the IRC server, and to listen to messages from
Icinga and Munin. In Python, either of these tasks would be blocking. While
this can be solved (after all, people *do* write IRC bots in python), it is
nowhere as straightforward as it is in JavaScript, which has a native event
loop.

The end result is a short, dependency-free node.js script that, it turns out,
runs on node versions as early as `1.0.0` (when it wasn't even called node).
