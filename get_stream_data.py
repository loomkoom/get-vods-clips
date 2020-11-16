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
        stream = ()
        for td in tr.findAll("td"):
            if td.get("data-order") and td.get("nowrap") == "":
                date_time = td.get("data-order")
                vod_id = td.get("data-stream")
                stream = (date_time, vod_id)
            if td.get("data-order") and not td.get("class"):
                minutes = (td.get("data-order"),)
                stream += minutes
            if td.get("class") and "status" in td.get("class"):
                title = (td.string,)
                stream += title

        current_date = datetime.fromisoformat(date_time).date()
        if start_date <= current_date <= end_date:
            stream_data.append(stream)
        elif current_date > end_date:
            break
    return stream_data


def main():
    channel_name = input("streamer name? >>")
    start = input("from date (earliest) YYYY-MM-DD UTC >>")
    end = input("to date (newest) YYYY-MM-DD UTC >>")
    print(get_data(channel_name, start, end))


if __name__ == "__main__":
    main()
