import get_clips
import get_stream_data


def get_clips_date(channel_name, date):
    clips_lst = []
    stream_data = get_stream_data.get_data(channel_name, date, date)
    for stream in stream_data:
        date_time = stream[0]
        broadcast_id = stream[1]
        minutes = stream[2]
        title = stream[3]
        clips = get_clips.get_clips(broadcast_id, minutes)
        for clip in clips:
            data_string = f"DATE: {date_time}, URL: {clip[0]} , TIME: {clip[1]} , ID: {broadcast_id}, " \
                          f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                          f"TITLE: {title} \n"
            clips_lst.append(data_string)
    return clips_lst


def main():
    print("\n-gets all clips from a specific date\n"
          "-input [channel name] and [date] \n"
          "-outputs a list of valid clips\n\n")
    channel_name = input("channel name >> ").strip()
    date = input("date (YYYY-MM-DD UTC) >>").strip()
    print(get_clips_date(channel_name, date))


if __name__ == "__main__":
    main()
