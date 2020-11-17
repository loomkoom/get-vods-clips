import datetime
import hashlib
import time
from pathlib import Path

import get_muted_vod
import m3u8
import requests
import vlc


def to_timestamp(date_time, epoch = datetime.datetime(1970, 1, 1)):
    td = date_time - epoch
    return (td.microseconds + (td.seconds + td.days * 86400) * 10 ** 6) / 10 ** 6


def is_muted(url):
    playlist_url = m3u8.load(url)
    for uri in playlist_url.segments.uri:
        if uri.endswith("-unmuted.ts"):
            return True
    return False


def play_url(url):
    if not url.startswith("http"):
        url = str(Path(__file__).parents[1]).replace('\\', '/') + f"/output/files/playlists/{url}"
    instance = vlc.Instance()
    instance.log_unset()
    player = instance.media_player_new()
    player.set_mrl(f"{url}")
    player.play()
    player.audio_set_mute(True)
    start = time.time()
    timeout = 4
    while not player.get_state() == vlc.State.Ended and time.time() - start < timeout:
        time.sleep(0.1)
    if int(player.is_playing()):
        player.pause()
        player.stop()
    return player.get_state() == vlc.State.Stopped


def get_vod(channel_name, vod_id, timestamp,test="yes"):
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
        if test == "yes":
            if not is_muted(url):
                if play_url(url):
                    return url, None
            else:
                muted_vod = get_muted_vod.get_muted_playlist(url, str(vod_id))
                if play_url(muted_vod):
                    return url, muted_vod
        elif test == "no":
            return url, None
    return "no valid link", None


def main():
    print("returns the playlist link for a vod (m3u8 link) \n"
          "requires [channel name], [vod id] and [timestamp] \n"
          "all can be found on twitchtracker (in the streams page inspect element on the date+time link for a timestamp with seconds \n"
          "disable testing vod playback with vlc if you get vlc errors")
    channel_name = input("Enter streamer name >>").strip()
    vod_id = input("Enter vod id >>").strip()
    timestamp = input("Enter VOD timestamp (YYYY-MM-DD HH:MM:SS) UTC >>").strip()
    test = input("disable testing vod playback with vlc to make sure link works yes/no? >>").strip()
    vod = get_vod(channel_name, vod_id, timestamp,test)
    if test == "no":
        print("playback has not been tested, no guarantee file works")
    if vod[1] is not None:
        print(f"\n This vod has been muted following playlist link might not be able to play muted parts \n"
              f"{vod[0]}\n"
              f"Because of that a file has been created at output/files/playlists/{vod[1]} with the muted playlist \n")
    else:
        print(f"\nURL: {vod[0]} has been found \n")


if __name__ == "__main__":
    main()
