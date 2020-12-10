#encoding: utf-8
import get_stream_data
import get_vod


def get_vods(channel_name, date, test):
    vods = []
    stream_data = get_stream_data.get_data(channel_name, date, date)
    for stream in stream_data:
        date_time = stream[0]
        broadcast_id = stream[1]
        minutes = stream[2]
        title = stream[3]
        vod = get_vod.get_vod(channel_name, broadcast_id, date_time, test)
        data_string = f"DATE: {date_time}, URL: {vod[0]} , MUTED: {vod[1] if vod[1] else 0} , ID: {broadcast_id}, " \
                      f"LENGTH: {int(minutes) // 60}h{(int(minutes) - (int(minutes) // 60) * 60)}min, " \
                      f"TITLE: {title} \n"
        vods.append(data_string)
    return vods


def main():
    print("\n-returns the playlist links for all vods on a specific date usually available for any vod within 60 days \n"
          "-requires [channel name] and [date] \n"
          "-output a list wth vod link and data "
          "-disable testing vod playback with mpv if you get mpv errors\n\n")
    channel_name = input("Enter streamer name >> ").strip()
    date = input("date (YYYY-MM-DD UTC) >> ").strip()
    test = input("enable testing vod playback with mpv to make sure link works yes/no? >> ").strip()
    print(get_vods(channel_name, date, test))


if __name__ == "__main__":
    main()
