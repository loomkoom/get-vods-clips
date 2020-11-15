import os
import requests


def download_file(url, streamername):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36', }
    local_filename = url.split('/')[-1]
    r = requests.get(url, headers = headers, stream = True)
    if not os.path.isdir(f".\output\downloads\{streamername}"):
        os.mkdir(f".\output\downloads\{streamername}")
    with open(f".\output\downloads\{streamername}\{local_filename}", 'wb') as f:
        for chunk in r.iter_content(chunk_size = 1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                # f.flush() commented by recommendation from J.F.Sebastian
    return local_filename


def get_clips(streamername,filelocation):
    with open(filelocation, "r", encoding = 'utf8') as file:
        urls = list()
        streams = list(filter((lambda x: "clips-media-assets2.twitch.tv" in x), file.readlines()))
        for stream in streams:
            data = stream.split(',')
            for tag in data:
                tag = tag.strip()
                if tag[:3] == "URL":
                    url = (tag[4:].strip(),)
                    file_name = (tag[43:].strip(),)
                if tag[:4] == "DATE":
                    date = (tag[6:-9].strip(),)
                if tag[:4] == "TIME":
                    time = tag[6:].strip().split(":")
                    time = (f"{time[0]}h{time[1]}m{time[2]}s",)
                if tag[:6] == "LENGTH":
                    length = (tag[8:].strip(),)
                if tag[:5] == "TITLE":
                    title = tag[7:].strip()
                    trans = title.maketrans('<>:"/\\|?*', '         ')
                    title = (title.translate(trans),)
                print(tag)
            urls.append((date + file_name + url + time + length + title))

    for link in urls:
        date, filename, url, time, length, title = link[0], link[1], link[2], link[3], link[4], link[5]
        if (not os.path.exists(f".\output\downloads\{streamername}\{filename}")) and (
                not os.path.exists(f".\output\downloads\{streamername}\{date}__{link[5]}__{time}-{length}_{filename}")):
            file = download_file(url, streamername)

        if os.path.isfile(f".\output\downloads\{streamername}\{file}"):
            os.rename(f".\output\downloads\{streamername}\{filename}",
                      f".\output\downloads\{streamername}\{date}__{link[5]}__{time}-{length}_{filename}")
        print(link)


def main():
    streamername = input("streamer name? >>")
    get_clips(streamername)


if __name__ == "__main__":
    main()
