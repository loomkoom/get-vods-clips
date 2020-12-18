# encoding: utf-8
import logging
import os
from datetime import datetime, timedelta
from math import floor

import get_clips
import get_files
import get_stream_data
import get_vod


def set_logger(loglevel, logpath, start_time, channel_name):
    if not isinstance(loglevel, int):
        loglevels = {"NOTSET": 0, "DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
        loglevel = loglevels[loglevel.upper()]
    logger = logging.getLogger(__name__)
    logger.setLevel(loglevel)
    formatter = logging.Formatter('[%(asctime)s : %(name)s]: %(message)s')

    file_handler = logging.FileHandler(f"{logpath}/{start_time} {channel_name} Logs.log", encoding = 'utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def check_dirs(path):
    """Checks if directory exists, if not creates it"""
    if not os.path.isdir(path):
        parent_path = "/".join(path.split("/")[:-1])
        if not os.path.isdir(parent_path):
            os.mkdir(parent_path)
        os.mkdir(path)


def check_input(channel_name, vods_clips, index, start, end, download, rename, workers, test, logger):
    if (len(channel_name) < 4 or
            (not (vods_clips == "clips" or vods_clips == "vods" or vods_clips == "both")) or
            (not (start == "" or len(start) == 10)) or
            (not (end == "" or len(end) == 10)) or
            (not (rename == "no" or rename == "yes")) or
            (not (download == "no" or download == "yes")) or
            (not (test == "no" or test == "yes")) or
            (not isinstance(workers, int)) or
            (not isinstance(index, int))):
        logger.critical("invalid input, please try again")
        return 0
    return 1


def get_vods_clips(channel_name, vods_clips, index = 0, start = "", end = "", tracker = "TT", download = "no", rename = "no", workers = 150,
                   test = "yes", data_path = "../output/data", file_path = "../output/files", log_path = "../output/logs",
                   loglevel = "INFO"):
    check_dirs(data_path)
    check_dirs(file_path)
    check_dirs(log_path)
    start_time = datetime.now().strftime("%m-%d-%Y, %H.%M.%S")
    logger = set_logger(loglevel, log_path, start_time, channel_name)
    valid_input = check_input(channel_name, vods_clips, index, start, end, download, rename, workers, test, logger)
    if not bool(valid_input):
        return

    # list of streams in format: (date_time, broadcast_id, minutes, categories)
    stream_data = get_stream_data.get_data(channel_name, start, end, tracker = tracker)[index:]
    streams = len(stream_data)
    if streams == 0:
        logger.info(f"{channel_name} has no recorded stream history")
        return

    start = stream_data[0][0][:10]
    end = stream_data[-1][0][:10]

    total_minutes = sum(map(lambda x: int(x[2]), stream_data))
    time_now = datetime.now().time().strftime("%H:%M:%S")
    if vods_clips == "vods":
        logger.info(f"\n[{time_now}]: {streams} streams found \n"
                    f"processing ... ")
    elif vods_clips == "clips" or vods_clips == "both":
        logger.info(f"\n[{time_now}]: {streams} streams found, {total_minutes} vod minutes \n"
                    f"[{time_now}]: {timedelta(minutes = total_minutes * 0.0043)} estimated process time \n"
                    f"processing ... \n")

    for stream in stream_data:
        date_time = stream[0]
        broadcast_id = stream[1]
        minutes = stream[2]
        title = stream[3]
        categories = stream[4]
        if vods_clips == "vods" or vods_clips == "both":
            file_name = f"{channel_name} vods {start} - {end}.txt"
            log_string = f"DATE: {date_time}, ID: {broadcast_id}, LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                         f"TITLE: {title}, CATEGORIES: {categories}"
            logger.info(log_string)
            vod = get_vod.get_vod(channel_name, broadcast_id, date_time, test)
            logger.info(f"VOD: URL: {str(vod[0]).strip('][')} , MUTED: {vod[1] if vod[1] else 0}")
            data_string = f"DATE: {date_time}, URL: {vod[0]} , MUTED: {vod[1] if vod[1] else 0} , ID: {broadcast_id}, " \
                          f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                          f"TITLE: {title} , CATEGORIES: {categories} \n"
            time_now = datetime.now().time().strftime("%H:%M:%S")
            progress_string = f"[{time_now}]: {stream_data.index(stream) + 1}/{len(stream_data)} streams checked \t" \
                              f"{floor((stream_data.index(stream) + 1) / len(stream_data) * 100)}% done"
            if vods_clips != "both":
                logger.info(progress_string)

            with open(f"{data_path}/{file_name}", "a", encoding = 'utf8') as data_log:
                data_log.write(data_string)

        if vods_clips == "clips" or vods_clips == "both":
            file_name = f"{channel_name} clips {start} - {end}.txt"
            time_now = datetime.now().time().strftime("%H:%M:%S")
            log_string = f"DATE: {date_time}, ID: {broadcast_id}, LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                         f"TITLE: {title}, CATEGORIES: {categories}"
            if vods_clips != "both":
                logger.info(log_string)
            clips = get_clips.get_clips(broadcast_id, minutes, workers)

            with open(f"{data_path}/{file_name}", "a", encoding = 'utf8') as data_log:
                for clip in clips:
                    data_string = f"DATE: {date_time}, URL: {clip[0]} , TIME: {clip[1]} , ID: {broadcast_id}, " \
                                  f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                                  f"TITLE: {title} , CATEGORIES: {categories} \n"
                    data_log.write(data_string)

            minutes_left = sum(map(lambda x: int(x[2]), stream_data[stream_data.index(stream) + 1:]))
            timedelta_left = timedelta(minutes = minutes_left * 0.0043)
            timedelta_left -= timedelta(microseconds = timedelta_left.microseconds)
            found_string = f"CLIPS: {len(clips) if clips[0][0][:2] != 'no' else 0} clips found \n"
            progress_string = f"[{time_now}]: {stream_data.index(stream) + 1}/{len(stream_data)} streams checked \t" \
                              f"{floor(((total_minutes - minutes_left) / total_minutes) * 100)}% done \n" \
                              f"[{time_now}]: estimated time left: {timedelta_left} \n"

            logger.info(found_string + progress_string)
            logger.debug(log_string + found_string + progress_string)

            with open(f"{log_path}/{start_time} {channel_name} Logs.txt", "a", encoding = 'utf8') as progress_log:
                progress_log.write(log_string + found_string + progress_string)

    abs_data_path = os.path.abspath(data_path).replace('\\', '/')
    logger.info("\nAll retrievable links found")
    if not vods_clips == "both":
        logger.info(f"{vods_clips[:-1]} links located in '{abs_data_path}/{file_name}'")
    else:
        logger.info(f"vod links located in '{abs_data_path}/{channel_name} vods {start} - {end}.txt'")
        logger.info(f"clips links located in '{abs_data_path}/{channel_name} clips {start} - {end}.txt'")

    if download == "yes":
        abs_file_path = os.path.abspath(file_path).replace('\\', '/')

        logger.info("starting download")
        get_files.get_files(file_name, rename, data_path = data_path, file_path = file_path)
        logger.info("download finished")
        logger.info(f"files downloaded at '{abs_file_path}/{file_name}/{channel_name}/'\n")

    return file_name


def main():
    print("\n-gets all clips or vod links within time period \n"
          "-Leave start and end empty to get all-time \n"
          "-input [channel name] [vods or clips] [start date] [end date] [download] \n"
          "-outputs to a file in output/data\n"
          "-for downloads outputs in output/downloads (ffmpeg needed for vod downloads)\n"
          "-worker count is set to 150 by default try changing it to a lower number"
          " if the script uses too much resources (will take an extra 2.5sec per vod) otherwise leave empty \n"
          "-disable testing vod playback if it's slow and you don't mind false positives\n"
          "-choose twitchtracker or steamcharts as tracker\n"
          "     - streamcharts:\n"
          "         PRO: can get multiple vods when stream goes down\n"
          "         CON: earliest stream history is 2019-06-00\n"
          "              slower data retrieval and slower vod finding\n"
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
    else:
        rename = "no"
    if vods_clips == "clips":
        workers = input("worker count (empty for default) >> ").strip()
        if workers == "":
            workers = 150
        get_vods_clips(channel_name, vods_clips, 0, start = start, end = end, download = download, rename = rename, workers = workers)

    if vods_clips == "vods":
        test = input("test if vod actually plays with mpv (no false positives but a bit slower) [yes/no]? >>").strip()
        get_vods_clips(channel_name, vods_clips, 0, start = start, end = end, download = download, rename = rename, test = test)

    elif vods_clips == "both":
        workers = input("worker count (empty for default) >> ").strip()
        if workers == "":
            workers = 150
        test = input("test if vod actually plays with mpv (no false positives but a bit slower) [yes/no]? >>").strip()
        get_vods_clips(channel_name, vods_clips, 0, start = start, end = end, download = download, rename = rename, test = test,
                       workers = workers)


if __name__ == "__main__":
    main()
