from datetime import datetime

import requests
from bs4 import BeautifulSoup as soup


def souper(url):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            }
    html = requests.get(url, headers = headers).content
    return soup(html, "html.parser")


def get_data(streamername, start, end):
    data = list()
    start_date = datetime.fromisoformat(start).date()
    end_date = datetime.fromisoformat(end).date()
    url = f"https://twitchtracker.com/{streamername}/streams"
    page_soup = souper(url)
    for tr in page_soup.find("table", id = "streams").tbody.findAll("tr"):
        stream = ()
        for td in tr.findAll("td"):
            if td.get("data-order"):
                if td.get("nowrap") == "":
                    date_time = td.get("data-order")
                    vod_id = td.get("data-stream")
                    stream = (date_time, vod_id)
                    # print(f"date: {date}, vod id: {vod_id}")
                elif not td.get("class"):
                    minutes = (td.get("data-order"),)
                    stream += minutes
                    # print(f"minutes: {minutes}")
            if td.get("class") and "status" in td.get("class"):
                title = (td.string,)
                stream += title
                # print(f"title: {title}")
        current_date = datetime.fromisoformat(date_time).date()
        if current_date >= start_date and current_date <= end_date:
            data.append(stream)
        # print(stream)
        # print("--------------------------------------------------------")
    return data


def main():
    streamername = input("streamername >>")
    start = input("from date (earliest) YYYY-MM-DD >>")
    end = input("to date (newest) YYYY-MM-DD >>")
    return get_data(streamername, start, end)


if __name__ == "__main__":
    print(main())
