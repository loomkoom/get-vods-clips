import time
from datetime import timedelta

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


def test_vods(file_name,new_file_name):
    with open(f"../output/data/{file_name}.txt", "r", encoding = 'utf8') as file:
        output = list()
        streams = list(filter((lambda x: "vod-secure.twitch.tv" in x), file.readlines()))
        print(f"estimated run time: {timedelta(seconds=5*len(streams))}")
        for stream in streams:
            data = stream.split(',')
            url = data[1].strip()[5:]
            played = play_url(url)
            if played:
                output.append(stream)

    with open(f"../output/data/{new_file_name}.txt", "w", encoding = 'utf8') as file:
        file.writelines(output)



def main():
    print("\n-tests all vod links in file using vlc \n"
          "-input [input file name] and [output file name] only for files in /output/data/\n")

    input_file = input("input file name?  >>").strip()
    output_file = input("output file name?  >>").strip()
    test_vods(input_file,output_file)


if __name__ == "__main__":
    main()
