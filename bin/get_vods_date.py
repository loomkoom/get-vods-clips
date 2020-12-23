# encoding: utf-8
import logging

import get_stream_data
import get_vod

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def get_vods(channel_name, date, tracker = "TT", test = "yes", loglevel = "INFO"):
    if not isinstance(loglevel, int):
        loglevels = {"NOTSET": 0, "DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
        loglevel = loglevels[loglevel.upper()]
    logger.setLevel(loglevel)
    if (len(channel_name) < 4 or
            (not (date == "" or len(date) == 10)) or
            (not (test == "yes" or test == "no")) or
            (not (tracker == "TT" or tracker == "SC"))):
        logger.critical("\ninvalid input data, check that date is in the correct format (YYYY-MM-DD)")
        return

    vods = list()
    date = date.split(" ")[0]
    logger.info("fetching stream data")
    stream_data = get_stream_data.get_data(channel_name, date, date, tracker)
    if len(stream_data) == 0:
        logger.info(f"{tracker} found no stream for {channel_name} on {date}")
        return
    for stream in stream_data:
        logger.debug(stream)
        date_time, broadcast_id, minutes, title, categories = stream
        logger.info(f"fetching vod links for stream {stream_data.index(stream) + 1}")
        vod = get_vod.get_vod(channel_name, broadcast_id, date_time, tracker = tracker, test = test)
        data_string = f"DATE: {date_time}, URL: {vod[0]} , MUTED: {vod[1] if vod[1] else 0} , ID: {broadcast_id}, " \
                      f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                      f"TITLE: {title} , CATEGORIES: {categories}\n"
        vods.append(data_string)
    return vods


def main():
    print("\n-returns the playlist links for all vods on a specific date usually available for any vod within 60 days \n"
          "-requires [channel name] and [date] \n"
          "-output a list wth vod link and data\n"
          "-disable testing vod playback if it's slow and you don't mind false positives\n"
          "-choose twitchtracker or steamcharts as tracker\n"
          "     - streamcharts:\n"
          "         PRO: can get multiple vods when stream goes down\n"
          "         CON: slower data retrieval and slower vod finding\n"
          "     - twitchtracker:\n"
          "         PRO: fast\n"
          "         CON: will merge multiple streams (can only get 1st part of vod)\n\n")
    channel_name = input("Enter streamer name >> ").strip()
    date = input("date (YYYY-MM-DD UTC) >> ").strip()
    test = input("enable testing vod playback with mpv to make sure link works yes/no? >> ").strip()
    tracker = input("tracker to use [TT/SC]? >> ").strip().upper()
    vods = get_vods(channel_name, date, tracker, test)

    for tag in vods:
        print(tag)
    return vods


if __name__ == "__main__":
    print(main())
