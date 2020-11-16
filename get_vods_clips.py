from datetime import datetime, timedelta
from math import floor


import clips_script
import get_clip_files
import get_stream_data
import vod_script


def get_vods_clips(channel_name, vod_clips, index, start, end):
    start_time = datetime.now().strftime("%m-%d-%Y, %H.%M.%S")
    stream_data = get_stream_data.get_data(channel_name, start, end)  # list of streams in format: (date_time, vod_id, minutes, title)
    streams = len(stream_data[index:])
    total_minutes = sum(map(lambda x: int(x[2]), stream_data[index:]))
    if vod_clips == "vods":
        print(f"\n{streams} streams found")
    elif vod_clips == "clips":
        print(f"\n{streams} streams found, {total_minutes} vod minutes \n"
              f"{timedelta(minutes = total_minutes * 0.0048)} estimated process time \n")

    for stream in stream_data[index:]:
        date_time = stream[0]
        vod_id = stream[1]
        minutes = stream[2]
        title = stream[3]
        if vod_clips == "vods":
            vod = vod_script.get_vod(channel_name, vod_id, date_time)
            data_string = f"DATE: {date_time}, URL: {vod} , ID: {vod_id}, " \
                          f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                          f"TITLE: {title} \n"
            with open(f".\\output\\batch\\{start_time} {channel_name} data vods.txt", "a", encoding = 'utf8') as data_log:
                data_log.write(data_string)

        elif vod_clips == "clips":
            clips = clips_script.get_clips(channel_name, vod_id, minutes)

            with open(f".\\output\\batch\\{start_time} {channel_name} data clips.txt", "a", encoding = 'utf8') as data_log:
                for clip in clips:
                    data_string = f"DATE: {date_time}, URL: {clip[0]} , TIME: {clip[1]} , ID: {vod_id}, " \
                                  f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                                  f"TITLE: {title} \n"
                    data_log.write(data_string)
                data_log.write("\n")

            minutes_left = sum(map(lambda x: int(x[2]), stream_data[stream_data.index(stream) + 1:]))
            log_string = f"{date_time}, {vod_id}, {title} DONE {stream_data.index(stream) + 1}/{len(stream_data)}  \n" \
                         f"{len(clips) if clips[0] != '' else 0} clips found \n"
            time_left_string = f"{floor(((total_minutes - minutes_left) / total_minutes) * 100)}% done " \
                               f"estimated time left: {timedelta(minutes = minutes_left * 0.0048)} \n \n"

            with open(f".\\output\\logs\\{start_time} {channel_name} Logs.txt", "a", encoding = 'utf8') as progress_log:
                progress_log.write(log_string + time_left_string)
            print(log_string, time_left_string)
        else:
            print("input not valid please try again")
        print("all links found")
        return f".\\output\\batch\\{start_time} {channel_name} data clips.txt"


def download_all_files(channel_name, file_location,vod_clips):
    print("starting download")
    if vod_clips == "clips":
        get_clip_files.get_clips(channel_name, file_location)
    else:

    print("download finished")


def main():
    channel_name = input("streamer name? >>").strip()
    vod_clips = input("clips or vods? >>").strip()
    index = int(input("start/continue from index? >>").strip())
    start = input("from date (earliest) YYYY-MM-DD >>").strip()
    end = input("to date (newest) YYYY-MM-DD >>").strip()
    download = input("download files yes or no? >>").strip()
    # workers = 150
    links = get_vods_clips(channel_name, vod_clips, index, start, end)
    if download == "yes":
        download_all_files(channel_name, links,vod_clips)


if __name__ == "__main__":
    main()
