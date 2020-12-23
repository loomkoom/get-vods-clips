# encoding: utf-8
import logging
import subprocess
from pathlib import Path

import requests

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


def parse_tags(line, vods_clips):
    tags = line.split(',')
    for tag in tags:
        tag = tag.strip()
        if tag.startswith("URL"):
            url = (tag.split(" ")[1].strip("][").strip("'"),)
            if vods_clips == "clips":
                file_name = (Path(url[0].split("/")[-1].strip()),)
        if tag.startswith("ID") and vods_clips == "vods":
            broadcast_id = (tag.split(" ")[1],)
        if tag.startswith("DATE"):
            date = (tag.split(" ")[1],)
        if tag.startswith("TIME"):
            offset_time = tag.split(" ").split(":")
            offset_time = (f"{offset_time[0]}h{offset_time[1]}m{offset_time[2]}s",)
        if tag.startswith("LENGTH"):
            length = (tag.split(" ")[1],)
        if tag.startswith("MUTED"):
            muted_url = (tag.split(" ")[1],)
        if tag.startswith("TITLE"):
            title = tag[7:].strip()
            trans = title.maketrans('<>:"\\/|?*', '         ')
            title = (title.translate(trans),)
    if vods_clips == "clips":
        data = (date + file_name + url + length + title + offset_time)
    elif vods_clips == "vods":
        file_name = (Path(f"{date[0]}_{broadcast_id[0]}"),)
        data = (date + file_name + url + length + title + muted_url)
    return data


def get_link_data(data_file, vods_clips):
    path = Path("../output/data")
    data_file = Path.with_suffix(data_file, ".txt")
    with open(path / data_file, "r", encoding = 'utf8') as file:
        url_data = list()
        streams = list(filter((lambda x: any(s in x for s in (".twitch.tv", ".cloudfront.net"))), file.readlines()))
        for stream in streams:
            data = parse_tags(stream, vods_clips)
            url_data.append(data)
    return url_data, vods_clips


def download_file(url, channel_name, file_name, new_name, vods_clips, muted = None):
    file_path = Path("../output/files")
    path = Path.resolve(file_path / channel_name / vods_clips)
    muted_path = Path.resolve(Path.cwd() / file_path / channel_name / "playlists")
    if not Path.is_dir(path):
        Path.mkdir(path, parents = True)

    if Path.is_file(path / file_name) or Path.is_file(path / new_name):
        logger.warning(f"file for {vods_clips[:-1]}: {file_name} already exists\n")
        return
    if vods_clips == "vods":
        if muted == "muted":
            url = f"{muted_path / url}"
        output_file = f"{path / file_name}"
        logger.info(f"Download of {file_name} started\n")
        logger.info(f"Press [+] for more log details, [-] for less log details and [q] to quit\n")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "warning", "-protocol_whitelist", "file,https,http,tls,tcp",
                        "-i", url,
                        "-c", "copy", output_file])
        if Path.is_file(path / file_name):
            logger.info(f"{file_name} Downloaded to {path}\n")
        else:
            logger.warning("there seems to have gone something wrong downloading the file")
            logger.warning("please check if any errors are displayed and verify your input\n")

    elif vods_clips == "clips":
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36', }
        r = requests.get(url, headers = headers, stream = True)
        logger.info(f"Download of {file_name} started")
        with open(path / file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size = 1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        if Path.is_file(path / file_name):
            logger.info(f"{file_name} Downloaded to {path}\n")
        else:
            logger.warning("there seems to have gone something wrong downloading the file")
            logger.warning("please check if any errors are display and verify your input\n")


def get_files(data_file, rename, vods_clips, try_muted = "yes", loglevel = "INFO"):
    loglevels = {"NOTSET": 0, "DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
    loglevel = loglevels[loglevel.upper()]
    logger.setLevel(loglevel)

    data_file = Path(data_file)

    channel_name = data_file.name.split(" ")[0]
    file_names = []
    link_data = get_link_data(data_file, vods_clips)
    vods_clips = link_data[1]
    file_path = Path("../output/files")
    path = file_path / channel_name / vods_clips
    for data in link_data[0]:
        date, file_name, url, length, title, _ = data
        print(vods_clips, try_muted, len(data[5]))
        if vods_clips == "vods" and try_muted == "yes" and len(data[5]) != 1:
            logger.debug("vod has muted parts, using muted version\n")
            url = data[5]

        if vods_clips == "clips":
            offset_time = data[5]
            new_name = Path.with_suffix(Path(f"{date}__{title}__{offset_time}-{length}_{file_name}"), ".mp4")
            file_name = Path.with_suffix(file_name, ".mp4")
            download_file(url, channel_name, file_name, new_name, vods_clips)
        if vods_clips == "vods":
            muted = "muted" if len(data[5]) != 1 else "unmuted"
            new_name = Path.with_suffix(Path(f"{date}_{title}_{length}_{file_name}_{muted}"), ".mp4")
            file_name = Path.with_suffix(file_name, ".mp4")
            download_file(url, channel_name, file_name, new_name, vods_clips, muted)

        if rename == "yes" and Path.is_file(path / file_name) and not Path.is_file(path / new_name):
            Path.rename(path / file_name, path / new_name)
            file_names.append(new_name)
        else:
            file_names.append(file_name)
    return file_names


def main():
    print("\n-downloads all clips or vods from generated file \n"
          "-input [file_name] [vods or clips] for files in /output/data/ \n"
          "-outputs files in: /output/downloads/channel_name/[clips or vods]\n"
          "-option to rename files\n"
          "     (clips from {ID-offset}.mp4 ---> {date}__{title}__{offset_time}-{length}_{ID-offset}.mp4\n"
          "     (vods from {ID}.mp4 ---> {date}_{title}_{length}_{file}_{muted}.mp4\n"
          "-option to download muted versions (use if unmuted version doesn't work)\n\n")
    data_file = input("file name? >> ").strip()
    rename = input("rename files with stream data instead of ID's [yes/no] >> ").strip()
    vods_clips = Path(data_file).name.split(" ")[1]
    if vods_clips == "vods":
        try_muted = input("Download muted version when available [yes/no]? >>").strip()
    else:
        try_muted = "no"
    get_files(data_file, rename, vods_clips, try_muted, loglevel = "DEBUG")


if __name__ == "__main__":
    main()
