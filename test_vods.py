from time import sleep

import vlc


def play_url(url):
    played = False
    instance = vlc.Instance()
    instance.log_unset()

    player = instance.media_player_new()
    player.set_mrl(f"{url}")
    player.audio_set_mute(True)
    player.play()
    sleep(3)

    if player.is_playing() == 1:
        played = True
    player.stop()
    return played


def test_vods(channel_name, file_location):
    with open(file_location, "r", encoding = 'utf8') as file:
        output = list()
        streams = list(filter((lambda x: "vod-secure.twitch.tv" in x), file.readlines()))
        for stream in streams:
            data = stream.split(',')
            url = data[1].strip()
            played = play_url(url)
            if played:
                output.append(stream)
            print(played,url)

    with open(f".\\output\\batch\\{channel_name} valid vods.txt", "w", encoding = 'utf8') as file:
        file.writelines(output)


def main():
    channel_name = input("streamer name? >>").strip()
    file_location = input("file location? >>").strip()
    test_vods(channel_name, file_location)


if __name__ == "__main__":
    main()
