# get-vods-clips #

<!-- PROJECT SHIELDS -->
<!--
*** Using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![CodeFactor][codefactor-shield]][codefactor-url]
[![codecov][codecov-shield]][codecov-url]
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]

<!-- TABLE OF CONTENTS -->

### Table of Contents

* [Built With](#built-with)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Usage](#usage)
* [Roadmap](#roadmap)
* [Acknowledgements](#acknowledgements)

### Built With

* [python 3.5+](https://www.python.org/downloads/)
* packages used:
  * [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
  * [mpv](https://pypi.org/project/mpv/)
  * [requests](https://pypi.org/project/requests/)
  * [m3u8](https://pypi.org/project/m3u8/)

### Prerequisites

* installer as of now only supported on Windows (otherwise download programs separately)
* [python](https://www.python.org/downloads/)
* [MPV](https://mpv.io/) is used to check if links with a valid url are playable or not
* [ffmpeg](https://ffmpeg.org/download.html#build-windows) if you wish to download the vods

### Installation

1. Clone or download the repo
2. run installer.cmd to install needed programs and required packages, also updates files if needed.

<!-- USAGE EXAMPLES -->

### Usage

**Disclaimer this uses undocumented twitch end points and may break at any point in time** <br>

**info:** <br>

- Vods are only retrievable for the last 60days with some exceptions <br>
- If a vod goes down or is restarted resulting in multiple vods for the same stream in twitchtracker, only the 1st vod part will be found. <br>
- for clips most are retrievable for an unlimited amount of time but not 100% are found. <br>

- You need to have some data from the stream if you want to run scripts under the [extra scripts](#extra-scripts) section<br>
  all data can be found on twitchtracker if you inspect element on the stream link in the streams page https://twitchtracker.com/twitch/streams
  Using twitches glitchcon eve stream as an example: https://twitchtracker.com/twitch/streams/40468501598 <br>
  (dates/times are always in UTC format!) <br>
  ![tracker image][tracker-url] <br>
  ![source image][source-url] <br>
  Broadcast-id = 40468501598 <br>
  timestamp = 2020-11-13 19:14:07 <br>
  channel name = twitch <br>
  length = 30 (minutes) <br>

**<ins>all script executables are located in the scripts folder </ins>** <br>

### main scripts

* **get_all_vods_and_clips.cmd** writes a text file with all vods or urls found in a certain time period from channel name and date range and allows
  you to download everything it finds (*only thing you need to run if you want to bulk search clips/vods for a channel*)

* **download_all_files.cmd** downloads all links in the text file generated from get_all_vods_and_clips.cmd if you provide the name of the file in
  output/files/data (*use if you chose not to download at first in get_all_vods_and_clips but want to do it afterwards*)

* **get_vods_date.cmd** retrieves all vods from a specific day on a channel

* **get_clips_date.cmd** retrieves all clips from a specific day on a channel

### extra scripts

* **get_clips.cmd** returns a list with all clips from a specific broadcast-id

* **get_vod.cmd** gets the vod from the channel name,timestamp and vod-id if it's still available. If the vod is muted it also writes a muted version
  in output/files/playlists

* **get_muted_vod.cmd** writes a muted vod file in output/files/playlists if you input a url and filename

* **get_stream_data.cmd** returns a list with all stream data in certain time period from channel name and date range with each stream as (timestamp,
  broadcast-id, minutes, title)

* **test_vods.cmd** test all the vod links (with mpv) in the specified input file in /output/data and writes all successful links to output file

<!-- ROADMAP -->

### Roadmap

* [x] get vods by the timestamp and ID
* [x] get clips by ID and length
* [x] get vods/clips by date
* [x] get all vods/clips in date range
* [x] download them from generated txt file
* [ ] implement GUI
* [ ] make .exe for easier install

<!-- ACKNOWLEDGEMENTS -->

### Acknowledgements

* [u/ForgotMyPassword_III](https://www.reddit.com/r/LivestreamFail/comments/js6sf3/geeken_monkaw_deleted_vods_still_accessible/gbxwj0x?utm_source=share&utm_medium=web2x&context=3)
  on how to get vods
* [daylamtayari](https://github.com/daylamtayari) on how to get clips

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[codefactor-shield]: https://www.codefactor.io/repository/github/loomkoom/get-vods-clips/badge

[codefactor-url]: https://www.codefactor.io/repository/github/loomkoom/get-vods-clips

[codecov-shield]: https://codecov.io/gh/loomkoom/get-vods-clips/branch/dev/graph/badge.svg?token=854YYAWM89

[codecov-url]: https://codecov.io/gh/loomkoom/get-vods-clips

[contributors-shield]: https://img.shields.io/github/contributors/loomkoom/get-vods-clips.svg?style=flat-square

[contributors-url]: https://github.com/loomkoomget-vods-clips/graphs/contributors

[forks-shield]: https://img.shields.io/github/forks/loomkoom/get-vods-clips.svg?style=flat-square

[forks-url]: https://github.com/loomkoom/get-vods-clips/network/members

[stars-shield]: https://img.shields.io/github/stars/loomkoom/get-vods-clips.svg?style=flat-square

[stars-url]: https://github.com/loomkoom/get-vods-clips/stargazers

[issues-shield]: https://img.shields.io/github/issues/loomkoom/get-vods-clips.svg?style=flat-square

[issues-url]: https://github.com/loomkoom/get-vods-clips/issues

[source-url]: https://i.imgur.com/p1ZN35k.png

[tracker-url]: https://i.imgur.com/D6E5h0Z.png
