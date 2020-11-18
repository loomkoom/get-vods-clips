import os
import subprocess

import requests


def download_file(url, channel_name, file_name, new_name, vods_clips):
    path = f"../output/files/{channel_name}/{vods_clips}"
    if not os.path.isdir(path):
        os.mkdir(f"../output/files/{channel_name}")
        os.mkdir(path)
    if os.path.isfile(f"{path}/{file_name}.mp4") or os.path.isfile(f"{path}/{new_name}.mp4"):
        print(f"file for {vods_clips[:-1]}: {file_name} already exists\n")
        return
    if vods_clips == "vods":
        print(f"Download of {file_name}.mp4 started")
        subprocess.run(["ffmpeg", "-hide_banner", "-v", "24", "-i", url, "-c", "copy", f"{path}/{file_name}.mp4"])
        if os.path.isfile(f"{path}/{file_name}.mp4"):
            print(f"{file_name}.mp4 Downloaded to {path[2:]}\n")
        else:
            print("there seems to have gone something wrong downloading the file")
            print("please check if any errors are display and verify your input")

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
            print("please check if any errors are display and verify your input")


def get_link_data(data_file):
    path = "../output/data"
    data_file = data_file[:-4] if data_file.endswith(".txt") else data_file
    with open(f"{path}/{data_file}.txt", "r", encoding = 'utf8') as file:
        url_data = list()
        if file.readline().find("MUTED:") != -1:
            vods_clips = "vods"

        elif file.readline().find("TIME:") != -1:
            vods_clips = "clips"
        file.seek(0)
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
                    file_name = (tag[3:].strip(),)
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
                data = (date + file_name + url + length + title + muted_url)
            url_data.append(data)
    return url_data, vods_clips


def get_files(channel_name, data_file, rename, muted = "unmuted"):
    link_data = get_link_data(data_file)
    vods_clips = link_data[1]
    path = f"../output/files/{channel_name}/{vods_clips}"
    for data in link_data[0]:
        date, file_name, url, length, title = data[0], data[1], data[2], data[3], data[4]
        if vods_clips == "vods" and muted == "muted" and int(data[5]) != 0:
            print("vod has muted parts, using muted version")
            url = data[5]

        if vods_clips == "clips":
            offset_time = data[5]
            new_name = f"{date}__{title}__{offset_time}-{length}_{file_name}"
        if vods_clips == "vods":
            muted = "muted" if int(data[5]) != 0 else "muted"
            new_name = f"{date}_{title}_{length}_{file_name}_{muted}"
        download_file(url, channel_name, file_name, new_name, vods_clips)
        if rename == "yes" and os.path.exists(f"{path}/{file_name}.mp4") and not os.path.exists(f"{path}/{new_name}.mp4"):
            os.rename(f"{path}/{file_name}.mp4", f"{path}/{new_name}.mp4")


def main():
    print("\n-files all clips or vods from generated file \n"
          "-input [channel name] [file_name] [vods or clips] for files in /output/data/ \n"
          "-outputs files in: /output/downloads/channel_name/[clips or vods]\n"
          "-option to download muted versions (use if unmuted version doesn't work)\n"
          "-option to rename files\n"
          "     (clips from {ID-offset}.mp4 ---> {date}__{title}__{offset_time}-{length}_{ID-offset}.mp4\n"
          "     (vods from {ID}.mp4 ---> {date}_{title}_{length}_{file}_{muted}.mp4\n")
    channel_name = input("streamer name? >>").strip()
    data_file = input("file name? >>").strip()
    vods_clips = input("vods or clips? >>").strip()
    rename = input("rename files with stream data instead of ID's [yes/no] >>").strip()
    if vods_clips == "vods":
        muted = input("Download muted version when available [yes/no]? >>")
        muted = "muted" if muted == "yes" else "unmuted"
        get_files(channel_name, data_file, rename, muted)
    else:
        get_files(channel_name, data_file, rename)


if __name__ == "__main__":
    main()
