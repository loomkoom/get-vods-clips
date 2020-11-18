# get-vods-clips #



<!--
*** Thanks for checking out this README Template. If you have a suggestion that would
*** make this better, please fork the repo and create a pull request or simply open
*** an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
***
***
***
*** To avoid retyping too much info. Do a search and replace for the following:
*** github_username, repo_name, twitter_handle, email
-->





<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
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
* [Acknowledgements](#acknowledgements)


### Built With

* [python 3+](https://www.python.org/downloads/)
* packages used:
  * [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
  * [python-vlc](https://pypi.org/project/python-vlc/)
  * [requests](https://pypi.org/project/requests/)
  * [m3u8](https://pypi.org/project/m3u8/)


### Prerequisites

* [python](https://www.python.org/downloads/)
* [VLC media player](https://www.videolan.org/vlc/index.html) is used to check if links with a valid url are playable or not
* [ffmpeg](https://ffmpeg.org/download.html#build-windows) if you wish to download the vods

### Installation

1. Clone or download the repo
2. run install.cmd to install required packages


<!-- USAGE EXAMPLES -->
### Usage
You need to have some data from the stream if you want a specific vod or clips from that vod (for get_all_vods_and_clips.cmd only a date range is needed) <br>
all data can be found on twitchtracker if you inspect element on the stream link in the streams page https://twitchtracker.com/twitch/streams
Using twitches glitchcon eve stream as an example: https://twitchtracker.com/twitch/streams/40468501598 <br>
![tracker image][tracker-url] <br>
![source image][source-url]

vod-id = 40468501598 <br>
timestamp = 2020-11-13 19:14:07 <br>
channel name = twitch <br>
length = 30 (minutes) <br>

__all script executables are located in the scripts folder__

**get_clips.cmd** returns a list with all clips from a specific vod-id

**get_vod.cmd** gets the vod from the channel name,timestamp and vod-id if it's still available. If the vod is muted it also writes a muted version in output/files/playlists

**get_muted_vod.cmd** writes a muted vod file in output/files/playlists if you input a url and filename

**get_all_vods_and_clips.cmd** writes a text file with all vods or urls found in a certain time period from channel name and date range

**get_stream_data.cmd** returns a list with all stream data in certain time period from channel name and date range with each stream as (timestamp, vod_id, minutes, title)

**test_vods.cmd** test all the vod links (with vlc) in the specified input file in /output/data and writes all succesful links to output file




<!-- ACKNOWLEDGEMENTS -->
### Acknowledgements

* [u/ForgotMyPassword_III](https://www.reddit.com/r/LivestreamFail/comments/js6sf3/geeken_monkaw_deleted_vods_still_accessible/gbxwj0x?utm_source=share&utm_medium=web2x&context=3) on how to get vods
* [daylamtayari](https://github.com/daylamtayari) on how to get clips





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
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
