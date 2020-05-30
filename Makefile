DEST = /public/societies/srcf-web/public_html/_blog/
HUGO_VERSION = 0.71.1

build:
	./bin/hugo_$(HUGO_VERSION) --destination $(DEST)

post:
	./bin/new_post.py
