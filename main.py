import argparse
from pathlib import Path
import subprocess
from typing import List

MASTER_FILE = "/Users/ellana/notes/download.md"
DOWNLOAD_FOLDER = "/Users/ellana/Downloads/youtube_downloads"

# TODO: parametrize filetype
# TODO: add full pipeline from file checking to download with cleanup (for cron)
# TODO: clean filenames


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


def main(args):
    if args.download_only:
        download_links(get_links(Path(args.input_file)), Path(args.download_folder))
        return
    if args.upload_only:
        upload_to_onedrive(Path(args.download_folder))
        return
    download_links(get_links(Path(args.input_file)), Path(args.download_folder))
    upload_to_onedrive(Path(args.download_folder))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="yt-dlup",
        description="Download videos from youtube and upload them to onedrive",
    )
    parser.add_argument("-f", "--input-file", default=MASTER_FILE)
    parser.add_argument("-o", "--download-folder", default=DOWNLOAD_FOLDER)
    parser.add_argument("-d", "--download-only", action="store_true")
    parser.add_argument("-u", "--upload-only", action="store_true")
    args = parser.parse_args()
    main(args)
