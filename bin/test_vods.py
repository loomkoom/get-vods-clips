import time

import vlc


def play_url(url):
    instance = vlc.Instance()
    instance.log_unset()

    player = instance.media_player_new()
    player.set_mrl(f"{url}")
    player.audio_set_mute(True)
    player.play()
    start = time.time()
    timeout = 5
    while not player.get_state() == vlc.State.Ended and time.time() - start < timeout:
        time.sleep(0.1)
    if int(player.is_playing()):
        player.pause()
        player.stop()
    return player.get_state() == vlc.State.Stopped


def test_vods(file_location,file_name):
    with open(file_location, "r", encoding = 'utf8') as file:
        output = list()
        streams = list(filter((lambda x: "vod-secure.twitch.tv" in x), file.readlines()))
        for stream in streams:
            data = stream.split(',')
            url = data[1].strip()[5:]
            played = play_url(url)
            if played:
                output.append(stream)

    with open(f"../{file_location}/{file_name}.txt", "w", encoding = 'utf8') as file:
        file.writelines(output)


def main():
    print("tests all vod links in file \n"
          "input [file location] (from project directory) and [file name]  \n")

    channel_name = input("streamer name? >>").strip()
    file_location = input("file location? (//file path) >>").strip()
    file_name = input("file name?  >>").strip()
    test_vods(file_location,file_name)


if __name__ == "__main__":
    main()
