#!/usr/bin/env python3
"""
Download the latest Juggluco arm64 APK from SourceForge.
"""

import os
import re
import requests
import sys

from bs4 import BeautifulSoup
from pathlib import Path


FILES_URL = "https://sourceforge.net/projects/juggluco/files/"
DIRECT_DOWNLOAD_BASE = "https://master.dl.sourceforge.net/project/juggluco/"
FILENAME_PATTERN = re.compile(r"^Juggluco-[\d.]+-arm64\.apk$")


def get_latest_filename(url: str) -> str:
    """
    Fetch the SourceForge file list page, find the first entry whose title
    matches Juggluco-<version>-arm64.apk, and return the filename.
    """
    print(f"Fetching file list from {url} ...")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", id="files_list")
    if table is None:
        sys.exit("ERROR: Could not find the files_list table on the page.")

    for tr in table.find_all("tr", class_="file"):
        title = (tr.get("title") or "").strip()
        if FILENAME_PATTERN.match(title):
            return title

    sys.exit("ERROR: No file matching 'Juggluco-<version>-arm64.apk' found.")


def download_file(filename: str, dest_dir: str = ".") -> Path:
    """
    Download the file directly from the SourceForge mirror and save it
    to *dest_dir*.  Returns the path of the saved file.
    """
    download_url = f"{DIRECT_DOWNLOAD_BASE}{filename}?viasf=1"
    dest = Path(dest_dir) / filename

    print(f"Downloading {filename} ...")
    print(f"  URL: {download_url}")

    with requests.get(
        download_url, stream=True, timeout=60, allow_redirects=True
    ) as resp:
        resp.raise_for_status()

        total = resp.headers.get("Content-Length")
        total = int(total) if total else None

        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 256):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded * 100 / total
                    print(
                        f"\r  Progress: {downloaded / 1e6:.1f} / "
                        f"{total / 1e6:.1f} MB  ({pct:.1f}%)",
                        end="",
                        flush=True,
                    )
                else:
                    print(
                        f"\r  Downloaded: {downloaded / 1e6:.1f} MB",
                        end="",
                        flush=True,
                    )

    print()
    print(f"Saved to {dest.resolve()}")
    return dest


def main() -> None:
    filename = get_latest_filename(FILES_URL)
    print(f"Found latest arm64 APK: {filename}")
    download_dir = os.path.abspath("downloads")
    os.makedirs(download_dir, exist_ok=True)
    download_file(filename, download_dir)


if __name__ == "__main__":
    main()
