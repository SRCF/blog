#!/usr/bin/env python3

from srcf.database.queries import get_member
from datetime import datetime, timezone
from pathlib import Path
import string
import os
import sys
import subprocess

BASE_DIR = (Path(__file__).absolute().parent / "..").resolve()
ALLOWED_PATH_CHARS = set(string.ascii_lowercase + string.digits + "-")

postpath = input("Post path: ")
if any(x not in ALLOWED_PATH_CHARS for x in postpath):
    print("Invalid character in post path. Must be alphanumeric or '-'.")
    sys.exit(1)

dest = BASE_DIR / "content" / "posts" / (postpath + ".md")

if dest.exists():
    print("content/posts/%s already present. Aborting." % postpath)
    sys.exit(1)

data = {
    "author": get_member(os.getlogin()).name,
    "date": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "title": input("Post title: "),
    "tags": [x.strip() for x in input("Tags: ").split(",")]
}

TEMPLATE = r'''---
title: "{title}"
date: {date}
tags: {tags}
authors: ["{author}"]
draft: true
---
'''

dest.write_text(TEMPLATE.format(**data))

editor = os.environ.get("EDITOR", "nano")
if input("Open in {} [y/n]: ".format(editor)) == 'y':
    subprocess.call([editor, str(dest)])
