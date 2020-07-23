---
title: "Securing Mattermost via lua-nginx"
date: 2020-07-23T09:38:11+00:00
tags: ['mattermost', 'hacks', 'nginx']
authors: ["Dexter Chua"]
draft: false
---
As announced in the [previous blog post]({{< ref "mattermost.md" >}}), the SRCF
just launched a new mattermost instance. Mattermost runs on an [open-core
model](https://en.wikipedia.org/wiki/Open-core_model), with an open-sourced
free tier and paid "enterprise" feature. Being a student-run society, we went
with the free tier, officially known as "Team Edition". The Team Edition lacks
some access control features that would be useful for us. After numerous failed
attempts to do access control the "right" way, we decided to intercept
Mattermost's API calls at nginx via
[lua-nginx-module](https://github.com/openresty/lua-nginx-module) to run our
own authentication logic before passing them on to Mattermost. At the end, we
get more refined permission controls that we would have had with Enterprise
edition.

<!--more-->
# (Failed) OAuth2 login
Originally, our goal was to restrict access to Cambridge members only. At
first, we tried to let users log in via Raven (or [SRCF
Goose](https://auth.srcf.net), which uses your SRCF credentials). In addition
to restricting access, this avoids the need to keep and remember another
password. This would have used a work-in-progress [OpenID Connect
(OIDC)](https://openid.net/connect/) implementation. However, Mattermost
doesn't support generic OIDC, even in the Enterprise Edition.

As Edwin
[discovered](https://devopstales.github.io/home/mattermost-keycloak-sso/), what
Mattermost *does* support is GitLab authentication, and GitLab has a
sufficiently compliant OIDC implementation. Moreover, since GitLab is often
self-hosted, Mattermost allows us to set custom API endpoints. Thus, we can
simply mock GitLab's API and provide authentication that way.

However, there was one critical issue that made us abandon this approach. The
login button still says "GitLab". We can inject CSS into the web client to
replace the text of the button, but mobile buttons are a lost cause because
mobile Mattermost plugins don't exist yet. We *can* tell users to click the
GitLab button to log in via Raven, but that screams "this is a huge hack"; we
can only do that in blog posts.

# Restricting to custom email domains
Without GitLab authentication, we had to do with email logins. Since we do not
want to run a completely open server, we wanted to limit the email domains to
`@srcf.net` or `@cam.ac.uk`. Mattermost has a configuration option for this.
However, not every member of the university has a `@cam.ac.uk` domain. Some
have department-issued emails instead. Mattermost doesn't natively support
matching `@*.cam.ac.uk`.

Moreover, we envision cases where a Cambridge-based team wants to invite some
non-Cambridge members for discussion, e.g. alumni. It is *extremely* difficult
to allow users with an "invalid" email domain. The domain is checked whenever
one creates and joins a team, in addition to during sign up. The server
command-line management tools do not let us bypass the restriction. The best
solution we found was to

 1. Ask the user to create an account with a dummy `@srcf.net` email
 2. Add them to the teams using the server cli tool. This *must* be done while
    they still have the `@srcf.net` email.
 3. Manually edit the database to replace their email address.
 4. Have them verify the real email.

This requires a lot of manual intervention, and is highly inflexible. The
database schema is also not something that is guaranteed to be stable between
versions, and editing the database directly is always risky.

While we had a working set up to do this, at the end, we decided to go for
something bolder.

# Filtering nginx requests with Lua
We put Mattermost behind an nginx reverse proxy, and all requests pass through
nginx before reaching Mattermost. Since nginx allows custom scripting via
[lua-nginx-module](https://github.com/openresty/lua-nginx-module), we can
intercept the requests to perform custom validation.

On Ubuntu, `lua-nginx-module` can be installed via the `nginx-extras` package.
To make use of this, we add the following line in the nginx config:
```
 server {
     # Usual stuff

     location / {
+        access_by_lua_file /usr/local/share/lua/5.1/mattermost.lua;
         # The rest of the usual stuff
     }
 }
```
This line tells `nginx` to run the file `mattermost.lua` to determine if the
request should be allowed. The rest of the logic is all contained in this Lua
file.

The next step is to figure out how the Mattermost client communicates with the
server. Thankfully, the Mattermost API is [well
documented](https://api.mattermost.com). To create a user, they send a `POST`
request to
`https://mattermost.srcf.net/api/v4/users`. The body of the request is a json
of the form
```json
{
    "email": "...",
    "...": "..."
}
```

A simplified version of `mattermost.lua` that validates the email domain will
have the following contents:
```lua
json = require "json"

-- Define a helper function to check if a string ends with a suffix
local function endswith(s, x)
    return x == "" or string.sub(s, -#x) == x
end

if ngx.var.request_method == "POST" and ngx.var.uri == "/api/v4/users" then
    -- We tell nginx to wait for the entire request body so that we can read it
    -- in the next step.
    ngx.req.read_body()

    local args = json.decode(ngx.req.get_body_data())
    local email = args["email"]

    if not (endswith(email, "@srcf.net") or
            endswith(email, "@cam.ac.uk") or
            endswith(email, ".cam.ac.uk")) then

        -- If so, we send an error response using ngx library functions.
        -- In particular, ngx.say writes to the body.
        ngx.header["Content-type"] = 'application/json'
        ngx.say(json.encode({
            id="api.user.create_user.accepted_domain.app_error",
            message="You must use an @srcf.net or @cam.ac.uk email",
            status_code=400,
        }))

        -- ngx.exit tells to respond with what we have written.
        ngx.exit(400)
    end
    -- If ngx.exit has not been called, the request is passed on to the
    -- original processor, in this case mattermost. We can also do an early
    -- return by with `return`.
end
```
Note that we return the same error as what Mattermost would have replied if
the request were denied by Mattermost. Thus, any client should be able to
handle this gracefully, instead of breaking in mysterious ways.

Moreover, since this denial is done by nginx at this particular endpoint, users
are allowed to change their email after registration. We can also add custom
logic such as allowing any domain when they have an invitation.

# And beyond
This strategy allows for fully customising access control, and opens up a lot
of possibilities. For example, we forbid users from creating open teams (teams
that don't require invitation to join).

We can also filter requests based on who is making it. Lua is able to make
requests to the API endpoint to determine the access level of various users. We
use this to restrict channel creation and modification rights to team
administrators, which is vital for more public teams like the [srcf
team](https://mattermost.srcf.net/srcf).

While this *is* a hack, it relies on the officially documented API. Of course,
it would require updating if there is a new API version, or if there are new
endpoints that do things we want to forbid. Compared to patching the server
directly, this avoids the need to recompile the code and resolve merge
conflicts every new version.

The full glory of the ~~hack~~code is available on
[GitHub](https://github.com/SRCF/downpour-ansible/blob/master/roles/mattermost/files/lua/mattermost.lua).
