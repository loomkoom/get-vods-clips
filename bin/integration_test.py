# encoding: utf-8
import datetime
import os
from datetime import timedelta
from math import floor
from pathlib import Path
from random import choice

import pytest
import requests

import get_all_vods_clips
import get_clips
import get_clips_date
import get_stream_data
import get_vod
import get_vods_date


@pytest.fixture()
def get_data_in():
    channels = ["hasanabi", "xqcow", "shroud", "mizkif"]
    channel_name = choice(channels).lower()
    today = datetime.datetime.today()
    other_day = today - timedelta(days = 7)
    date_range = (other_day.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
    return [channel_name, date_range]


# test get stream data
@pytest.mark.parametrize("tracker", ["TT", "SC"])
def test_get_stream_data_daterange(get_data_in, tracker):
    channel_name, date_1, date_2 = get_data_in[0], get_data_in[1][0], get_data_in[1][1]
    stream_data = get_stream_data.get_data(channel_name, start = date_1, end = date_2, tracker = tracker, loglevel = "DEBUG")
    assert len(stream_data) > 1, "No Streams found"
    assert len(stream_data[0]) == 5, "Stream data incomplete"


@pytest.mark.parametrize("tracker", ["TT", "SC"])
def test_get_stream_data_all(get_data_in, tracker):
    channel_name = get_data_in[0]
    stream_data = get_stream_data.get_data(channel_name, tracker = tracker, loglevel = "DEBUG")
    assert len(stream_data) > 1, "No Streams found"
    assert len(stream_data[0]) == 5, "Stream data incomplete"


@pytest.mark.parametrize("tracker", ["TT", "SC"])
def test_get_stream_data_start(get_data_in, tracker):
    channel_name, date = get_data_in[0], get_data_in[1][0]
    stream_data = get_stream_data.get_data(channel_name, start = date, tracker = tracker, loglevel = "DEBUG")
    assert len(stream_data) > 1, "No Streams found"
    assert len(stream_data[0]) == 5, "Stream data incomplete"


@pytest.mark.parametrize("tracker", ["TT", "SC"])
def test_get_stream_data_end(get_data_in, tracker):
    channel_name, date = get_data_in[0], get_data_in[1][1]
    stream_data = get_stream_data.get_data(channel_name, end = date, tracker = tracker, loglevel = "DEBUG")
    assert len(stream_data) > 1, "No Streams found"
    assert len(stream_data[0]) == 5, "Stream data incomplete"


@pytest.fixture()
def get_data_stream(get_data_in):
    channel_name, date_1, date_2 = get_data_in[0], get_data_in[1][0], get_data_in[1][1]
    stream_data = get_stream_data.get_data(channel_name, date_1, date_2, loglevel = "DEBUG")
    return channel_name, stream_data


# test get vod
def test_get_vod_latest_no_play(get_data_stream):
    stream_data = get_data_stream
    channel_name = stream_data[0]
    stream = choice(stream_data[1])
    timestamp, broadcast_id = stream[0], stream[1]
    vod = get_vod.get_vod(channel_name, broadcast_id, timestamp, loglevel = "DEBUG")
    urls = vod[0]
    for url in urls:
        if url != "no valid link":
            assert requests.head(url, allow_redirects = False).ok, "4xx vod url response"


def test_get_vod_latest_play(get_data_stream, tmpdir):
    output = tmpdir.mkdir("output")
    file_path = output.mkdir("files")
    stream_data = get_data_stream
    channel_name = stream_data[0]
    stream = choice(stream_data[1])
    timestamp, broadcast_id = stream[0], stream[1]
    vod = get_vod.get_vod(channel_name, broadcast_id, timestamp, test = "yes", file_path = Path(file_path), loglevel = "DEBUG")
    urls = vod[0]
    for url in urls:
        if url != "no valid link":
            assert requests.head(url, allow_redirects = False).ok, "4xx vod url response"
            assert get_vod.play_url(url, channel_name), "Vod not playable"


# test get vods date
@pytest.mark.parametrize("tracker", ["TT", "SC"])
def test_get_vods_date(get_data_stream, tracker):
    stream_data = get_data_stream
    channel_name = stream_data[0]
    stream = choice(stream_data[1])
    date = stream[0].split(" ")[0]
    vod = get_vods_date.get_vods(channel_name, date, test = "no", tracker = tracker, loglevel = "DEBUG")
    url = vod[0].split(",")[1].strip()[5:].strip("][").replace("'", "")
    if url != "no valid link":
        assert requests.head(url, allow_redirects = False).ok, "4xx vod url response"


def test_get_vods_date_play(get_data_stream, tmpdir):
    output = tmpdir.mkdir("output")
    file_path = output.mkdir("files")
    stream_data = get_data_stream
    channel_name = stream_data[0]
    stream = choice(stream_data[1])
    date = stream[0].split(" ")[0]
    vod = get_vods_date.get_vods(channel_name, date, test = "yes", file_path = Path(file_path), loglevel = "DEBUG")
    url = vod[0].split(",")[1].strip()[5:].strip("][").replace("'", "")
    if url != "no valid link":
        assert requests.head(url, allow_redirects = False).ok, "4xx vod url response"
        assert get_vod.play_url(url, channel_name), "Vod not playable"


# test get clips
def test_get_clips(get_data_stream):
    stream = choice(get_data_stream[1])
    broadcast_id, time_offset = stream[1], stream[2]
    clips = get_clips.get_clips(broadcast_id, time_offset, loglevel = "DEBUG")
    assert len(clips) > 1, "no valid clips found"
    assert requests.head(clips[1][0], allow_redirects = False).ok, "clip not valid"


def test_get_clips_file(get_data_stream, tmpdir):
    output = tmpdir.mkdir("output")
    data_path = output.mkdir("data")
    stream = choice(get_data_stream[1])
    broadcast_id, time_offset = stream[1], floor(int(stream[2]) / 5)
    clips = get_clips.get_clips(broadcast_id, time_offset, file = "yes", data_path = Path(data_path), loglevel = "DEBUG")
    assert len(clips) > 1, "no valid clips found"
    assert requests.head(clips[1][0], allow_redirects = False).ok, "clip not valid"
    assert os.path.isfile(f"{data_path}/{broadcast_id}_clips.txt"), "File not made"
    with open(f"{data_path}/{broadcast_id}_clips.txt", "r", encoding = "utf8") as file:
        assert len(file.readline().split(",")) == 2, "data file not correctly formatted"
        file.seek(0)
        url = file.readline().split(",")[0].strip()[5:]
        assert requests.head(url, allow_redirects = False).ok, "clip not valid"


# test get clips date
def test_get_clips_date(get_data_stream):
    stream_data = get_data_stream
    channel_name = stream_data[0]
    stream = choice(get_data_stream[1])
    date = stream[0].split(" ")[0]
    clips = get_clips_date.get_clips_date(channel_name, date, loglevel = "DEBUG")
    assert len(clips) > 1, "no valid clips found"
    url = clips[0].split(",")[1].strip()[5:]
    if url != "no valid clips found":
        assert requests.head(url, allow_redirects = False).ok, "clip not valid"


def test_get_clips_date_file(get_data_stream, tmpdir):
    output = tmpdir.mkdir("output")
    data_path = output.mkdir("data")
    stream_data = get_data_stream
    channel_name = stream_data[0]
    stream = choice(get_data_stream[1])
    date = stream[0].split(" ")[0]
    clips = get_clips_date.get_clips_date(channel_name, date, file = "yes", data_path = Path(data_path), loglevel = "DEBUG")
    url = clips[0].split(",")[1].strip()[5:]
    assert len(clips) > 1, "no valid clips found"
    assert requests.head(url, allow_redirects = False).ok, "clip not valid"
    assert os.path.isfile(f"{data_path}/{channel_name} clips {date}.txt"), "File not made"
    with open(f"{data_path}/{channel_name} clips {date}.txt", "r", encoding = "utf8") as file:
        assert len(file.readline().split(",")) == 7, "data file not correctly formatted"
        file.seek(0)
        url = file.readline().split(",")[1].strip()[5:]
        assert requests.head(url, allow_redirects = False).ok, "clip not valid"


# test get_all_vods_clips
@pytest.mark.parametrize("tracker", ["TT", "SC"])
def test_get_all_vods_clips(get_data_stream, tracker, tmpdir):
    output = tmpdir.mkdir("output")
    data_path = output.mkdir("data")
    file_path = output.mkdir("files")
    log_path = output.mkdir("logs")
    stream_data = get_data_stream
    channel_name = stream_data[0]
    stream = choice(stream_data[1])
    date = stream[0].split(" ")[0]
    vods_clips = "both"
    get_all_vods_clips.get_vods_clips(channel_name, vods_clips, start = date, end = date, download = "no", rename = "no",
                                      test = "no", workers = 150, tracker = tracker, loglevel = "DEBUG",
                                      data_path = Path(data_path), file_path = Path(file_path), log_path = Path(log_path))
    assert os.path.isfile(f"{data_path}/{channel_name} clips {date} - {date}.txt")
    with open(f"{data_path}/{channel_name} clips {date} - {date}.txt", "r", encoding = "utf8") as file:
        assert len(file.readline().split(",")) == 7, "data file not correctly formatted"
        file.seek(0)
        url = file.readline().split(",")[1].strip()[5:]
        url = url.strip("'")
        if url != "no valid link":
            assert requests.head(url, allow_redirects = False).ok, "link not valid"
    assert os.path.isfile(f"{data_path}/{channel_name} vods {date} - {date}.txt")
    with open(f"{data_path}/{channel_name} vods {date} - {date}.txt", "r", encoding = "utf8") as file:
        assert len(file.readline().split(",")) == 7, "data file not correctly formatted"
        file.seek(0)
        url = file.readline().split(",")[1].strip()[5:]
        if "[" in url:
            url = url.strip("][").strip("'")
        if url != "no valid link":
            assert requests.head(url, allow_redirects = False).ok, "link not valid"
