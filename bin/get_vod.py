import datetime
import hashlib
import time

import requests
import vlc


def to_timestamp(date_time, epoch = datetime.datetime(1970, 1, 1)):
    td = date_time - epoch
    return (td.microseconds + (td.seconds + td.days * 86400) * 10 ** 6) / 10 ** 6


def play_url(url):
    instance = vlc.Instance()
    instance.log_unset()
    player = instance.media_player_new()
    player.set_mrl(f"{url}")
    player.play()
    player.audio_set_mute(True)
    start = time.time()
    timeout = 5
    while not player.get_state() == vlc.State.Ended and time.time() - start < timeout:
        time.sleep(0.1)
    if int(player.is_playing()):
        player.pause()
        player.stop()
    return player.get_state() == vlc.State.Stopped


def get_vod(channel_name, vod_id, timestamp):
    dt = timestamp.split()[0].split('-')
    tm = timestamp.split()[1].split(':')

    y, m, d = (int(x) for x in dt)
    hr, mins, sec = (int(x) for x in tm)

    date_time = datetime.datetime(y, m, d, hr, mins, sec)
    converted_timestamp = int(to_timestamp(date_time))

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


def main():
    print("returns the playlist file for a vod (m3u8 link) \n"
          "requires [channel name], [vod id] and [timestamp] all can be found on twitchtracker \n")
    channel_name = input("Enter streamer name >>").strip()
    vod_id = input("Enter vod id >>").strip()
    timestamp = input("Enter VOD timestamp (YYYY-MM-DD HH:MM:SS) UTC >>").strip()
    print(get_vod(channel_name, vod_id, timestamp))


if __name__ == "__main__":
    main()
