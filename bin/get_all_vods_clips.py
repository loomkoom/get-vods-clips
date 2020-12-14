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


def check_input(channel_name, vods_clips, index, start, end, download, rename, workers, test):
    if (len(channel_name) < 4 or
            (not (vods_clips == "clips" or vods_clips == "vods")) or
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
    valid_input = check_input(channel_name, vods_clips, index, start, end, download, rename, workers, test)
    if not bool(valid_input):
        return
    check_dirs(data_path)
    check_dirs(file_path)
    check_dirs(log_path)
    start_time = datetime.utcnow().strftime("%m-%d-%Y, %H.%M.%S")
    logger = set_logger(loglevel, logpath, start_time, channel_name)

    # list of streams in format: (date_time, broadcast_id, minutes, categories)
    stream_data = get_stream_data.get_data(channel_name, start, end, tracker = tracker)[index:]
    streams = len(stream_data)
    if streams == 0:
        print(f"{channel_name} has no recorded stream history")
        return

    start = stream_data[0][0][:10]
    end = stream_data[-1][0][:10]
    file_name = f"{channel_name} {vods_clips} {start} - {end}.txt"
    total_minutes = sum(map(lambda x: int(x[2]), stream_data))
    time_now = datetime.now().time().strftime("%H:%M:%S")
    if vods_clips == "vods":
        logger.info(f"\n[{time_now}]: {streams} streams found \n"
                    f"processing ... ")
    elif vods_clips == "clips":
        logger.info(f"\n[{time_now}]: {streams} streams found, {total_minutes} vod minutes \n"
                    f"[{time_now}]: {timedelta(minutes = total_minutes * 0.0043)} estimated process time \n")

    for stream in stream_data:
        date_time = stream[0]
        broadcast_id = stream[1]
        minutes = stream[2]
        title = stream[3]
        categories = stream[4]
        if vods_clips == "vods":
            log_string = f"[{time_now}]: DATE: {date_time}, ID: {broadcast_id}, LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                         f"TITLE: {title}, CATEGORIES: {categories}"
            logger.info(log_string)
            vod = get_vod.get_vod(channel_name, broadcast_id, date_time, test)
            logger.info(f"URL: {vod[0]} , MUTED: {vod[1] if vod[1] else 0}")
            data_string = f"DATE: {date_time}, URL: {vod[0]} , MUTED: {vod[1] if vod[1] else 0} , ID: {broadcast_id}, " \
                          f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                          f"TITLE: {title} , CATEGORIES: {categories} \n"
            time_now = datetime.now().time().strftime("%H:%M:%S")
            progress_string = f"streams checked {stream_data.index(stream) + 1}/{len(stream_data)}  \n" \
                              f"{floor((stream_data.index(stream) + 1) / len(stream_data) * 100)}% done "
            logger.info(progress_string)

            with open(f"{data_path}/{file_name}", "a", encoding = 'utf8') as data_log:
                data_log.write(data_string)

        elif vods_clips == "clips":
            time_now = datetime.now().time().strftime("%H:%M:%S")
            log_string = f"[{time_now}]: DATE: {date_time}, ID: {broadcast_id}, LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                         f"TITLE: {title}, CATEGORIES: {categories}"
            logger.info(log_string)
            clips = get_clips.get_clips(broadcast_id, minutes, workers)

            with open(f"{data_path}/{file_name}", "a", encoding = 'utf8') as data_log:
                for clip in clips:
                    data_string = f"DATE: {date_time}, URL: {clip[0]} , TIME: {clip[1]} , ID: {broadcast_id}, " \
                                  f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                                  f"TITLE: {title} , CATEGORIES: {categories} \n"
                    data_log.write(data_string)

            minutes_left = sum(map(lambda x: int(x[2]), stream_data[stream_data.index(stream) + 1:]))
            found_string = f"[{time_now}]: {len(clips) if clips[0][0][:2] != 'no' else 0} clips found "
            progress_string = f"streams checked {stream_data.index(stream) + 1}/{len(stream_data)}" \
                              f"{floor(((total_minutes - minutes_left) / total_minutes) * 100)}% done \n" \
                              f"estimated time left: {timedelta(minutes = minutes_left * 0.0043)}"
            logger.info(found_string + progress_string)
            logger.debug(log_string + found_string + progress_string)

            with open(f"{log_path}/{start_time} {channel_name} Logs.txt", "a", encoding = 'utf8') as progress_log:
                progress_log.write(log_string + found_string + progress_string)

    abs_data_path = os.path.abspath(data_path).replace('\\', '/')
    logger.info("\nAll retrievable links found")
    logger.info(f"{vods_clips[:-1]} links located in '{abs_data_path}/{file_name}'")

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
          "-disable testing vod playback with mpv if you get mpv errors\n\n")

    channel_name = input("channel name? >> ").strip().lower()
    vods_clips = input("clips or vods? >> ").strip().lower()
    start = input("from date (earliest) YYYY-MM-DD >> ").strip()
    end = input("to date (newest) YYYY-MM-DD >> ").strip()
    download = input("download files yes/no? >> ").strip()
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


if __name__ == "__main__":
    main()
