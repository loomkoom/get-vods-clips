import get_stream_data
import vod_script
import clips_script
import getfiles
from datetime import datetime, timedelta
from math import floor


def get_vods_clips(streamername, vod_clips, start, output_file = "separate"):
    start_time = datetime.now().strftime("%m-%d-%Y, %H.%M.%S")
    stream_data = get_stream_data.get_data(streamername)  # list of streams in format: (date_time, vod_id, minutes, title)
    streams = len(stream_data[start:])
    total_minutes = sum(map(lambda x: int(x[2]), stream_data[start:]))
    if vod_clips == "vods":
        print(f"{streams} streams found")
    elif vod_clips == "clips":
        print(f"{streams} streams found, {total_minutes} vod minutes \n"
              f" {timedelta(minutes = total_minutes * 0.0048)} estimated process time")

    for stream in stream_data[start:]:
        date_time = stream[0]
        vod_id = stream[1]
        minutes = stream[2]
        title = stream[3]
        if vod_clips == "vods":
            if output_file == "local":
                vod = vod_script.get_vod(streamername, vod_id, date_time, output = output_file)
                data_string = f"{vod} ID: {vod_id}, " \
                              f"DATE: {date_time}, LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                              f"TITLE: {title} \n"
                with open(f".\output\\batch\{streamername} data vods {start_time}.txt", "a", encoding = 'utf8') as data_log:
                    data_log.write(data_string)
            else:
                vod_script.get_vod(streamername, vod_id, date_time, title)

        elif vod_clips == "clips":
            if output_file == "local":
                clips = clips_script.get_clips(streamername, vod_id, minutes, output = output_file)

                with open(f".\output\\batch\{streamername} data clips {start_time}.txt", "a", encoding = 'utf8') as data_log:
                    for clip in clips:
                        data_string = f"{clip[0]} TIME: {clip[1]} ID: {vod_id}, " \
                                      f"DATE: {date_time}, LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                                      f"TITLE: {title} \n"
                        data_log.write(data_string)
                    data_log.write("\n")
            else:
                clips = clips_script.get_clips(streamername, vod_id, minutes, title)

            minutes_left = sum(map(lambda x: int(x[2]), stream_data[stream_data.index(stream) + 1:]))
            log_string = f"{date_time}, {vod_id}, {title} DONE {stream_data.index(stream) + 1}/{len(stream_data)}  \n " \
                         f"{len(clips)} clips found \n "
            time_left_string = f"{floor(((total_minutes - minutes_left) / total_minutes) * 100)}% done " \
                               f"estimated time left: {timedelta(minutes = minutes_left * 0.0048)} \n \n"

            with open(f".\output\logs\{streamername} Logs {start_time}.txt", "a", encoding = 'utf8') as progress_log:
                progress_log.write(log_string + time_left_string)
            print(log_string, time_left_string)
        else:
            print("input not valid please try again")


def open_all_files(streamername, vod_clips):
    stream_data = get_stream_data.get_data(streamername)
    vod_ids = map(lambda x: x[1], stream_data)
    getfiles.open_files(streamername, vod_clips, vod_ids)


def main():
    streamername = input("streamer name? >>")
    vod_clips = input("clips or vods? >>")
    start = int(input("start/continue from index? >>"))
    # workers = 150
    # TO DO date from til
    get_vods_clips(streamername, vod_clips, start, output_file = "local")


if __name__ == "__main__":
    main()
