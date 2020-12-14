# encoding: utf-8
import get_clips
import get_stream_data


def get_clips_date(channel_name, date, tracker = "SC", file = "no", workers = 150, data_path = "../output/data"):
    file_name = f"{channel_name}_clips_{date}.txt"
    clips_lst = []
    stream_data = get_stream_data.get_data(channel_name, date, date, tracker = tracker)
    for stream in stream_data:
        date_time = stream[0]
        broadcast_id = stream[1]
        minutes = stream[2]
        title = stream[3]
        clips = get_clips.get_clips(broadcast_id, minutes, workers)

        for clip in clips:
            data_string = f"DATE: {date_time}, URL: {clip[0]} , TIME: {clip[1]} , ID: {broadcast_id}, " \
                          f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                          f"TITLE: {title} \n"
            clips_lst.append(data_string)
        if file == "yes":
            with open(f"{data_path}/{file_name}", "w", encoding = 'utf8') as data_log:
                data_log.writelines(clips_lst)
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
    clips = get_clips_date(channel_name, date, file, workers)

    for clip in clips:
        print(clip.replace("\n", ""))


if __name__ == "__main__":
    main()
