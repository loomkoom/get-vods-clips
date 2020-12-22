# encoding: utf-8
import concurrent.futures
import hashlib
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests

import get_muted_vod
import mpv_py as mpv

logger = logging.getLogger(__name__)
formatter = logging.Formatter('[%(asctime)s : %(name)s]: %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def to_timestamp(date_time, epoch = datetime(1970, 1, 1)):
    td = date_time - epoch
    day = 60 * 60 * 24
    return (td.microseconds + (td.seconds + td.days * day) * 10 ** 6) / 10 ** 6


def get_urls(channel_name, broadcast_id, date_time):
    converted_timestamp = int(to_timestamp(date_time))
    formatted_string = f"{channel_name}_{broadcast_id}_{str(converted_timestamp)}"
    hash_string = str(hashlib.sha1(formatted_string.encode('utf-8')).hexdigest())
    required_hash = hash_string[:20]
    final_formatted_string = f"{required_hash}_{formatted_string}"

    hosts = ["https://vod-secure.twitch.tv",
             "https://d2nvs31859zcd8.cloudfront.net",
             "https://d3c27h4odz752x.cloudfront.net",
             "https://dqrpb9wgowsf5.cloudfront.net",
             "https://d2e2de1etea730.cloudfront.net",
             "https://ds0h3roq6wcgc.cloudfront.net",
             "https://vod-metro.twitch.tv"]

    urls = [f"{host}/{final_formatted_string}/chunked/index-dvr.m3u8" for host in hosts]
    return urls


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


def verify_url(urls, test, channel_name, date_time, broadcast_id, session):
    header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.323', }
    for url in urls:
        url = url.strip(" ").strip("'")
        if session.head(url, headers = header, allow_redirects = False).ok:
            if test == "yes":
                if not get_muted_vod.is_muted(url):
                    if play_url(url, channel_name):
                        logger.info(f"link found (not muted): {url}")
                        return url, False
                else:
                    muted_vod = get_muted_vod.get_muted_playlist(url, Path(f"{datetime.date(date_time)}_{broadcast_id}"))[0]
                    if play_url(muted_vod, channel_name):
                        logger.info(f"link found (muted): {url} , {muted_vod}")
                        return url, muted_vod
            elif test == "no":
                logger.info(f"link found (not tested): {url}")
                return url, False
    logger.info("no link found")
    return "no valid link", False


def get_vod(channel_name, broadcast_id, timestamp, tracker = "TT", test = "no", workers = 60, loglevel = "WARNING"):
    loglevels = {"NOTSET": 0, "DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
    loglevel = loglevels[loglevel.upper()]
    logger.setLevel(loglevel)

    channel_name = channel_name.lower()
    date_time = datetime.fromisoformat(timestamp)
    found = list()

    if len(timestamp.split(" ")[1].split(":")) == 2:
        if tracker == "SC":
            secs, mins = 600, 5
        else:
            secs, mins = 60, 0
        dates = [date_time - timedelta(minutes = mins) for i in range(secs)]
        timestamps = list(map((lambda date, sec: date + timedelta(seconds = sec)), dates, range(secs)))
        all_urls = {f"{get_urls(channel_name, broadcast_id, time_stamp)}": time_stamp for time_stamp in timestamps}
        with concurrent.futures.ThreadPoolExecutor(max_workers = workers) as executor:
            logger.info("searching all urls ...")
            with requests.session() as session:
                adapter = requests.adapters.HTTPAdapter(pool_connections = 7, pool_maxsize = workers, pool_block = True)
                session.mount('https://', adapter)
                session.mount('http://', adapter)
                future_to_url = {executor.submit(verify_url,
                                                 urls.strip("][").replace("'", "").strip(" ").split(","),
                                                 test, channel_name, date_time, broadcast_id, session = session)
                                 : urls for urls in all_urls.keys()}

                for future in concurrent.futures.as_completed(future_to_url):
                    timestamp = all_urls[f"{future_to_url[future]}"]
                    found_url = future.result()[0]
                    muted = future.result()[1]
                    if found_url != "no valid link":
                        found.append(found_url)
                        break
    else:
        urls = get_urls(channel_name, broadcast_id, date_time)
        with requests.session() as session:
            verified = verify_url(urls, test, channel_name, date_time, broadcast_id, session)
            found_url = verified[0]
            muted = verified[1]
            if found_url != "no valid link":
                found.append(found_url)
    if len(found) == 0:
        found.append("no valid link")
    return found, muted


def main():
    print("\n-returns the playlist link for a vod (m3u8 link) usually available for any vod within 60 days \n"
          "-requires [channel name], [broadcast id] and [timestamp] \n"
          "-all can be found on twitchtracker (in the streams page inspect element on the date+time link for a timestamp with seconds \n"
          "-disable testing vod playback if it's slow and you don't mind false positives\n\n")
    channel_name = input("Enter streamer name >> ").strip()
    broadcast_id = input("Enter broadcast id >> ").strip()
    timestamp = input("Enter VOD timestamp (YYYY-MM-DD HH:MM:SS) UTC >> ").strip()
    test = input("enable testing vod playback with mpv to make sure link works yes/no? >> ").strip()
    tracker = input("tracker you got data from twitchtracker/streamcharts [TT/SC]? >> ").strip().upper()
    vod = get_vod(channel_name, broadcast_id, timestamp, tracker = tracker, test = test, loglevel = "INFO")
    if test == "no":
        print("playback has not been tested, no guarantee file works")
    if vod[1]:
        print(f"\nThis vod has been muted following playlist link might not be able to play muted parts \n"
              f"{vod[0]}\n"
              f"Because of that a file has been created at output/files/{channel_name}/playlists/{vod[1]} with the muted playlist \n")
    else:
        print(f"\nURL: {vod[0]} has been found \n")
    return vod


if __name__ == "__main__":
    main()
