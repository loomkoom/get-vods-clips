# encoding: utf-8
import concurrent.futures
import logging
from pathlib import Path

import requests


def load_url(url, session):
    r = session.head(url, allow_redirects = False)
    return r.ok


def get_clips(broadcast_id, time_offset, file = "no", workers = 150, loglevel = "INFO"):
    loglevels = {"NOTSET": 0, "DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
    logger = logging.getLogger(__name__)
    loglevel = loglevels[loglevel.upper()]
    logger.setLevel(loglevel)

    output = list()
    time_offset = (int(time_offset) + 5) * 60 + 24
    urls = {f"https://clips-media-assets2.twitch.tv/{broadcast_id}-offset-{str(offset)}.mp4": offset for offset in range(0, time_offset)}
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.323', }

    with concurrent.futures.ThreadPoolExecutor(max_workers = workers) as executor:
        with requests.session() as session:
            logger.info("fetching clips ...")
            session.headers.update(headers)
            adapter = requests.adapters.HTTPAdapter(pool_connections = 1, pool_maxsize = workers, pool_block = True)
            session.mount('https://', adapter)
            session.mount('http://', adapter)

            future_to_url = {executor.submit(load_url, url, session = session): url for url in urls.keys()}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                if future.result():
                    offset_time = urls[url] - 24
                    hr = offset_time // 3600
                    mins = (offset_time % 3600) // 60
                    sec = (offset_time % 60)
                    offset_time = f"{str(hr).zfill(2)}:{str(mins).zfill(2)}:{str(sec).zfill(2)}"
                    logger.debug(f"clip found at {offset_time}")
                    output.append((url, offset_time))

    if len(output) > 0:
        output.sort(key = lambda x: x[57:-4])
        if file == "yes":
            file_name = f"{broadcast_id}_clips.txt"
            data_path = Path("../output/data")
            if not Path.is_dir(data_path):
                Path.mkdir(data_path, parents = True)
            with open(data_path / f"{file_name}", "w", encoding = 'utf8') as data_log:
                for clip in output:
                    data_string = f"URL: {clip[0]} , TIME: {clip[1]}\n"
                    data_log.write(data_string)
        logger.info(f"{len(output)} links found")
        return output
    return [("no valid clips found,", "None")]


def main():
    print("\n-gets all clips from a vod, you can round up vod length as it is just the upper border to search for clips \n"
          "-worker count is set to 150 by default try changing it to a lower number"
          " if the script uses too much resources (will be slower) otherwise leave empty \n"
          "-input [broadcast id] [vod length](minutes) \n"
          "-outputs a list of valid clips with each clip as (url,offset time)\n\n")
    broadcast_id = input("broadcast id >> ").strip()
    time_offset = input("vod length in minutes >> ").strip()
    file = input("save output to file? [yes/no] >> ").strip()
    workers = input("worker count (empty for default) >> ").strip()
    if workers == "":
        workers = 150
    clips = get_clips(broadcast_id, time_offset, file, int(workers))

    for clip in clips:
        print(clip)
    return clips


if __name__ == "__main__":
    main()
