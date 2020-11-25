import os
import subprocess

import requests


def download_file(url, channel_name, file_name, new_name, vods_clips, filepath = "../output/files", muted = None):
    path = f"{filepath}/{channel_name}/{vods_clips}"
    muted_path = os.path.abspath(f"{filepath}/{channel_name}/playlists").replace("\\", "/")
    if not os.path.isdir(f"{filepath}/{channel_name}"):
        os.mkdir(f"{filepath}/{channel_name}")
    if not os.path.isdir(path):
        os.mkdir(path)

    if os.path.isfile(f"{path}/{file_name}.mp4") or os.path.isfile(f"{path}/{new_name}.mp4"):
        print(f"file for {vods_clips[:-1]}: {file_name} already exists\n")
        return
    if vods_clips == "vods":
        if muted == "muted":
            url = f"{muted_path}/{url}"
            print(url)
        print(f"Download of {file_name}.mp4 started")
        subprocess.run(["ffmpeg", "-hide_banner", "-v", "24", "-i", url, "-c", "copy", f"{path}/{file_name}.mp4"])
        if os.path.isfile(f"{path}/{file_name}.mp4"):
            print(f"{file_name}.mp4 Downloaded to {path[2:]}\n")
        else:
            print("there seems to have gone something wrong downloading the file")
            print("please check if any errors are display and verify your input\n")

    elif vods_clips == "clips":
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36', }
        r = requests.get(url, headers = headers, stream = True)
        print(f"Download of {file_name}.mp4 started")
        with open(f"{path}/{file_name}.mp4", 'wb') as f:
            for chunk in r.iter_content(chunk_size = 1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        if os.path.isfile(f"{path}/{file_name}.mp4"):
            print(f"{file_name}.mp4 Downloaded to {path[2:]}\n")
        else:
            print("there seems to have gone something wrong downloading the file")
            print("please check if any errors are display and verify your input\n")


def get_link_data(data_file, vods_clips, datapath):
    path = datapath
    data_file = data_file[:-4] if data_file.endswith(".txt") else data_file
    with open(f"{path}/{data_file}.txt", "r", encoding = 'utf8') as file:
        url_data = list()
        streams = list(filter((lambda x: ".twitch.tv" in x), file.readlines()))
        for stream in streams:
            data = stream.split(',')
            for tag in data:
                tag = tag.strip()
                if tag.startswith("URL"):
                    url = (tag[4:].strip(),)
                    if vods_clips == "clips":
                        file_name = (tag[43:-4].strip(),)
                if tag.startswith("ID") and vods_clips == "vods":
                    broadcast_id = (tag[3:].strip(),)
                if tag.startswith("DATE"):
                    date = (tag[6:-9].strip(),)
                if tag.startswith("TIME"):
                    offset_time = tag[6:].strip().split(":")
                    offset_time = (f"{offset_time[0]}h{offset_time[1]}m{offset_time[2]}s",)
                if tag.startswith("LENGTH"):
                    length = (tag[8:].strip(),)
                if tag.startswith("MUTED"):
                    muted_url = (tag[7:].strip(),)
                if tag.startswith("TITLE"):
                    title = tag[7:].strip()
                    trans = title.maketrans('<>:"//|?*', '         ')
                    title = (title.translate(trans),)
            if vods_clips == "clips":
                data = (date + file_name + url + length + title + offset_time)
            elif vods_clips == "vods":
                file_name = (f"{date[0]}_{broadcast_id[0]}",)
                data = (date + file_name + url + length + title + muted_url)
            url_data.append(data)
    return url_data, vods_clips


def get_files(data_file, rename, datapath = "../output/data", filepath = "../output/files"):
    channel_name = data_file.split(" ")[0]
    vods_clips = data_file.split(" ")[1]
    file_names = []
    if vods_clips == "vods":
        try_muted = input("Download muted version when available [yes/no]? >>").strip()
    link_data = get_link_data(data_file, vods_clips, datapath)
    vods_clips = link_data[1]
    path = f"{filepath}/{channel_name}/{vods_clips}"
    for data in link_data[0]:
        date, file_name, url, length, title = data[0], data[1], data[2], data[3], data[4]
        if vods_clips == "vods" and try_muted == "yes" and len(data[5]) != 1:
            print("vod has muted parts, using muted version\n")
            url = data[5]

        if vods_clips == "clips":
            offset_time = data[5]
            new_name = f"{date}__{title}__{offset_time}-{length}_{file_name}"
            download_file(url, channel_name, file_name, new_name, vods_clips, filepath)
        if vods_clips == "vods":
            muted = "muted" if len(data[5]) != 1 else "unmuted"
            new_name = f"{date}_{title}_{length}_{file_name}_{muted}"
            download_file(url, channel_name, file_name, new_name, vods_clips, filepath, muted)

        if rename == "yes" and os.path.exists(f"{path}/{file_name}.mp4") and not os.path.exists(f"{path}/{new_name}.mp4"):
            os.rename(f"{path}/{file_name}.mp4", f"{path}/{new_name}.mp4")
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
    data_file = input("file name? >>").strip()
    rename = input("rename files with stream data instead of ID's [yes/no] >>").strip()
    get_files(data_file, rename)


if __name__ == "__main__":
    main()
