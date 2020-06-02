DEST = /public/societies/srcf-web/public_html/_blog/
DRAFTDEST = /public/societies/srcf-web/public_html/blog_draft/
HUGO_VERSION = 0.71.1

HUGO = ./bin/hugo_$(HUGO_VERSION) --noTimes

production:
	$(HUGO) --destination $(DEST)

post:
	./bin/new_post.py

draft:
	$(HUGO) -b "https://www.srcf.net/blog_draft/" -D --destination $(DRAFTDEST)
	echo "AuthType Ucam-WebAuth\nRequire unix-group executive" > $(DRAFTDEST).htaccess
