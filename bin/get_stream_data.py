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
                broadcast_id = (td.get("data-stream"),)
            if td.get("data-order") and not td.get("class"):
                minutes = (td.get("data-order"),)
            if td.get("class") and "status" in td.get("class"):
                title = (td.string,)
            if td.get("class") and "games" in td.get("class"):
                categories = ()
                for img in td.findAll("img"):
                    categories += (img.get("title"),)

        current_date = datetime.fromisoformat(date_time).date()
        if start_date <= current_date <= end_date:
            data = (date_time,) + broadcast_id + minutes + title + categories
            stream_data.append(data)
        elif current_date > end_date:
            break
    return stream_data


def main():
    print("\n-gets stream data between specific time period \n"
          "-returns a list with streams as (timestamp, broadcast id, length (in minutes),title\n\n")
    channel_name = input("streamer name? >>").strip()
    start = input("from date (earliest) YYYY-MM-DD UTC >>").strip()
    end = input("to date (newest) YYYY-MM-DD UTC >>").strip()
    print(get_data(channel_name, start, end))


if __name__ == "__main__":
    main()
