import m3u8


def get_muted_playlist(url, filename):
    playlist_url = m3u8.load(url)
    playlist_url.dump(f"..\\output\\playlists\\{filename}.m3u8")
    full_url = url.split("/")
    url_path = "/".join(full_url[0:-1]) + "/"

    with open(f"..\\output\\playlists\\{filename}.m3u8", 'r+') as playlist:
        input_lines = playlist.readlines()
        output_lines = []
        for line in input_lines:
            if line.rstrip().endswith('unmuted.ts'):
                line = url_path + line.rstrip().replace("unmuted", "muted") + "\n"
            elif line.rstrip().endswith('.ts'):
                line = url_path + line.rstrip() + "\n"
            output_lines.append(line)
    with open(f"..\\output\\playlists\\{filename}-muted.m3u8", 'w') as playlist:
        playlist.writelines(output_lines)


def main():
    print("script will replace unmuted ts files with muted counterparts \n"
          "input [playlist url](m3u8) [filename]"
          "outputs the playlist file as <filename>-muted.m3u8 in \\output\\playlists")
    url = input("url >>").strip()
    filename = input("filename to call playlist >>").strip()
    get_muted_playlist(url, filename)


if __name__ == "__main__":
    main()
