from time import sleep

import vlc


def play_url(url):
    played = False
    player = vlc.MediaPlayer()
    player.set_mrl(f"{url}")
    player.play()
    player.audio_set_mute(True)
    sleep(2.5)
    if player.is_playing() == 1:
        played = True
    player.stop()
    return played


def test_vods(streamername, filelocation):
    with open(filelocation, "r", encoding = 'utf8') as file:
        output = list()
        badlinks = list()
        streams = list(filter((lambda x: "vod-secure.twitch.tv" in x), file.readlines()))
        for stream in streams:
            data = stream.split(',')
            url = data[1].strip()
            played = play_url(url)
            if played:
                output.append(stream)
            else:
                badlinks.append(stream)
            print(f"{streams.index(stream)}/{len(streams)}", played, url)

    with open(f".\output\\batch\\{streamername} valid vods.txt", "w", encoding = 'utf8') as file:
        file.writelines(output)
    with open(f".\output\\batch\\{streamername} invalid vods.txt", "w", encoding = 'utf8') as file:
        file.writelines(badlinks)


def main():
    streamername = input("streamer name? >>")
    filelocation = input("file location? >>")
    test_vods(streamername, filelocation)


if __name__ == "__main__":
    main()
