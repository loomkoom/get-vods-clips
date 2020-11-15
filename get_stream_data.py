from bs4 import BeautifulSoup as soup
import requests


def souper(url):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            }
    html = requests.get(url, headers = headers).content
    return soup(html, "html.parser")


def get_data(streamername):
    data = list()
    url = f"https://twitchtracker.com/{streamername}/streams"
    page_soup = souper(url)
    for tr in page_soup.find("table", id = "streams").tbody.findAll("tr"):
        stream = ()
        for td in tr.findAll("td"):
            if td.get("data-order"):
                if td.get("nowrap") == "":
                    date = td.get("data-order")
                    vod_id = td.get("data-stream")
                    stream = (date, vod_id)
                    # print(f"date: {date}, vod id: {vod_id}")
                elif not td.get("class"):
                    minutes = (td.get("data-order"),)
                    stream += minutes
                    # print(f"minutes: {minutes}")
            if td.get("class") and "status" in td.get("class"):
                title = (td.string,)
                stream += title
                # print(f"title: {title}")
        data.append(stream)
        # print(stream)
        # print("--------------------------------------------------------")
    return data


def main():
    streamername = input("streamername >>")
    # date from til ...
    return get_data(streamername)


if __name__ == "__main__":
    main()
