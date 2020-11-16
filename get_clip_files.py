import os
import time

import requests


def download_file(url, channel_name):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36', }
    local_filename = url.split('/')[-1]
    r = requests.get(url, headers = headers, stream = True)

    if not os.path.isdir(f".\\output\\downloads\\{channel_name}"):
        os.mkdir(f".\\output\\downloads\\{channel_name}")

    with open(f".\\output\\downloads\\{channel_name}\\{local_filename}", 'wb') as f:
        for chunk in r.iter_content(chunk_size = 1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return local_filename


def get_clips(channel_name, file_location):
    with open(file_location, "r", encoding = 'utf8') as file:
        urls = list()
        streams = list(filter((lambda x: "clips-media-assets2.twitch.tv" in x), file.readlines()))
        start = time.time()
        for stream in streams:
            data = stream.split(',')
            for tag in data:
                tag = tag.strip()
                if tag.startswith("URL"):
                    url = (tag[4:].strip(),)
                    file_name = (tag[43:].strip(),)
                if tag.startswith("DATE"):
                    date = (tag[6:-9].strip(),)
                if tag.startswith("TIME"):
                    offset_time = tag[6:].strip().split(":")
                    offset_time = (f"{offset_time[0]}h{offset_time[1]}m{offset_time[2]}s",)
                if tag.startswith("LENGTH"):
                    length = (tag[8:].strip(),)
                if tag.startswith("TITLE"):
                    title = tag[7:].strip()
                    trans = title.maketrans('<>:"/\\|?*', '         ')
                    title = (title.translate(trans),)
            urls.append((date + file_name + url + offset_time + length + title))
        runtime = time.time() - start
        print(runtime)

    for link in urls:
        date, filename, url, offset_time, length, title = link[0], link[1], link[2], link[3], link[4], link[5]

        if (not os.path.exists(f".\\output\\downloads\\{channel_name}\\{filename}")) and (
                not os.path.exists(f".\\output\\downloads\\{channel_name}\\{date}__{link[5]}__{offset_time}-{length}_{filename}")):
            file = download_file(url, channel_name)

        if os.path.isfile(f".\\output\\downloads\\{channel_name}\\{file}"):
            os.rename(f".\\output\\downloads\\{channel_name}\\{filename}",
                      f".\\output\\downloads\\{channel_name}\\{date}__{link[5]}__{offset_time}-{length}_{filename}")


def main():
    channel_name = input("streamer name? >>")
    file_location = input("file location? >>")
    get_clips(channel_name, file_location)


if __name__ == "__main__":
    main()
