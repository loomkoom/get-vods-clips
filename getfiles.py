import webbrowser

def open_file(streamername,vod_clips,vod_id):
    with open(f".\output\{streamername} {vod_clips}-{vod_id}.txt", "r") as clips:
        if vod_clips == "clips":
            urls = clips.readlines()
            for url in urls:
                webbrowser.open(url)
        else:
            url = clips.read()
            webbrowser.open(url)

def open_files(streamername,vod_clips,vod_ids):
    for vod_id in vod_ids:
        with open(f".\output\separate\{streamername} {vod_clips}-{vod_id}.txt", "r") as clips:
            if vod_clips == "clips":
                urls = clips.readlines()
                for url in urls:
                    webbrowser.open(url)
            else:
                url = clips.read()
                webbrowser.open(url)

if __name__ == "__main__":
    streamername = input("streamername? >>")
    vod_id = input("vod id? >>")
    vod_clips = input("vod or clips? >>")
    open_file(streamername, vod_clips, vod_id)

