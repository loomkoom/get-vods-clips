import os
import subprocess
import requests


def download_file(url, channel_name, file_name,vod_clips):
    if vod_clips == "vods":
        subprocess.run(["ffmpeg", "-i", url, "-c", "copy", f"{file_name[:-3]}.mp4"])
    else:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36', }
        r = requests.get(url, headers = headers, stream = True)
        if not os.path.isdir(f"../output/files/{channel_name}"):
            os.mkdir(f"../output/files/{channel_name}")

            with open(f"../output/files/{channel_name}/{file_name}.mp4", 'wb') as f:
                for chunk in r.iter_content(chunk_size = 1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)

    return file_name


def get_clips(channel_name, file_location, vod_clips):
    with open(file_location, "r", encoding = 'utf8') as file:
        urls = list()
        streams = list(filter((lambda x: ".twitch.tv" in x), file.readlines()))
        for stream in streams:
            data = stream.split(',')
            for tag in data:
                tag = tag.strip()
                if tag.startswith("URL"):
                    url = (tag[4:].strip(),)
                    if vod_clips == "clips":
                        file_name = (tag[43:].strip(),)
                if tag.startswith("ID"):
                    file_name = (tag[3:].strip(),)
                if tag.startswith("DATE"):
                    date = (tag[6:-9].strip(),)
                if tag.startswith("TIME"):
                    offset_time = tag[6:].strip().split(":")
                    offset_time = (f"{offset_time[0]}h{offset_time[1]}m{offset_time[2]}s",)
                if tag.startswith("LENGTH"):
                    length = (tag[8:].strip(),)
                if tag.startswith("TITLE"):
                    title = tag[7:].strip()
                    trans = title.maketrans('<>:"//|?*', '         ')
                    title = (title.translate(trans),)
            if vod_clips == "clips":
                data = (date + file_name + url + length + title + offset_time)
            elif vod_clips == "vods":
                data = (date + file_name + url + length + title)
            urls.append(data)

    for data in urls:
        date, file_name, url, length, title = data[0], data[1], data[2], data[3], data[4]
        if vod_clips == "clips":
            offset_time = data[5]

        if (not os.path.exists(f"../output/files/{channel_name}/{file_name}")) and (
                not os.path.exists(f"../output/files/{channel_name}/{date}_{title}_{length}_{file_name}")):
            file = download_file(url, channel_name, file_name,vod_clips)
            print(file)
        if vod_clips == "clips":
            if not os.path.exists(f"../output/files/{channel_name}/{date}__{title}__{offset_time}-{length}_{file_name}"):
                file = download_file(url, channel_name, file_name,vod_clips)
            if os.path.isfile(f"../output/files/{channel_name}/{file}"):
                os.rename(f"../output/files/{channel_name}/{file_name}",
                          f"../output/files/{channel_name}/{date}__{title}__{offset_time}-{length}_{file_name}")
        elif vod_clips == "vods":
            print(file, url)
            if os.path.isfile(f"../output/files/{channel_name}/{file}"):
                os.rename(f"../output/files/{channel_name}/{file_name}",
                          f"../output/files/{channel_name}/{date}_{title}_{length}_{file_name}")


def main():
    print("files all clips or vods from generated file \n"
          "input [channel name] [file_location] [vods or clips] \n"
          "outputs files in:\output\downloads\channelname\[clips or vods]\n")
    channel_name = input("streamer name? >>").strip()
    file_location = input("file location? >>")
    vods_clips = input("vods or clips? >>").strip()
    get_clips(channel_name, file_location, vods_clips)


if __name__ == "__main__":
    main()
