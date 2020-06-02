---
title: "Hello World!"
date: 2020-05-30T09:44:20+00:00
tags: ['meta']
authors: ["Dexter Chua"]
draft: false
---
There have been many exciting SRCF projects recently, the most prominent of
which is [Timeout](https://timeout.srcf.net), a video conferencing platform
that Matias will tell you all about [later]({{< ref "timeout.md" >}}). In the
meantime, we decided to start a blog to share our sysadmin experiences.

The goal is to give our users some insight into what we do, and hopefully
attract some of them to join us in the future. Moreover, we hope that
documenting our experiences can be helpful for other people intending to deploy
similar systems.

<!--more-->

# Choosing the stack
We have always been a fan of static sites. For most of our users, our primary
role is to host websites for societies and the users themselves. Since our
inception, we've had lots and lots of Wordpress and Drupal sites compromised
due to outdated plugins, or outright outdated installations (just to be clear,
the fact that these two CMS are singled out is not a comment on their software
quality, but their popularity). While it is possible to maintain secure sites
using Wordpress or Drupal, doing so requires constant maintenance and
attention. On the other hand, static sites just *are* secure. Any compromises
are necessarily due to the web server itself, which would affect any site
whatsoever.

Of course, there is also the simplicity aspect &mdash; deployment is nothing
but a `cp`. If anything goes wrong, we can directly inspect the HTML files
produced on the server.

At the time of writing, the two main competitors for static blog generators
are [Hugo](https://gohugo.io) and [Jekyll](https://jekyllrb.com). We ended up
with Hugo, for no good reason other than the fact that many of our sysadmins
have used Hugo in the past and have had good experiences.

# Setting up
Unfortunately, many of our servers still run on Ubuntu 16.04 (work in progress,
I promise), which comes with a rather outdated version of Hugo. Since Hugo is
built with Go and is distributed as a single binary, we decided to download the
binary from GitHub and vendor it.

To streamline the build process, we wrote a simple Makefile to automate
the invocation of `hugo` with the right arguments. We decided make Hugo
directly write the files into the relevant `public_html/` directory, so we
spared even the `cp`!

# Theming
Theming Hugo turned out to be much simpler than I expected. The minimum amount
of theming (which was sufficient for us) requires templates for two different
views. The first is the single page view, which you are looking at right now.
It displays a single blog post. The other is a list view, which presents a list
of posts. This is what you see in the homepage or when you click on tags. It
was easy to adapt the css used for the [main srcf
webpage](https://www.srcf.net) for the blog, which took less than an hour or
so.

# Epilogue
Turns out that's all there is to setting up a blog using Hugo! Hope you enjoy
our blog.
