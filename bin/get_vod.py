# encoding: utf-8
import datetime
import hashlib
import time
from pathlib import Path

import requests

import get_muted_vod
import mpv_py as mpv


def to_timestamp(date_time, epoch = datetime.datetime(1970, 1, 1)):
    td = date_time - epoch
    day = 60 * 60 * 24
    return (td.microseconds + (td.seconds + td.days * day) * 10 ** 6) / 10 ** 6


def extract_timestamp(timestamp):
    dt = timestamp.split()[0].split('-')
    tm = timestamp.split()[1].split(':')

    y, m, d = (int(x) for x in dt)
    hr, mins, sec = (int(x) for x in tm)
    return y, m, d, hr, mins, sec


def play_url(url, channel_name):
    if not url.startswith("http"):
        url = str(Path(__file__).parents[1]).replace('\\', '/') + f"/output/files/{channel_name}/playlists/{url}"
    player = mpv.MPV(window_minimized = "yes", osc = "no", load_osd_console = "no", load_stats_overlay = "no", profile = "low-latency",
                     frames = "1", untimed = "yes", demuxer = "lavf", demuxer_lavf_format = "hls", demuxer_thread = "no", cache = "no",
                     ytdl = "no", load_scripts = "no", audio = "no", demuxer_lavf_o = '"protocol_whitelist"="file,https,http,tls,tcp"')
    player.play(url)
    timeout = 2.5
    start = time.time()
    player.wait_until_playing(timeout)
    player.quit()
    time_taken = time.time() - start
    return not (time_taken >= 2.499)


def get_vod(channel_name, broadcast_id, timestamp, test = "no"):
    channel_name = channel_name.lower()

    y, mt, d, h, mn, s = extract_timestamp(timestamp)
    date_time = datetime.datetime(y, mt, d, h, mn, s)
    converted_timestamp = int(to_timestamp(date_time))

    formatted_string = f"{channel_name}_{broadcast_id}_{str(converted_timestamp)}"
    hash_string = str(hashlib.sha1(formatted_string.encode('utf-8')).hexdigest())
    required_hash = hash_string[:20]
    final_formatted_string = f"{required_hash}_{formatted_string}"

    url = f"https://vod-secure.twitch.tv/{final_formatted_string}/chunked/index-dvr.m3u8"
    header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.323', }

    if requests.head(url, headers = header, allow_redirects = False).ok:
        if test == "yes":
            if not get_muted_vod.is_muted(url):
                if play_url(url, channel_name):
                    return url, False
            else:
                muted_vod = get_muted_vod.get_muted_playlist(url, f"{datetime.datetime.date(date_time)}_{broadcast_id}")
                if play_url(muted_vod, channel_name):
                    return url, muted_vod
        elif test == "no":
            return url, False
    return "no valid link", False


def main():
    print("\n-returns the playlist link for a vod (m3u8 link) usually available for any vod within 60 days \n"
          "-requires [channel name], [broadcast id] and [timestamp] \n"
          "-all can be found on twitchtracker (in the streams page inspect element on the date+time link for a timestamp with seconds \n"
          "-enable testing vod playback with mpv if you non working links (no false positives) takes a little longer and less stable\n\n")
    channel_name = input("Enter streamer name >> ").strip()
    broadcast_id = input("Enter broadcast id >> ").strip()
    timestamp = input("Enter VOD timestamp (YYYY-MM-DD HH:MM:SS) UTC >> ").strip()
    test = input("enable testing vod playback with mpv to make sure link works yes/no? >> ").strip()
    vod = get_vod(channel_name, broadcast_id, timestamp, test)
    if test == "no":
        print("playback has not been tested, no guarantee file works")
    if vod[1]:
        print(f"\nThis vod has been muted following playlist link might not be able to play muted parts \n"
              f"{vod[0]}\n"
              f"Because of that a file has been created at output/files/{channel_name}/playlists/{vod[1]} with the muted playlist \n")
    else:
        print(f"\nURL: {vod[0]} has been found \n")


if __name__ == "__main__":
    main()
