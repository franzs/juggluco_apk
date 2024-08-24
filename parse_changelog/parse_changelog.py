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
        ul = p.find_next_sibling('ul')
        if ul:
            version_number = p.get_text().strip()
            version_number = re.sub(r'[:\.]$', '', version_number)
            changes_html = str(ul)  # Convert the BeautifulSoup object to a string
            changes_markdown = h.handle(changes_html)
            changes_markdown = re.sub(r'^ *', '', changes_markdown, flags=re.MULTILINE)

            if re.match(r'\d+\.\d+(\.\d+)?', version_number):
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
        print(changelog[args.version])
    except KeyError:
        print(f"No changes for version {args.version} found.")
        sys.exit(1)
