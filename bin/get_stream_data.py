from datetime import datetime

import requests
from bs4 import BeautifulSoup as soup


def get_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36', }
    html = requests.get(url, headers = headers).content
    return soup(html, "html.parser")


def get_data(channel_name, start, end):
    stream_data = list()
    start_date = datetime.fromisoformat(start).date()
    end_date = datetime.fromisoformat(end).date()
    url = f"https://twitchtracker.com/{channel_name}/streams"
    page_soup = get_soup(url)

    for tr in page_soup.find("table", id = "streams").tbody.findAll("tr"):
        for td in tr.findAll("td"):
            if td.get("data-order") and td.get("nowrap") == "":
                date_time = td.get("data-order")
                vod_id = (td.get("data-stream"),)
            if td.get("data-order") and not td.get("class"):
                minutes = (td.get("data-order"),)
            if td.get("class") and "status" in td.get("class"):
                title = (td.string,)

        current_date = datetime.fromisoformat(date_time).date()
        if start_date <= current_date <= end_date:
            data = (date_time,) + vod_id + minutes + title
            stream_data.append(data)
        elif current_date > end_date:
            break
    return stream_data


def main():
    print("gets stream data between specific time period \n"
          "returns a list with streams as (timestamp, vod id, length (in minutes),title")
    channel_name = input("streamer name? >>").strip()
    start = input("from date (earliest) YYYY-MM-DD UTC >>").strip()
    end = input("to date (newest) YYYY-MM-DD UTC >>").strip()
    print(get_data(channel_name, start, end))


if __name__ == "__main__":
    main()
