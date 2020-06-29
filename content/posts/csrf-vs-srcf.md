---
title: "Cross-Site Request Forgery"
date: 2020-06-29T01:27:49+00:00
tags: ['security', 'control-panel']
authors: ["Dexter Chua"]
---
In this blog post, I will discuss how the SRCF recently hardened the control
panel against [cross-site request forgery
(CSRF)](https://en.wikipedia.org/wiki/Cross-site_request_forgery) attacks.
These attacks allow malicious sites to perform actions in the control panel on
your behalf.

<!--more-->

# The setup

To understand the attack, let us first consider how authentication works with
the control panel (and most websites out there). After the control panel is
convinced that you are who you are, it sets a cookie in the browser.
Afterwards, whenever you visit any page on `control.srcf.net`, the browser
sends the cookie back to the web server alongside with the request. The web
server then compares the cookie with what it has in its records to know who you
authenticated as. If the cookie is invalid or not present, it sends you back to
the authentication page.

Crucially, this communication is only between the browser and the webserver.
The browser will send the cookies only to `control.srcf.net` and no one else.
A webpage can read cookies on its own domain via JavaScript, but this is
usually prohibited by setting the `HttpOnly` attribute (this prevents
[cross-site scripting](https://en.wikipedia.org/wiki/Cross-site_scripting)
attacks). A webpage can never read cookies on a different domain.

*Note: A user is able to read their own cookies and send requests with arbitrary
cookies. Cookies are usually cryptographically signed by the webserver to
ensure they were indeed set by the webserver. We are not protecting against the
user here. After all, the user already has the authority to make changes on the
control panel. We are preventing malicious sites from making requests on the
user's behalf.*

A user wants to reset their MySQL password. In the control panel, they would
encounter a form that looks like
```html
<form action="/member/mysql/password" method="post">
    <input type="submit" value="Confirm">
</form>
```
Once they press the "Confirm" button, the browser submits the form by sending a
`POST` request to `https://control.srcf.net/member/mysql/password`. The request
will contain the authentication cookies previously set, which is used to verify
identity.

# How to perform the attack
Suppose our user has previously logged into the control panel to do some
work, and later visits a malicious site. The site wants to reset the user's
MySQL password. What the attacker can do is to make an identical form on
*their* website:
```html
<form action="https://control.srcf.net/member/mysql/password" method="post">
    <input type="submit" value="Confirm">
</form>
```
If they somehow trick the user into clicking the "Confirm" button, then this
submits a request to the control panel as if the user submitted it from the
control panel. Since we are accessing `https://control.srcf.net/` directly via
the browser, the browser sends the authentication cookies with the request.
This does not require the attacker to learn the contents of the cookie &mdash;
they instead trick the browser into sending it for them.

We can avoid the need to trick the user by making JavaScript send the form for
us. The full exploit page then looks like
```html
<!-- exploit.html -->
<!DOCTYPE HTML>
<html>
  <body>
    <form action="https://control.srcf.net/member/mysql/password" method="post">
      <input type="submit" value="Confirm">
    </form>
    <script>
      document.forms[0].submit()
    </script>
  </body>
</html>
```
This will successfully trick the browser into resetting the MySQL password, but
the user will know it after the fact, since they get redirected to the control
panel. To hide this from the user, we can put this in an iframe:
```html
<!-- better_exploit.html -->
<!DOCTYPE HTML>
<html>
  <body>
    <iframe style="display: none" src="exploit.html"></iframe>
  </body>
</html>
```
By directing users to `better_exploit.html`, the exploit in `exploit.html` runs
in the iframe which is hidden from the user, and the user would not notice anything.

## Attacks that don't work
Before we discuss mitigations to this attack, we first look at some versions of
the attack that *don't* work. This is pretty important &mdash; if these worked,
the attacker can combine these with the previous attack to bypass our CSRF
protections.

* Instead of the redirect, one might try to simply fetch the page with
  JavaScript, which is even more invisible to the user. However, this is
  blocked by [CORS
  policies](https://en.wikipedia.org/wiki/Cross-origin_resource_sharing) by
  default. Since the attacker must redirect the user to the target page
  directly, they cannot use CSRF attacks to retrieve password-protected
  information from the control panel; they can only submit requests.

* If an attacker wants to retrieve password-protected information, they can try
  to embed the control panel into their webpage via an iframe. However,
  browsers do not allow sites to access contents of an iframe if it comes from
  a separate domain. We can also set headers to tell the browser to not allow
  embedding `control.srcf.net` into anyone's iframe, which prevents this
  problem for good.

# CSRF Protection
To protect users against CSRF attacks, we use a strategy called "double-submit
cookie pattern".

When the user logs into the control panel, we place a random string in the
cookie, which we call the `csrf_token`. In every form the user accesses, we
include the `csrf_token` as a hidden field:
```html
<form action="/member/mysql/password" method="post">
  <input type="hidden" name="csrf_token" value="totally-a-secret">
  <input type="submit" value="Confirm">
</form>
```
When the user submits a request, we obtain the `csrf_token` from two sources
&mdash; one in the `Cookie` header and one in the form data. We then check that
they agree.

If a malicious party attempts to carry out a CSRF attack, they can trick the
browser into sending the `csrf_token` in the `Cookie` header. However, they
never get to learn the value of the `csrf_token`, so they cannot include the
token in their form data when they submit on the user's behalf.

Naively, the attacker might try to steal the token by accessing the form itself
on `control.srcf.net`, which contains the `csrf_token`. However, as mentioned,
the attacker cannot read the contents of pages on `control.srcf.net`, only
redirect people to it, so this also doesn't work.

Fortunately for us, there are already libraries that handle all this for us.
We use [`flask-seasurf`](https://flask-seasurf.readthedocs.io/en/latest/),
which makes CSRF protection a one-liner (after adding the hidden fields to all
of our forms, which is a simple `sed` invocation).

# Remarks
 * We use resetting of MySQL passwords as an example, because it is a
   relatively non-disruptive thing to test on. The attack works for any action;
   for more complex requests, we need a pre-filled form instead of one with
   just a submit button.
 * Our mitigations assume that browsers are reasonably compliant and secure.
   This is a necessary assumption. After all, a broken browser might allow
   malicious sites to access and modify all your cookies on all sites, or even
   delete all files on your filesystem.
 * A reader was concerned about our use of `sed`; it might miss something.
   However, this is not a *security* concern. If we forget to add the
   `csrf_token` somewhere, the request will just be always rejected for not
   having a matching token in the form data. Not the best for someone who
   actually wants to carry out the action, but we will most likely notice this
   immediately and deploy a fix.
