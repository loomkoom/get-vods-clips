# encoding: utf-8
from pathlib import Path

import m3u8


def is_muted(url):
    playlist_url = m3u8.load(url)
    for uri in playlist_url.segments.uri:
        if uri.endswith("-unmuted.ts"):
            return True
    return False


def get_muted_playlist(url, file_name = None, file_path = Path("../output/files")):
    if file_name is None:
        file_name = Path(url.split("/")[-3])
    if not is_muted(url):
        return "stream has no muted parts"
    file_name = Path.with_suffix(file_name, ".m3u8")
    channel_name = url.split("_")[1]
    path = file_path / channel_name / "playlists"
    if not Path.is_dir(path):
        Path.mkdir(path, parents = True)

    playlist_url = m3u8.load(url)
    playlist_url.dump(path / file_name)
    full_url = url.split("/")
    url_path = "/".join(full_url[0:-1]) + "/"

    with open(path / file_name, 'r+', encoding = 'utf8') as playlist:
        input_lines = playlist.readlines()
        output_lines = []
        new_lines = []
        for line in input_lines:
            output_line = new_line = line
            if line.rstrip().endswith('unmuted.ts'):
                output_line = url_path + line.rstrip().replace("unmuted", "muted") + "\n"
            elif line.rstrip().endswith(".ts"):
                new_line = output_line = url_path + line.rstrip() + "\n"
            new_lines.append(new_line)
            output_lines.append(output_line)
        playlist.truncate(0)
        playlist.seek(0)
        playlist.writelines(new_lines)
    muted_file = Path(f"{file_name.stem}-muted.m3u8")
    with open(path / muted_file, 'w', encoding = 'utf8') as playlist:
        playlist.writelines(output_lines)
    return muted_file.name, path


def main():
    print("\n-script will replace unmuted ts files with muted counterparts \n"
          "-input [playlist url](m3u8) [file_name]\n"
          "-outputs the playlist file as <file_name>-muted.m3u8 in /output/files/channel-name/playlists\n\n")
    url = input("url >> ").strip()
    file_name = Path(input("file name to call playlist >> ").strip())
    file, path = get_muted_playlist(url, file_name)
    print(f"playlist saved at '{path / file}'")


if __name__ == "__main__":
    main()
