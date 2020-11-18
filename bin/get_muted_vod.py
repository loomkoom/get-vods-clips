import m3u8


def get_muted_playlist(url, file_name):
    file_name = file_name[:-5] if file_name.endswith(".m3u8") else file_name
    path = "../output/files/playlists"
    playlist_url = m3u8.load(url)
    playlist_url.dump(f"{path}/{file_name}.m3u8")
    full_url = url.split("/")
    url_path = "/".join(full_url[0:-1]) + "/"

    with open(f"{path}/{file_name}.m3u8", 'r+', encoding = 'utf8') as playlist:
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
        playlist.truncate(0), playlist.seek(0)
        playlist.writelines(new_lines)
    with open(f"{path}/{file_name}-muted.m3u8", 'w', encoding = 'utf8') as playlist:
        playlist.writelines(output_lines)
    return f"{file_name}-muted.m3u8"


def main():
    print("\n-script will replace unmuted ts files with muted counterparts \n"
          "-input [playlist url](m3u8) [file_name]\n"
          "-outputs the playlist file as <file_name>-muted.m3u8 in /output/files/playlists\n")
    url = input("url >>").strip()
    file_name = input("file name to call playlist >>").strip()
    get_muted_playlist(url, file_name)


if __name__ == "__main__":
    main()
