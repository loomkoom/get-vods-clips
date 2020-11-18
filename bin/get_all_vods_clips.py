from datetime import datetime, timedelta
from math import floor

import get_clips
import get_files
import get_stream_data
import get_vod


def get_vods_clips(channel_name, vod_clips, start, end, workers = 150, test = "yes"):
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
            vod = get_vod.get_vod(channel_name, vod_id, date_time, test)
            data_string = f"DATE: {date_time}, URL: {vod[0]} , MUTED: {vod[1] if vod[1] else 0} , ID: {vod_id}, " \
                          f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                          f"TITLE: {title} \n"
            log_string = f"{date_time}, {vod_id}, {title} \nstreams checked {stream_data.index(stream) + 1}/{len(stream_data)}  \n"
            with open(f"../output/data/{channel_name} vods {start} - {end}.txt", "a", encoding = 'utf8') as data_log:
                data_log.write(data_string)
            if vod[0] != "no valid link":
                print(log_string)

        elif vod_clips == "clips":
            clips = get_clips.get_clips(vod_id, minutes, workers)

            with open(f"../output/data/{channel_name} clips {start} - {end}.txt", "a", encoding = 'utf8') as data_log:
                for clip in clips:
                    data_string = f"DATE: {date_time}, URL: {clip[0]} , TIME: {clip[1]} , ID: {vod_id}, " \
                                  f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                                  f"TITLE: {title} \n"
                    data_log.write(data_string)

            minutes_left = sum(map(lambda x: int(x[2]), stream_data[stream_data.index(stream) + 1:]))
            log_string = f"{date_time}, {vod_id}, {title} \nstreams checked {stream_data.index(stream) + 1}/{len(stream_data)}  \n" \
                         f"{len(clips) if clips[0] != '' else 0} clips found \n"
            time_left_string = f"{floor(((total_minutes - minutes_left) / total_minutes) * 100)}% done " \
                               f"estimated time left: {timedelta(minutes = minutes_left * 0.0048)}\n"

            with open(f"../output/logs/{start_time} {channel_name} Logs.txt", "a", encoding = 'utf8') as progress_log:
                progress_log.write(log_string + time_left_string)
            print(log_string + time_left_string)

        else:
            print("input not valid please try again")
    print("\nAll retrievable links found")
    if vod_clips == "clips":
        return f"{channel_name} clips {start} - {end}.txt"
    return f"{channel_name} vods {start} - {end}.txt"


def main():
    print("\n-gets all clips or vod links within time period \n"
          "-input [channel name] [vods or clips] [start date] [end date] [download] \n"
          "-outputs to a file in output/data\n"
          "-for downloads outputs in output/downloads (ffmpeg needed for vod downloads\n"
          "-worker count is set to 150 by default try changing it to a lower number"
          " if the script uses too much resources otherwise leave empty \n"
          "-disable testing vod playback with vlc if you get vlc errors other than those starting with [h264 @ 000001df3c9623e0] \n\n")

    channel_name = input("streamer name? >>").strip()
    vod_clips = input("clips or vods? >>").strip()
    start = input("from date (earliest) YYYY-MM-DD >>").strip()
    end = input("to date (newest) YYYY-MM-DD >>").strip()
    download = input("download files yes/no? >>").strip()
    if download == "yes":
        rename = input("rename files after download?\n"
                       "     (clips from {ID-offset}.mp4  --->  {date}__{title}__{offset_time}-{length}_{ID-offset}.mp4\n"
                       "     (vods  from {ID}.mp4  --->  {date}_{title}_{length}_{file}_{muted}.mp4\n[yes/no]?  >>")
    if vod_clips == "clips":
        workers = input("worker count (empty for default) >>").strip()
        if workers == "":
            workers = 150
        file_location = get_vods_clips(channel_name, vod_clips, start, end, workers = workers)
        print(f"clip links located in '/output/data/{file_location}'\n")
    if vod_clips == "vods":
        test = input("test if vod actually plays with vlc (more reliable but slower) [yes/no]? >>").strip()
        file_location = get_vods_clips(channel_name, vod_clips, start, end, test = test)
        print(f"vod links located in '/output/data/{file_location}'\n")
    if download == "yes":
        print("starting download")
        get_files.get_files(file_location, rename)
        print("download finished")


if __name__ == "__main__":
    main()
