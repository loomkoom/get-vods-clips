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


def test_vods(channel_name, file_location):
    with open(file_location, "r", encoding = 'utf8') as file:
        output = list()
        streams = list(filter((lambda x: "vod-secure.twitch.tv" in x), file.readlines()))
        for stream in streams:
            data = stream.split(',')
            url = data[1].strip()[5:]
            played = play_url(url)
            print(url)
            if played:
                output.append(stream)
            print(played, url)

    with open(f".\\output\\batch\\{channel_name} valid vods.txt", "w", encoding = 'utf8') as file:
        file.writelines(output)


def main():
    channel_name = input("streamer name? >>").strip()
    file_location = input("file location? >>").strip()
    test_vods(channel_name, file_location)


if __name__ == "__main__":
    main()
