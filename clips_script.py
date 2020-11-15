import requests
import concurrent.futures
import time
from datetime import timedelta
import winsound
from ratelimit import limits, sleep_and_retry


# @sleep_and_retry
# @limits(calls =, period =)
def load_url(url, session):
    r = session.head(url, allow_redirects = False)
    return r.ok


def get_clips(streamername, vod_id, time_offset = "",workers = 150, output = "separate", title = "title"):
    if time_offset == '':
        time_offset = 99999  # 28hrs
    elif "h" in time_offset:
        hrs_min = time_offset.split('h')
        time_offset = int(hrs_min[0]) * 3600 + (int(hrs_min[1]) + 1) * 60 + 24
    else:
        time_offset = (int(time_offset) + 1) * 60 + 24
    urls = {f"https://clips-media-assets2.twitch.tv/{vod_id}-offset-{str(offset)}.mp4": offset for offset in range(0, time_offset)}
    output = list()
    i = 0

    start = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers = workers) as executor:
        with requests.session() as session:
            future_to_url = {executor.submit(load_url, url, session = session): url for url in urls.keys()}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                if future.result():
                    offset = urls[url] - 24
                    hr = offset // 3600
                    min = (offset % 3600) // 60
                    sec = (offset % 60)
                    offset_time = f"{hr}:{min}:{sec}"
                    output.append((url, offset_time))
                    # print(f"Completed link {i} at: {offset_time} result: {url} \r")
                i += 1
                # hr = (time_offset - i) // 3600
                # min = ((time_offset - i) % 3600) // 60
                # sec = (time_offset - i) % 60
                # print(f"{hr} hrs {min} min {sec} sec left in vod")

            runtime = time.time() - start
            # print(f"took {timedelta(seconds = runtime)} seconds or {100 / runtime} links per second")
    if len(output) > 0:
        # print(f"{len(output)} clips found {streamername} vod id: {vod_id}\n")
        if output == "separate":
            with open(f".\output\separate\{streamername} clips-{vod_id}.txt", "w") as clips:
                for url in output:
                    clips.write(url[0] + url[1] + '\n')
        return output
    else:
        # print(f"no valid clips found {streamername} vod id: {vod_id}\n")
        return [("no valid clips found,","None")]


def main():
    streamername = input("streamer name >> ")
    vod_id = input("vod id >> ")
    time_offset = input('vod length if known in [hrs]h[min] or minutes >> ')
    get_clips(streamername, vod_id, time_offset)
    winsound.PlaySound("empty", winsound.MB_OK)


if __name__ == "__main__":
    main()
