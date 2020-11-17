import concurrent.futures
import winsound

import requests


# @sleep_and_retry
# @limits(calls =, period =)
def load_url(url, session):
    r = session.head(url, allow_redirects = False)
    return r.ok


def get_clips(vod_id, time_offset, workers = 150):
    time_offset = (int(time_offset) + 5) * 60 + 24
    urls = {f"https://clips-media-assets2.twitch.tv/{vod_id}-offset-{str(offset)}.mp4": offset for offset in range(0, time_offset)}
    output = list()

    with concurrent.futures.ThreadPoolExecutor(max_workers = workers) as executor:
        with requests.session() as session:
            future_to_url = {executor.submit(load_url, url, session = session): url for url in urls.keys()}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                if future.result():
                    offset_time = urls[url] - 24
                    hr = offset_time // 3600
                    mins = (offset_time % 3600) // 60
                    sec = (offset_time % 60)
                    offset_time = f"{hr}:{mins}:{sec}"
                    output.append((url, offset_time))

    if len(output) > 0:
        return output
    else:
        return [("no valid clips found,", "None")]


def main():
    print("gets all clips from a vod, you can round up vod length as it is just the upper border to search for clips \n"
          "input [vod id] [vod length](minutes) \n"
          "outputs a list of valid clips with each clip as (url,offset time)")
    vod_id = input("vod id >> ").strip()
    time_offset = input('vod length in minutes >> ').strip()
    print(get_clips(vod_id, time_offset))
    winsound.PlaySound("empty", winsound.MB_OK)


if __name__ == "__main__":
    main()
