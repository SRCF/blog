---
title: "Timeout conferencing goes live!"
date: 2020-06-02T13:06:42+00:00
tags: ['announcement', 'timeout']
authors: ["Matias Silva"]
---

*tl;dr – The SRCF is offering free and simple video conferencing for all members of the university. To get started, visit https://timeout.srcf.net and read our documentation. You can host meetings for as long as you want, when you want and have anyone join all via a convenient link. No annoying downloads needed – it runs in your browser and is very mobile friendly.*

<!--more-->

To all SRCF members,

First, I hope that you are well in these odd and turbulent times. The past few months have been odd for all of us in one way or another. I would like to offer my most sincere and heartfelt thoughts to all those who have been personally affected. While plenty of unfortunate events have occurred, this period has also been one of great innovation within the SRCF as we put our thinking hats on and brace for what may soon be a virtual academic year. 

The SRCF has been thinking about what it can do in addition to our existing services for the University community and our discussions found a lacking platform for secure, reliable and convenient video conferencing. Inspired by my tinkering with BigBlueButton (see wholesome story below), the SRCF has released a video conferencing platform that solves several of these problems, all while being free for all. Sounds great, right? So let’s get started…

You may access the service, which we have named Timeout, at https://timeout.srcf.net and read about what features are available, how to use this, and more at https://docs.srcf.net/#timeout.

We understand by now most will have found a way to cope with the existing tools out there in some way or another, but we nonetheless urge you to give Timeout a try (we’ll give you your money back if you’re dissatisfied)! After all, there was once a time when none of us knew how to use Zoom :). Once you've given us a try, do let us know what you think about it! And lastly, though we have worked hard over the past weeks to build this and it is fully functional, it’s likely that some things need ironing out and so we would appreciate any and all feedback!

Reach out to us at `support@srcf.net` or join us on #timeout [IRC channel](https://webchat.srcf.net/) or our [discord channel](https://discord.com/invite/et353sv) if you want to help out, improve Timeout, or ask us how it works!

## Where it all started

The idea behind Timeout started when I returned to Portugal after the University had entered its red phase and was looking for yet another way to fill up my new "free time". I remembered that I used to do quite a bit of volunteering for CoderDojo LX, one of the thousand worldwide CoderDojos that teach and inspire young kids to get their hands dirty with code and electronics. I hadn't checked up on them since I left for University in October (sadly, I quickly ran out of time for much of what I used to do once I started at Cambridge) and thought it couldn't hurt to email the last contact I had.

A few days later, and I get a disheartening response. It turns out that most leaders had left the project due to other commitments, and my contact was the only one left. He, too, had limited time and so the session count slowly went from one a week to one every month until there were no more sessions for two whole months. He told me about how my email had re-energized him after a few weeks of intense work and a complete shift in lifestyle due to the pandemic. That night, I logged into Slack and we have a conversation that lasted until 3AM, sharing our latest novelties and things we'd been up to. It was an exciting time for me but having lost two months' worth of sessions had me sad and it was time for that to change.

I started to look into ways we could kickstart our sessions but this time online. What are the best tools out there? How would they join? Are there any security concerns (remember, working with children is *difficult*)? How could they ask for help? At that point, there were quite a lot of unknowns and few solutions. We started to try out all sorts of things: Google Classroom, Jitsi, WebEx, YouTube livestreaming and the list goes on...None of them were great and we were scratching our heads until I remembered that I could, if I asked nicely, perhaps ask some folks back at this thing called the SRCF that I'm junior treasurer of about hosting my own BigBlueButton instance. I didn't quite know what it was but I *did* know that it had all the features I wanted and seemed very robust. I didn't know what I needed to do or how to even do it but I remotely knew that I needed something called a *server* and that the SRCF had something to do with servers. After some talking, a kind stranger at the SRCF gifted me with a virtual machine to play with and I got started with playing around. 

It worked! I didn't know what most of what I did meant (thanks <3 BBB documentation) or what it did - but I did know I had a working platform and that I had MADE SOMETHING!!! I quickly shared this with my contact and we were both grinning at the thought of online CoderDojo LX sessions becoming a reality. Looking back at my Linux skills then, I chuckle, knowing very well that even what I know now is still just the tip of the iceberg. A few days of intense testing went by and we were satisfied. Time for CoderDojo LX #243. 

Our first session was a resounding success. The kids loved it, we had incredibly positive feedback and our hard work had paid off. Excellent! Some of our old mentors and leaders who saw the success we'd had, started to join our sessions and follow our Slack channel more closely now. I gradually started to make some more changes to our installation and tinkered about to learn how things worked.

Fast forward to a few weeks of very successful sessions (we now offered 3 sessions per week, as opposed to our measely once a month) and I get a message in Discord (I had no idea how to use IRC at the time) from a "malc" saying that "the provision of a VM on short notice for Matias had been a success story for the SRCF". And thus began what would turn into many nights, most of them ending past 1 AM, of SRCF history, fun conversations between friends, and me getting lost in technical jargon. The idea of the SRCF hosting video conferencing came up, as a joke initially (I believe) but we then began to actually think about turning this joke into a *what if*...and thus Timeout was born. I teamed up with a team of experienced sysadmins to make Timeout happen. While I myself am a beginner to many of these things, those who have guided me are most definitely not.

I'll leave the troubleshooting, the difficulties we ran into and why Timeout has been built the way it has for another blog post but for now I hope you enjoy using Timeout and appreciate its wholesome beginning. 
