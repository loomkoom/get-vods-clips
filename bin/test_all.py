import datetime
import os
from datetime import timedelta

import get_all_vods_clips
import get_files
import get_vod
import get_clips
import get_stream_data
import pytest
import requests


@pytest.fixture()
def get_data_in():
    channel_name = "Hasanabi".lower()
    today = datetime.datetime.today()
    other_day = today - timedelta(days = 3)
    date_range = (other_day.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
    return [channel_name, date_range]


def test_get_stream_data(get_data_in):
    channel_name, date_1, date_2 = get_data_in[0], get_data_in[1][0], get_data_in[1][1]
    stream_data = get_stream_data.get_data(channel_name, date_1, date_2)
    assert len(stream_data) > 1, "No Streams found"
    assert len(stream_data[0]) == 4, "Stream data incomplete"


@pytest.fixture()
def get_data_stream(get_data_in):
    channel_name, date_1, date_2 = get_data_in[0], get_data_in[1][0], get_data_in[1][1]
    stream_data = get_stream_data.get_data(channel_name, date_1, date_2)
    return channel_name, stream_data


def test_get_vod_latest(get_data_stream):
    stream_data = get_data_stream
    channel_name = stream_data[0]
    stream = stream_data[1][-1]
    timestamp, broadcast_id = stream[0], stream[1]
    vod = get_vod.get_vod(channel_name, broadcast_id, timestamp)
    assert requests.head(vod[0], allow_redirects = False).ok, "4xx vod url response"


def test_get_clips(get_data_stream):
    stream = get_data_stream[1][-1]
    broadcast_id, time_offset = stream[1], stream[2]
    clips = get_clips.get_clips(broadcast_id, time_offset)
    assert len(clips) > 1, "no clips found"
    assert requests.head(clips[1][0], allow_redirects = False).ok, "clip not valid"


@pytest.mark.parametrize("vods_clips", ["vods", "clips"])
def test_get_all_vods_clips(get_data_stream, vods_clips, tmpdir,monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "no")
    output = tmpdir.mkdir("output")
    data_path = output.mkdir("data")
    file_path = output.mkdir("files")
    log_path = output.mkdir("logs")
    stream_data = get_data_stream
    channel_name = stream_data[0]
    stream = stream_data[1][-1]
    date = stream[0][:10]
    get_all_vods_clips.get_vods_clips(channel_name, vods_clips, date, date, download = "no", rename = "no", test = "no", workers = 150,
                                      datapath = data_path, filepath = file_path,logpath=log_path)
    assert os.path.isfile(f"{data_path}/{channel_name} {vods_clips} {date} - {date}.txt")
    with open(f"{data_path}/{channel_name} {vods_clips} {date} - {date}.txt", "r", encoding = "utf8") as file:
        assert len(file.readline().split(",")) == 6, "data file not correctly formatted"
