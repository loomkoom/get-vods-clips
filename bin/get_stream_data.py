# encoding: utf-8
from datetime import datetime

import requests
from bs4 import BeautifulSoup as soup


def get_soup(url):
    headers = {
            'Accept'                   : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding'          : 'gzip, deflate, br',
            'Accept-Language'          : 'en-US,en;q=0.9,nl;q=0.8',
            'Dnt'                      : '1',
            'Sec-Gpc'                  : '1',
            'Upgrade-Insecure-Requests': '1',
            'referer'                  : f'{"/".join(url.split("/")[:-1])}',
            'User-Agent'               : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.323',
            }
    html = requests.get(url, headers = headers, allow_redirects = False).content
    return soup(html, "html.parser")


def get_data(channel_name, start = "", end = ""):
    if len(channel_name) < 4 \
            or (start != "" and len(start) != 10) \
            or (end != "" and len(end) != 10):
        print("\ninvalid input data, check that date is in the correct format (YYYY-MM-DD)")
        return

    try:
        start_date = datetime.fromisoformat(start).date()
    except ValueError:
        start_date = ""
    try:
        end_date = datetime.fromisoformat(end).date()
    except ValueError:
        end_date = ""

    stream_data = list()
    url = f"https://twitchtracker.com/{channel_name}/streams"
    page_soup = get_soup(url)

    has_streams = page_soup.find("table", id = "streams")
    if has_streams:
        streams = page_soup.find("table", id = "streams").tbody.findAll("tr")
        for tr in streams:
            for td in tr.findAll("td"):
                if td.get("data-order") and td.get("nowrap") == "":
                    date_time = (td.get("data-order"),)
                    broadcast_id = (td.get("data-stream"),)
                if td.get("data-order") and not td.get("class"):
                    minutes = (td.get("data-order"),)
                if td.get("class") and "status" in td.get("class"):
                    if td.string:
                        title = (td.string.strip(),)
                    else:
                        title = ("",)
                if td.get("class") and "games" in td.get("class"):
                    categories = ()
                    for img in td.findAll("img"):
                        if img.get("title"):
                            categories += (img.get("title").strip(),)

            data = date_time + broadcast_id + minutes + title + categories
            current_date = datetime.fromisoformat(date_time[0]).date()
            if start != "":
                if start_date <= current_date:
                    stream_data.append(data)
            elif end != "":
                if current_date <= end_date:
                    stream_data.append(data)
                else:
                    break
            else:
                stream_data.append(data)
    else:
        print(f"{channel_name} has no recorded stream history")
    return stream_data


def main():
    print("\n-gets stream data between specific time period \n"
          "-Leave start and end empty to get all-time \n"
          "-returns a list with streams as (timestamp, broadcast id, length (in minutes),title\n\n")
    channel_name = input("streamer name? >> ").strip()
    start = input("from date (earliest) YYYY-MM-DD UTC >> ").strip()
    end = input("to date (newest) YYYY-MM-DD UTC >> ").strip()
    data = get_data(channel_name, start, end)

    if data is not None:
        for stream in data:
            print(stream)


if __name__ == "__main__":
    main()
