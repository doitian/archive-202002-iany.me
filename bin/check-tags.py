#!/usr/bin/env python

import sys
from subprocess import check_output

tags_text = check_output(['rg', '-N', '-I', '--no-heading', '--color', 'never', r'^tags\s*[:=]\s*\[(.*)\]', '-r', '$1,', 'content'], encoding='utf-8')

tags = {}

for line in tags_text.splitlines():
    for tag in line.split(','):
        tag = tag.strip().strip('\'"')
        if tag != '':
            lower_tag = tag.lower()
            if lower_tag in tags and tags[lower_tag] != tag:
                print("Conflict: {}, {}".format(tags[lower_tag], tag))
            else:
                tags[lower_tag] = tag

if len(sys.argv) > 1 and sys.argv[1] == 'print':
    for tag in sorted(tags.values()):
        print(tag)
