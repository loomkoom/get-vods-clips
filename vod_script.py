import datetime
import hashlib

import requests


def totimestamp(dt, epoch = datetime.datetime(1970, 1, 1)):
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 86400) * 10 ** 6) / 10 ** 6


def get_vod(streamername, vod_id, timestamp, output = "separate", title = "title"):
    dt = timestamp.split()[0].split('-')
    tm = timestamp.split()[1].split(':')

    year, month, day = (int(x) for x in dt)
    hour, minute, seconds = (int(x) for x in tm)

    td = datetime.datetime(year, month, day, hour, minute, seconds)
    converted_timestamp = int(totimestamp(td))

    formattedstring = f"{streamername}_{vod_id}_{str(converted_timestamp)}"

    hash = str(hashlib.sha1(formattedstring.encode('utf-8')).hexdigest())
    requiredhash = hash[:20]

    finalformattedstring = f"{requiredhash}_{formattedstring}"

    url = f"https://vod-secure.twitch.tv/{finalformattedstring}/chunked/index-dvr.m3u8"

    if not requests.head(url, allow_redirects = False).ok:
        print(f"no valid link found {vod_id}")
        return "no valid link found"
    else:
        print(f"Completed link: {url}")
        if output == "separate":
            with open(f".\output\separate\{streamername} vod-{vod_id}.txt", "w") as vod:
                vod.writelines(url)
        return url


def main():
    print("this method should work for any vods less than 60 days old" + "\n" + "[streamer name], [vod id] and [vod time] needed")
    streamername = input("Enter streamer name >> ")
    vod_id = input("Enter vod id >> ")
    timestamp = input("Enter VOD timestamp (YYYY-MM-DD HH:MM:SS) UTC >>  ")
    get_vod(streamername, vod_id, timestamp)


if __name__ == "__main__":
    main()
