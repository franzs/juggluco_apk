#!/usr/bin/env python

import argparse
import html2text
import os
import re

import sys

from bs4 import BeautifulSoup


def parse_changelog(html_content):
    changelog_dict = {}

    soup = BeautifulSoup(html_content, 'html.parser')
    h = html2text.HTML2Text()

    body = soup.body
    for p in body.findChildren('p'):
        stripped_p_text = p.text.strip()
        if re.match(r'\d+\.\d+(\.\d+)?', stripped_p_text):
            version_number = stripped_p_text

            if version_number == '9.0.15':
                version_number = '9.0.16'

            changes = []

            for sibling in p.next_siblings:
                stripped_sibling_text = sibling.text.strip()
                if sibling.name == 'p' and (re.match(r'\d+\.\d+(\.\d+)?', stripped_sibling_text) or stripped_sibling_text == 'Goto Start'):
                    break

                changes.append(str(sibling))

            changes_markdown = h.handle('\n'.join(changes))
            changes_markdown = re.sub(r'^ *', '', changes_markdown, flags=re.MULTILINE)

            changelog_dict[version_number] = changes_markdown

    return changelog_dict


parser = argparse.ArgumentParser(prog=os.path.basename(__file__), description="Parses Juggluco's changelog")
parser.add_argument('filename')
parser.add_argument('version')

args = parser.parse_args()

with open(args.filename, 'r', encoding='utf-8') as file:
    html_content = file.read()
    changelog = parse_changelog(html_content)

    try:
        print(changelog[args.version].strip())
    except KeyError:
        print(f"No changes for version {args.version} found.", file=sys.stderr)
        sys.exit(1)
