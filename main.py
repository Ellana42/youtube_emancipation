import argparse
import json
import logging
from pathlib import Path
import re
import shutil
import subprocess
from typing import List

MASTER_FILE = "/Users/ellana/notes/download.md"
DOWNLOAD_FOLDER = "/Users/ellana/Downloads/youtube_downloads"
ONEDRIVE_ROOT = "watching"


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
                "--write-info-json",
                "-P",
                download_folder,
                link,
            ]
        )


def cleanup_name(download_name: str):
    download_name = download_name.strip(".info")
    elements = re.search(r"^(.*)\[\w*\]$", download_name)
    if elements:
        return elements.group(1)
    return download_name.split(".")[0]


def cleanup_download_names(download_folder: Path):
    for file in download_folder.iterdir():
        path = file.parent
        new_name = cleanup_name(file.stem)
        logging.debug(f"Renaming {file.stem} to {new_name}")
        new_path = (path / new_name).with_suffix(file.suffix)
        file.rename(new_path)


def get_channel_name(info_file: Path):
    with open(info_file) as f:
        infos = json.loads(f.read())
    return infos["channel"]


def upload_to_onedrive(
    download_folder: Path,
    organise_in_subfolders: bool = False,
    root_folder: str = ONEDRIVE_ROOT,
):
    for file in download_folder.iterdir():
        if file.suffix != ".json":
            folder = root_folder
            info_file = file.with_suffix(".json")
            if organise_in_subfolders:
                channel_name = get_channel_name(info_file)
                add_onedrive_folder(channel_name, root_folder)
                folder = root_folder + "/" + channel_name
            subprocess.run(["onedrive-uploader", "upload", file, folder])


def add_onedrive_folder(foldername: str, root_folder: str = ONEDRIVE_ROOT):
    subprocess.run(["onedrive-uploader", "mkdir", f"{ root_folder}/{foldername}"])


def delete_folder(download_folder: Path):
    shutil.rmtree(download_folder)


def main(args):
    input_file = Path(args.input_file)
    download_folder = Path(args.download_folder)
    if args.download_only:
        download_links(get_links(input_file), download_folder)
        cleanup_download_names(download_folder)
        if not args.no_cleanup:
            cleanup_link_file(input_file)
            delete_folder(download_folder)
        return
    if args.upload_only:
        upload_to_onedrive(download_folder, args.channel_subfolder)
        if not args.no_cleanup:
            cleanup_link_file(input_file)
            delete_folder(download_folder)
        return
    download_links(get_links(input_file), download_folder)
    cleanup_download_names(download_folder)
    upload_to_onedrive(download_folder, args.channel_subfolder)
    if not args.no_cleanup:
        cleanup_link_file(input_file)
        delete_folder(download_folder)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        prog="yt-dlup",
        description="Download videos from youtube and upload them to onedrive",
    )
    parser.add_argument("-i", "--input-file", default=MASTER_FILE)
    parser.add_argument("-o", "--download-folder", default=DOWNLOAD_FOLDER)
    parser.add_argument("-d", "--download-only", action="store_true")
    parser.add_argument("-u", "--upload-only", action="store_true")
    parser.add_argument("--no-cleanup", action="store_true")
    parser.add_argument("-f", "--format", default="audio", choices=["audio", "video"])
    parser.add_argument("--channel-subfolder", action="store_true")
    args = parser.parse_args()
    main(args)
