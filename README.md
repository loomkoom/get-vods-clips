get-vods-clips

run **install.cmd** on first launch to install dependencies

**get_clips.cmd** returns a list with all clips from a specific vod-id

**get_vod.cmd** gets the vod from the channel name,timestamp and vod-id if it's still available. If the vod is muted it also writes a muted version in output/files/playlists

**get_muted_vod.cmd** writes a muted vod file in output/files/playlists if you input a url and filename

**get_all_vods_and_clips.cmd** writes a text file with all vods or urls found in a certain time period from channel name and date range
