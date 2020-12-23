# encoding: utf-8
import logging
from pathlib import Path

import get_clips
import get_stream_data

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def get_clips_date(channel_name, date, tracker = "SC", file = "no", workers = 150, loglevel = "INFO"):
    if not isinstance(loglevel, int):
        loglevels = {"NOTSET": 0, "DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
        loglevel = loglevels[loglevel.upper()]
    logger.setLevel(loglevel)
    if (len(channel_name) < 4 or
            (not (len(date) == 10 and len(date.split("-")[0]) == 4)) or
            (not (file == "yes" or file == "no")) or
            (not (tracker == "TT" or tracker == "SC")) or
            (not isinstance(workers, int))):
        logger.critical("\ninvalid input data, check that date is in the correct format (YYYY-MM-DD)")
        return

    file_name = f"{channel_name} clips {date}.txt"
    clips_lst = []
    logger.info("fetching stream data")
    stream_data = get_stream_data.get_data(channel_name, date, date, tracker = tracker)
    if len(stream_data) == 0:
        logger.info(f"{tracker} found no stream for {channel_name} on {date}")
        return
    for stream in stream_data:
        logger.debug(stream)
        date_time, broadcast_id, minutes, title, categories = stream
        logger.info(f"fetching clips for stream {stream_data.index(stream) + 1}")
        clips = get_clips.get_clips(broadcast_id, minutes, workers)

        for clip in clips:
            data_string = f"DATE: {date_time}, URL: {clip[0]} , TIME: {clip[1]} , ID: {broadcast_id}, " \
                          f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                          f"TITLE: {title} , CATEGORIES: {categories}\n"
            clips_lst.append(data_string)
        if file == "yes":
            data_path = Path("../output/data")
            if not Path.is_dir(data_path):
                Path.mkdir(data_path, parents = True)
            with open(data_path / f"{file_name}", "w", encoding = 'utf8') as data_log:
                data_log.writelines(clips_lst)
    logger.debug(clips_lst)
    return clips_lst


def main():
    print("\n-gets all clips from a specific date\n"
          "-worker count is set to 150 by default try changing it to a lower number"
          " if the script uses too much resources (will be slower) otherwise leave empty \n"
          "-input [channel name] and [date] \n"
          "-outputs a list of valid clips\n\n")
    channel_name = input("channel name >> ").strip()
    date = input("date (YYYY-MM-DD UTC) >> ").strip()
    file = input("save output to file? [yes/no] >> ").strip()
    workers = input("worker count (empty for default) >> ").strip()
    if workers == "":
        workers = 150
    clips = get_clips_date(channel_name, date, file = file, workers = workers)

    if clips is not None:
        for clip in clips:
            print(clip.replace("\n", ""))
    return clips


if __name__ == "__main__":
    main()
