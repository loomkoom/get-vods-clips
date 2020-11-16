import datetime
import hashlib
from time import sleep

import requests
import vlc


def to_timestamp(dt, epoch = datetime.datetime(1970, 1, 1)):
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 86400) * 10 ** 6) / 10 ** 6


def get_vod(channel_name, vod_id, timestamp):
    dt = timestamp.split()[0].split('-')
    tm = timestamp.split()[1].split(':')

    year, month, day = (int(x) for x in dt)
    hour, minute, seconds = (int(x) for x in tm)

    td = datetime.datetime(year, month, day, hour, minute, seconds)
    converted_timestamp = int(to_timestamp(td))

    formatted_string = f"{channel_name}_{vod_id}_{str(converted_timestamp)}"
    hash_string = str(hashlib.sha1(formatted_string.encode('utf-8')).hexdigest())
    required_hash = hash_string[:20]
    final_formatted_string = f"{required_hash}_{formatted_string}"

    url = f"https://vod-secure.twitch.tv/{final_formatted_string}/chunked/index-dvr.m3u8"

    if requests.head(url, allow_redirects = False).ok:
        if play_url(url):
            return url
    else:
        return "no valid link found"


def play_url(url):
    played = False
    instance = vlc.Instance()
    instance.log_unset()
    player = instance.media_player_new()
    player.set_mrl(f"{url}")
    player.play()
    player.audio_set_mute(True)
    sleep(2.5)
    if player.is_playing() == 1:
        played = True
    player.stop()
    return played


def main():
    channel_name = input("Enter streamer name >> ")
    vod_id = input("Enter vod id >> ")
    timestamp = input("Enter VOD timestamp (YYYY-MM-DD HH:MM:SS) UTC >>  ")
    print(get_vod(channel_name, vod_id, timestamp))


if __name__ == "__main__":
    main()
