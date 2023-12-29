from pathlib import Path
from re import M
import subprocess
from typing import List

MASTER_FILE = "/Users/ellana/notes/download.md"
DOWNLOAD_FOLDER = "/Users/ellana/Downloads/youtube_downloads"

# TODO: parametrize filetype
# TODO: add command line args


def get_links(path: Path) -> List[str]:
    with open(path) as f:
        links = f.readlines()
    links = [link.strip("\n") for link in links]
    return links


def cleanup_link_file(path: Path):
    open(path, "w").close()


def download_links(links: List[str], download_folder: Path):
    download_folder.mkdir(exist_ok=True)
    for link in links:
        subprocess.run(
            [
                "yt-dlp",
                "--extract-audio",
                "--audio-format",
                "mp3",
                "-P",
                download_folder,
                link,
            ]
        )


def upload_to_onedrive(download_folder: Path):
    # TODO: parametrize location on onedrive
    for file in download_folder.iterdir():
        subprocess.run(["onedrive-uploader", "upload", file, "watching"])


def delete_folder(download_folder: Path):
    download_folder.rmdir()


if __name__ == "__main__":
    download_links(get_links(Path(MASTER_FILE)), Path(DOWNLOAD_FOLDER))
    upload_to_onedrive(Path(DOWNLOAD_FOLDER))
