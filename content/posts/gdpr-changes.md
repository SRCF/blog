---
title: "SRCF changes due to GDPR"
date: 2018-05-11T23:53:51+00:00
authors: ["Malcolm Scott"]
---
_Note: this post has been migrated from our previous wiki documentation._

On 13th May 2018 the SRCF sysadmins will begin making some system changes to better comply with the upcoming General Data Protection Regulation.

<!--more-->

## Filesystem permissions and layout changes

  * Users’ and societies’ home directories (/home/spqr2, /societies/foosoc) will have any public-access permissions revoked (chmod o-rx); only the owner will be able to read a directory in /home and only society administrators will be able to read a directory in /societies
  * Users and societies will be given an additional public directory, named /public/home/spqr2 or /public/societies/foosoc; anything placed in there will be readable by anybody else unless the permissions are explicitly changed
  * public_html and cgi-bin directories will be moved into /public (with a symbolic link from the old location)
  * Nothing else will be moved into /public since we have no way of knowing what data should be public

(Of course, replace ‘spqr2’ or ‘foosoc’ with your relevant CRSid or society short-names respectively.)

As a result:

  * Scripts in websites which use relative paths to access files outside of public_html will need adjusting
  * Ad-hoc file-sharing arrangements which relied upon files or directories being world-readable may need adjusting, e.g. by moving the relevant directories into /public

Please be prepared to take some action next week to make sure that everything you use the SRCF for still works.
