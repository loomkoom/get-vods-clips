# encoding: utf-8
import time
from datetime import timedelta
from pathlib import Path
import requests

import mpv_py


def play_url(url):
    player = mpv_py.MPV(window_minimized = "yes", osc = "no", load_osd_console = "no", load_stats_overlay = "no", profile = "low-latency",
                        frames = "1", untimed = "yes", demuxer = "lavf", demuxer_lavf_format = "hls", demuxer_thread = "no", cache = "no",
                        ytdl = "no", load_scripts = "no", audio = "no", demuxer_lavf_o = '"protocol_whitelist"="file,https,http,tls,tcp"')
    player.play(url)
    timeout = 2.5
    start = time.time()
    player.wait_until_playing(timeout)
    player.quit()
    time_taken = time.time() - start
    return not (time_taken >= 2.499)


def validate_vods(file_name, new_file_name):
    file_name = Path.with_suffix(Path(file_name), ".txt")
    path = Path("../output/data")
    with open(path / file_name, "r", encoding = 'utf8') as file:
        output = list()
        streams = list(filter((lambda x: any(s in x for s in (".twitch.tv", ".cloudfront.net"))), file.readlines()))
        print(f"estimated run time: {timedelta(seconds = 5 * len(streams))}")
        for stream in streams:
            data = stream.split(',')
            url = data[1].strip()[5:]
            if requests.head(url).ok:
                played = play_url(url)
                if played:
                    output.append(stream)

    with open(path / new_file_name, "w", encoding = 'utf8') as file:
        file.writelines(output)


def main():
    print("\n-tests all vod links in file using mpv \n"
          "-input [input file name] and [output file name] only for files in /output/data/\n")

    input_file = input("input file name?  >> ").strip()
    output_file = input("output file name?  >> ").strip()
    validate_vods(input_file, output_file)


if __name__ == "__main__":
    main()
