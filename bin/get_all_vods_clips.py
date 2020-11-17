from datetime import datetime, timedelta
from math import floor

import get_clips
import get_files
import get_stream_data
import get_vod


def get_vods_clips(channel_name, vod_clips, start, end):
    start_time = datetime.now().strftime("%m-%d-%Y, %H.%M.%S")
    stream_data = get_stream_data.get_data(channel_name, start, end)  # list of streams in format: (date_time, vod_id, minutes, title)
    streams = len(stream_data)
    total_minutes = sum(map(lambda x: int(x[2]), stream_data))
    if vod_clips == "vods":
        print(f"\n{streams} streams found \n"
              f"processing ... ")
    elif vod_clips == "clips":
        print(f"\n{streams} streams found, {total_minutes} vod minutes \n"
              f"{timedelta(minutes = total_minutes * 0.0048)} estimated process time \n")

    for stream in stream_data:
        date_time = stream[0]
        vod_id = stream[1]
        minutes = stream[2]
        title = stream[3]
        if vod_clips == "vods":
            vod = get_vod.get_vod(channel_name, vod_id, date_time)
            data_string = f"found DATE: {date_time}, URL: {vod[0]} , MUTED: {vod[1] if not None else 'No'} ID: {vod_id}, " \
                          f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                          f"TITLE: {title} \n"
            log_string = f"{date_time}, {vod_id}, {title} \nCHECKED {stream_data.index(stream) + 1}/{len(stream_data)}  \n"
            with open(f"../output/data/{channel_name} vods {start} - {end}.txt", "a", encoding = 'utf8') as data_log:
                data_log.write(data_string)
            if vod[0] != "no valid link":
                print(log_string)

        elif vod_clips == "clips":
            clips = get_clips.get_clips(channel_name, vod_id, minutes)

            with open(f"../output/data/{channel_name} clips {start} - {end}.txt", "a", encoding = 'utf8') as data_log:
                for clip in clips:
                    data_string = f"DATE: {date_time}, URL: {clip[0]} , TIME: {clip[1]} , ID: {vod_id}, " \
                                  f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                                  f"TITLE: {title} \n"
                    data_log.write(data_string)
                data_log.write("\n")

            minutes_left = sum(map(lambda x: int(x[2]), stream_data[stream_data.index(stream) + 1:]))
            log_string = f"{date_time}, {vod_id}, {title} CHECKED {stream_data.index(stream) + 1}/{len(stream_data)}  \n" \
                         f"{len(clips) if clips[0] != '' else 0} clips found \n"
            time_left_string = f"{floor(((total_minutes - minutes_left) / total_minutes) * 100)}% done " \
                               f"estimated time left: {timedelta(minutes = minutes_left * 0.0048)} \n \n"

            with open(f"../output/logs/{start_time} {channel_name} Logs.txt", "a", encoding = 'utf8') as progress_log:
                progress_log.write(log_string + time_left_string)
            print(log_string, time_left_string)
        else:
            print("input not valid please try again")
    print("\nFinished")
    if vod_clips == "clips":
        return f"clip links located in /output/data/{channel_name} clips {start} - {end}.txt"
    return f"vod links located in /output/data/{channel_name} vods {start} - {end}.txt"


def main():
    print("gets all clips or vod links within time period \n"
          "input [channel name] [vods or clips] [start date] [end date] [download] \n"
          "outputs to a file in output/data\n")
    channel_name = input("streamer name? >>").strip()
    vod_clips = input("clips or vods? >>").strip()
    start = input("from date (earliest) YYYY-MM-DD >>").strip()
    end = input("to date (newest) YYYY-MM-DD >>").strip()
    # download = input("download files yes/no? >>").strip()
    # workers = 150
    print(get_vods_clips(channel_name, vod_clips, start, end))
    # if download == "yes":
    #     print("starting download")
    #     get_files.get_clips(channel_name, links, vod_clips)
    #     print("download finished")


if __name__ == "__main__":
    main()
