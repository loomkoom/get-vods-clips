# encoding: utf-8
import logging
from datetime import datetime, timedelta
from math import ceil

import requests
from alt_twitch.twitch.helix.api import TwitchHelix
from bs4 import BeautifulSoup as soup

logger = logging.getLogger(__name__)
formatter = logging.Formatter('[%(asctime)s : %(name)s]: %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def get_page(url, format = "html", session = False):
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
    if session:
        resp = session.get(url, headers = headers, allow_redirects = False)
    else:
        resp = requests.get(url, headers = headers, allow_redirects = False)

    if format == "html":
        html = resp.content
        page = soup(html, "html.parser")
    elif format == "json":
        page = resp.json()
    return page


def parse_tags_TT(page, start, end):
    stream_data = list()
    streams = page.find("table", id = "streams").tbody.findAll("tr")
    for tr in streams:
        for td in tr.findAll("td"):
            if td.get("data-order") and td.get("nowrap") == "":
                date_time = (td.get("data-order"),)
                broadcast_id = (td.get("data-stream"),)
            if td.get("data-order") and not td.get("class"):
                minutes = (td.get("data-order"),)
            if td.get("class") and "status" in td.get("class"):
                if td.string:
                    title = (td.string.strip().replace(",", ";"),)
                else:
                    title = ("",)
            if td.get("class") and "games" in td.get("class"):
                categories = "("
                for img in td.findAll("img"):
                    if img.get("title"):
                        category = f'{img.get("title").strip()}; '
                        categories += category
                categories = categories[:-2]
                categories += ")"
        data = date_time + broadcast_id + minutes + title + (categories,)
        current_date = datetime.fromisoformat(date_time[0]).date()
        if start < current_date <= end:
            stream_data.append(data)
        if current_date > end:
            break
    return stream_data


def parse_tags_SC(streams_json, start, end):
    stream_data = list()
    for stream in streams_json["streams"]:
        date_time = stream["stream_created_at"][:-3]
        broadcast_id = stream["stream_id"]
        length = ceil((float(stream["air_time"]) + 0.1) * 60)
        title = stream["stream_status"]
        games = stream["games"]
        categories = str(tuple(game["slug"] for game in games)).replace(",", ";")
        data = (date_time, broadcast_id, length, title, categories)

        current_date = datetime.fromisoformat(date_time).date()
        if start < current_date <= end:
            stream_data.append(data)
    return stream_data


def get_data(channel_name, start = "", end = "", tracker = "TT"):
    if (len(channel_name) < 4 or
            (not (start == "" or len(start) == 10)) or
            (not (end == "" or len(end) == 10))):
        logger.critical("\ninvalid input data, check that date is in the correct format (YYYY-MM-DD)")
        return

    try:
        start = datetime.fromisoformat(start).date()
        start -= timedelta(days = 1)
    except ValueError:
        start = datetime.fromisoformat("2000-01-01").date()
    try:
        end = datetime.fromisoformat(end).date()
    except ValueError:
        end = datetime.today().date()

    stream_data = None
    if tracker == "TT":
        url = f"https://twitchtracker.com/{channel_name}/streams"
        page = get_page(url, "html")
        has_streams = page.find("table", id = "streams")
        if has_streams:
            stream_data = parse_tags_TT(page, start, end)

    elif tracker == "SC":
        client = TwitchHelix(client_id = "qe38ugsyxwcmzg7hhva1b55qhoc65u", oauth_token = "wbrkcr8uyg2p5yw3pn97ci1u4haby5")
        user_id = client.get_users(channel_name)[0]["id"]

        url = f"https://alla.streamscharts.com/api/free/streaming/platforms/1/channels/{user_id}/" \
              f"streams?startDate={start}&endDate={end}"
        page = get_page(url, "json")
        total_streams = page["total"]

        streams_json = {"streams": []}
        with requests.session() as session:
            logger.info("getting stream info from streamcharts")
            for offset in range(0, total_streams, 10):
                url = f"https://alla.streamscharts.com/api/free/streaming/platforms/1/channels/{user_id}/streams?" \
                      f"startDate={start}&endDate={end}&orderBy=stream_created_at&orderDirection=desc&offset={offset}&limit=10"

                data = get_page(url, "json", session)
                streams_json["streams"].extend(data["streams"])
        if total_streams != 0:
            stream_data = parse_tags_SC(streams_json, start, end)

    if stream_data is not None:
        logger.info(f"{len(stream_data)} streams found")
        return stream_data
    logger.info(f"{channel_name} has no recorded stream history (in this date range)")
    return []


def main():
    print("\n-gets stream data between specific time period \n"
          "-choose twitchtracker or steamcharts as tracker\n"
          "     - streamcharts:\n"
          "         PRO: can get multiple vods when stream goes down\n"
          "         CON: earliest stream history is 2019-06-00\n"
          "              slower data retrieval and slower vod finding\n"
          "     - twitchtracker:\n"
          "         PRO: fast\n"
          "              large stream history\n"
          "         CON: will merge multiple streams (can only get 1st part of vod)\n"
          "-Leave start and end empty to get all-time \n"
          "-returns a list with streams as (timestamp, broadcast id, length (in minutes),title\n\n")
    tracker = input("tracker to use [TT/SC]? >> ").strip()
    channel_name = input("streamer name? >> ").strip()
    start = input("from date (earliest) YYYY-MM-DD UTC >> ").strip()
    end = input("to date (newest) YYYY-MM-DD UTC >> ").strip()
    data = get_data(channel_name, start, end, tracker)

    if data is not None:
        for stream in data:
            print(stream)


if __name__ == "__main__":
    main()
