from datetime import datetime, timedelta
from math import floor

import get_clips
import get_files
import get_stream_data
import get_vod


def get_vods_clips(channel_name, vods_clips, start, end, download, rename, workers = 150, test = "yes",
                   datapath = "../output/data", filepath = "../output/files", logpath = "../output/logs"):
    start_time = datetime.utcnow().strftime("%m-%d-%Y, %H.%M.%S")
    stream_data = get_stream_data.get_data(channel_name, start,
                                           end)  # list of streams in format: (date_time, broadcast_id, minutes, categories)
    streams = len(stream_data)
    file_name = f"{channel_name} {vods_clips} {start} - {end}.txt"
    total_minutes = sum(map(lambda x: int(x[2]), stream_data))
    time_now = datetime.utcnow().time().strftime("%H:%M:%S")
    if vods_clips == "vods":
        print(f"\n[{time_now}]: {streams} streams found \n"
              f"processing ... ")
    elif vods_clips == "clips":
        print(f"\n[{time_now}]: {streams} streams found, {total_minutes} vod minutes \n"
              f"[{time_now}]: {timedelta(minutes = total_minutes * 0.0043)} estimated process time \n")

    for stream in stream_data:
        date_time = stream[0]
        broadcast_id = stream[1]
        minutes = stream[2]
        title = stream[3]
        categories = stream[4]
        if vods_clips == "vods":
            vod = get_vod.get_vod(channel_name, broadcast_id, date_time, test)
            data_string = f"DATE: {date_time}, URL: {vod[0]} , MUTED: {vod[1] if vod[1] else 0} , ID: {broadcast_id}, " \
                          f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                          f"TITLE: {title} , CATEGORIES: {categories} \n"
            time_now = datetime.utcnow().time().strftime("%H:%M:%S")
            log_string = f"[{time_now}]: {date_time}, {broadcast_id}, {title} \n" \
                         f"streams checked {stream_data.index(stream) + 1}/{len(stream_data)}  \n"
            with open(f"{datapath}/{file_name}", "a", encoding = 'utf8') as data_log:
                data_log.write(data_string)
            if vod[0] != "no valid link":
                print(log_string)

        elif vods_clips == "clips":
            clips = get_clips.get_clips(broadcast_id, minutes, workers)

            with open(f"{datapath}/{file_name}", "a", encoding = 'utf8') as data_log:
                for clip in clips:
                    data_string = f"DATE: {date_time}, URL: {clip[0]} , TIME: {clip[1]} , ID: {broadcast_id}, " \
                                  f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                                  f"TITLE: {title} , CATEGORIES: {categories} \n"
                    data_log.write(data_string)

            minutes_left = sum(map(lambda x: int(x[2]), stream_data[stream_data.index(stream) + 1:]))
            time_now = datetime.utcnow().time().strftime("%H:%M:%S")
            log_string = f"[{time_now}]: {date_time}, {broadcast_id}, {title} \n" \
                         f"streams checked {stream_data.index(stream) + 1}/{len(stream_data)}  \n" \
                         f"[{time_now}]: {len(clips) if clips[0] != '' else 0} clips found \n"
            time_left_string = f"{floor(((total_minutes - minutes_left) / total_minutes) * 100)}% done " \
                               f"estimated time left: {timedelta(minutes = minutes_left * 0.0043)}\n"

            with open(f"{logpath}/{start_time} {channel_name} Logs.txt", "a", encoding = 'utf8') as progress_log:
                progress_log.write(log_string + time_left_string)
            print(log_string + time_left_string)

        else:
            print("input not valid please try again")
    print("\nAll retrievable links found")

    if download == "yes":
        print("starting download")
        get_files.get_files(file_name, rename, datapath = datapath, filepath = filepath)
        print("download finished")
    return file_name


def main():
    print("\n-gets all clips or vod links within time period \n"
          "-input [channel name] [vods or clips] [start date] [end date] [download] \n"
          "-outputs to a file in output/data\n"
          "-for downloads outputs in output/downloads (ffmpeg needed for vod downloads\n"
          "-worker count is set to 150 by default try changing it to a lower number"
          " if the script uses too much resources otherwise leave empty \n"
          "-disable testing vod playback with mpv if you get mpv errors\n\n")

    channel_name = input("channel name? >>").strip().lower()
    vods_clips = input("clips or vods? >>").strip().lower()
    start = input("from date (earliest) YYYY-MM-DD >>").strip()
    end = input("to date (newest) YYYY-MM-DD >>").strip()
    download = input("download files yes/no? >>").strip()
    if download == "yes":
        rename = input("rename files after download?\n"
                       "     (clips from {ID-offset}.mp4  --->  {date}__{title}__{offset_time}-{length}_{ID-offset}.mp4\n"
                       "     (vods  from {ID}.mp4  --->  {date}_{title}_{length}_{file}_{muted}.mp4\n[yes/no]?  >>")
    else:
        rename = "no"
    if vods_clips == "clips":
        workers = input("worker count (empty for default) >>").strip()
        if workers == "":
            workers = 150
        file_name = get_vods_clips(channel_name, vods_clips, start, end, download, rename, workers = workers)
        print(f"clip links located in '/output/data/{file_name}'\n")
    if vods_clips == "vods":
        test = input("test if vod actually plays with mpv (no false positives but a bit slower) [yes/no]? >>").strip()
        file_name = get_vods_clips(channel_name, vods_clips, start, end, download, rename, test = test)
        print(f"vod links located in '/output/data/{file_name}'\n")
    if download == "yes":
        print(f"files downloaded at '/output/files/{channel_name}/'\n")


if __name__ == "__main__":
    main()
