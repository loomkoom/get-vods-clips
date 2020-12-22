# encoding: utf-8
import logging
from datetime import datetime, timedelta
from math import floor
from pathlib import Path

import get_clips
import get_files
import get_stream_data
import get_vod


def set_logger(loglevel, log_path, channel_name):
    """Initialize logger
        - debug to file stream
        - info to output stream """
    start_time = datetime.now().strftime("%Y-%m-%d, %H.%M.%S")
    if not isinstance(loglevel, int):
        loglevels = {"NOTSET": 0, "DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
        loglevel = loglevels[loglevel.upper()]
    logger = logging.getLogger(__name__)
    logger.setLevel(loglevel)
    formatter = logging.Formatter('[%(asctime)s : %(name)s]: %(message)s')

    file_handler = logging.FileHandler(log_path / f"{start_time} {channel_name}.log", encoding = 'utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def check_dirs(path):
    """Checks if directory exists, if not creates it"""
    if not Path.is_dir(path):
        Path.mkdir(path, parents = True)


def check_input(channel_name, vods_clips, start, end, download, rename, workers, test, logger):
    """checks if input is valid returns 0 or 1"""
    if (len(channel_name) < 4 or
            (not (vods_clips == "clips" or vods_clips == "vods" or vods_clips == "both")) or
            (not (start == "" or len(start) == 10)) or
            (not (end == "" or len(end) == 10)) or
            (not (rename == "no" or rename == "yes")) or
            (not (download == "no" or download == "yes")) or
            (not (test == "no" or test == "yes")) or
            (not isinstance(workers, int))):
        logger.critical("invalid input, please try again")
        return 0
    return 1


def calculate_time(vods_clips, tracker, test, stream_data, index):
    """returns estimated time until finish"""
    stream_data = stream_data[index + 1:]
    streams = len(stream_data)
    estimated_time = timedelta(seconds = 0)
    total_minutes = sum(map(lambda x: int(x[2]), stream_data))

    if vods_clips == "vods" or vods_clips == "both":
        if tracker == "SC":
            estimated_vod_time = timedelta(seconds = streams * 35)
        elif tracker == "TT":
            if test == "yes":
                estimated_vod_time = timedelta(seconds = streams * 1.5)
            elif test == "no":
                estimated_vod_time = timedelta(seconds = streams * 0.2)
        estimated_time += estimated_vod_time
    if vods_clips == "clips" or vods_clips == "both":
        estimated_clip_time = timedelta(minutes = total_minutes * 0.0043)
        estimated_time += estimated_clip_time

    return estimated_time


def find_vod(stream, channel_name, tracker, test, file_name, data_path):
    """finds vod link and appends to file"""
    logger = logging.getLogger(__name__)
    date_time, broadcast_id, minutes, title, categories, = stream

    vod = get_vod.get_vod(channel_name, broadcast_id, date_time, tracker = tracker, test = test)
    vod_string = f"VOD: URL: {str(vod[0]).strip('][')} , MUTED: {vod[1] if vod[1] else 0}"
    data_string = f"DATE: {date_time}, URL: {vod[0]} , MUTED: {vod[1] if vod[1] else 0} , ID: {broadcast_id}, " \
                  f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                  f"TITLE: {title} , CATEGORIES: {categories} \n"

    with open(data_path / file_name, "a", encoding = 'utf8') as data_log:
        data_log.write(data_string)
    logger.info(vod_string)


def find_clips(stream, workers, file_name, data_path):
    """finds clip links and appends to file"""
    logger = logging.getLogger(__name__)
    date_time, broadcast_id, minutes, title, categories, = stream

    clips = get_clips.get_clips(broadcast_id, minutes, workers)
    with open(data_path / file_name, "a", encoding = 'utf8') as data_log:
        for clip in clips:
            data_string = f"DATE: {date_time}, URL: {clip[0]} , TIME: {clip[1]} , ID: {broadcast_id}, " \
                          f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                          f"TITLE: {title} , CATEGORIES: {categories} \n"
            data_log.write(data_string)

    found_string = f"CLIPS: {len(clips) if clips[0][0][:2] != 'no' else 0} clips found \n"
    logger.info(found_string)
    logger.debug(found_string)


def download_links(channel_name, vods_clips, rename, try_muted, file_path, file_name_vods, file_name_clips):
    """Download clips and/or vods listed in the data file"""
    logger = logging.getLogger(__name__)
    abs_file_path = Path.resolve(Path.cwd() / file_path)
    if vods_clips == "vods" or vods_clips == "both":
        logger.info("starting vods download ...")
        get_files.get_files(file_name_vods, rename, "vods", try_muted,
                            loglevel = "DEBUG")
        logger.info(f"vods downloaded at '{abs_file_path / channel_name / 'vods'}'\n")

    if vods_clips == "clips" or vods_clips == "both":
        logger.info("starting clips download ...")
        get_files.get_files(file_name_clips, rename, "clips", loglevel = "DEBUG")
        logger.info(f"clips downloaded at '{abs_file_path / channel_name / 'clips'}'\n")


def get_vods_clips(channel_name, vods_clips, start = "", end = "", tracker = "TT", download = "no", rename = "no",
                   try_muted = "yes", workers = 150, test = "yes", loglevel = "INFO"):
    data_path = Path("../output/data")
    file_path = Path("../output/files")
    log_path = Path("../output/logs")
    check_dirs(data_path)
    check_dirs(file_path)
    check_dirs(log_path)

    logger = set_logger(loglevel, log_path, channel_name)
    valid_input = check_input(channel_name, vods_clips, start, end, download, rename, workers, test, logger)
    if not bool(valid_input):
        return

    # list of streams in format: (date_time, broadcast_id, minutes, categories)
    stream_data = get_stream_data.get_data(channel_name, start, end, tracker = tracker)
    streams = len(stream_data)
    if streams == 0:
        logger.info(f"{channel_name} has no recorded stream history")
        return

    start = stream_data[0][0][:10]
    end = stream_data[-1][0][:10]

    time_now = datetime.now().time().strftime("%H:%M:%S")
    total_minutes = sum(map(lambda x: int(x[2]), stream_data))
    estimated_time = calculate_time(vods_clips, tracker, test, stream_data, -1)
    logger.info(f"\n[{time_now}]: {streams} streams found, {total_minutes} vod minutes \n"
                f"[{time_now}]: estimated process time:\t {estimated_time - timedelta(microseconds = estimated_time.microseconds)}  \n")

    for index, stream in enumerate(stream_data):
        logger.debug(f"{index}, {stream}")
        date_time, broadcast_id, minutes, title, categories, = stream
        vod_length = f"{int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min"
        log_string = f"DATE: {date_time}, ID: {broadcast_id}, LENGTH: {vod_length}, " \
                     f"TITLE: {title}, CATEGORIES: {categories}"
        logger.debug(log_string)
        logger.info(log_string)

        if vods_clips == "vods" or vods_clips == "both":
            file_name_vods = Path(f"{channel_name} vods {start} - {end}.txt")
            if index == 0:
                open(data_path / file_name_vods, "w").close()
            find_vod(stream, channel_name, tracker, test, file_name_vods, data_path)

        if vods_clips == "clips" or vods_clips == "both":
            file_name_clips = Path(f"{channel_name} clips {start} - {end}.txt")
            if index == 0:
                open(data_path / file_name_clips, "w").close()
            find_clips(stream, workers, file_name_clips, data_path)

        time_now = datetime.now().time().strftime("%H:%M:%S")
        estimated_time_left = calculate_time(vods_clips, tracker, test, stream_data, index)
        percent = floor(((estimated_time - estimated_time_left) / estimated_time) * 100)
        progress_string = f"[{time_now}]: {index + 1}/{streams} streams checked   \t" \
                          f"{percent}% done \n"
        time_left_string = f"[{time_now}]: estimated time left:\t" \
                           f" {estimated_time_left - timedelta(microseconds = estimated_time_left.microseconds)}"
        logger.info(progress_string + time_left_string)
        logger.debug(progress_string + time_left_string)

    logger.info("\nAll retrievable links found")
    abs_data_path = Path.resolve(Path.cwd() / data_path)
    file_names = list()
    if vods_clips == "vods" or vods_clips == "both":
        file_names.append(file_name_vods)
        logger.info(f"vod links located in '{abs_data_path / file_name_vods}'")
    if vods_clips == "clips" or vods_clips == "both":
        file_names.append(file_name_clips)
        logger.info(f"clip links located in '{abs_data_path / file_name_clips}'\n")

    if download == "yes":
        download_links(channel_name, vods_clips, rename, try_muted, file_path, file_name_vods, file_name_clips)

    return file_names


def main():
    print("\n-gets all clips or vod links within time period \n"
          "-Leave start and end empty to get all-time \n"
          "-input [channel name] [vods or clips] [start date] [end date] [download] \n"
          "-outputs to a file in output/data\n"
          "-for downloads outputs in output/downloads (ffmpeg needed for vod downloads)\n"
          "-worker count is set to 150 by default try changing it to a lower number"
          " if the script uses too much resources (will take an extra 2.5sec per vod) otherwise leave empty \n"
          "-disable testing vod playback if it's slow and you don't mind false positives\n"
          "-choose twitchtracker or streamcharts as tracker\n"
          "     - streamcharts:\n"
          "         PRO: can get multiple vods when stream goes down\n"
          "         CON: earliest stream history is 2019-06-00\n"
          "              considerably slower vod finding (+35sec per vod)\n"
          "     - twitchtracker:\n"
          "         PRO: fast\n"
          "              large stream history\n"
          "         CON: will merge multiple streams (can only get 1st part of vod)\n\n")

    channel_name = input("channel name? >> ").strip().lower()
    vods_clips = input("clips or vods or both? >> ").strip().lower()
    start = input("from date (earliest) YYYY-MM-DD >> ").strip()
    end = input("to date (newest) YYYY-MM-DD >> ").strip()
    download = input("download files yes/no? >> ").strip()
    tracker = input("tracker to use [TT/SC]? >> ").strip().upper()
    if download == "yes":
        rename = input("rename files after download?\n"
                       "     (clips from {ID-offset}.mp4  --->  {date}__{title}__{offset_time}-{length}_{ID-offset}.mp4\n"
                       "     (vods  from {ID}.mp4  --->  {date}_{title}_{length}_{file}_{muted}.mp4\n[yes/no]?  >>")
        use_muted = input("Download muted version when available [yes/no]? >>").strip()
    else:
        rename = "no"
        use_muted = "no"
    if vods_clips == "clips":
        workers = input("worker count (empty for default) >> ").strip()
        if workers == "":
            workers = 150
        get_vods_clips(channel_name, vods_clips, start = start, end = end, download = download, rename = rename, workers = int(workers),
                       tracker = tracker)

    if vods_clips == "vods":
        test = input("test if vod actually plays with mpv (no false positives but a bit slower) [yes/no]? >>").strip()
        get_vods_clips(channel_name, vods_clips, start = start, end = end, download = download, rename = rename, try_muted = use_muted,
                       test = test, tracker = tracker)

    elif vods_clips == "both":
        workers = input("worker count (empty for default) >> ").strip()
        if workers == "":
            workers = 150
        test = input("test if vod actually plays with mpv (no false positives but a bit slower) [yes/no]? >>").strip()
        get_vods_clips(channel_name, vods_clips, start = start, end = end, download = download, rename = rename, try_muted = use_muted,
                       test = test, workers = int(workers), tracker = tracker)


if __name__ == "__main__":
    main()
