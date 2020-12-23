# encoding: utf-8
import time
import pytest
import requests

import mpv_py as mpv


def test_sites():
    headers = {
            'Accept'                   : 'text/html,application/xhtml+xml,application/xml;q=0.9,application/json,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding'          : 'gzip, deflate',
            'Accept-Language'          : 'en-US,en;q=0.9,nl;q=0.8',
            'Dnt'                      : '1',
            'Sec-Gpc'                  : '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent'               : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.323',
            }
    with requests.session() as session:
        session.headers.update(headers)
        resp_tt = session.head("https://twitchtracker.com/statistics")
        resp_sc = session.head("https://streamscharts.com/twitch")
        resp_sc_api = session.head("https://alla.streamscharts.com/api/free/streaming/platforms/1/top-channels?withPreviousPeriod=0")
        resp_twitch_clips = session.head("https://clips-media-assets2.twitch.tv/36263368672-offset-406.mp4")
    assert resp_tt, "can't reach twitchtracker"
    assert resp_sc, "can't reach streamcharts"
    assert resp_sc_api, "can't reach streamcharts api"
    assert resp_twitch_clips, "can't reach twitch clips host"


@pytest.mark.parametrize("url", [
        "https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8",
        "https://bitdash-a.akamaihd.net/content/MI201109210084_1/m3u8s/f08e80da-bf1d-4e3d-8899-f0f6155f6efa.m3u8"])
def test_mpv(url):
    player = mpv.MPV(window_minimized = "yes", osc = "no", load_osd_console = "no", load_stats_overlay = "no", profile = "low-latency",
                     frames = "1", untimed = "yes", demuxer = "lavf", demuxer_lavf_format = "hls", demuxer_thread = "no", cache = "no",
                     ytdl = "no", load_scripts = "no", audio = "no", demuxer_lavf_o = '"protocol_whitelist"="file,https,http,tls,tcp"',
                     video = "no", sid = "no", hls_bitrate = "no")
    player.play(url)
    start = time.time()
    player.wait_for_playback(timeout = 5)
    player.quit()
    time_taken = time.time() - start
    assert time_taken < 4.99
