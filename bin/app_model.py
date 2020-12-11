# Model (data)
import get_all_vods_clips


class Model:

    def __init__(self):
        """ Initializes the members the class holds """

        self.channel_name = None
        self.vods_clips = None
        self.date_type = None
        self.date = None
        self.file_name = None
        self.output_folder = None

        self.link_data = [self.channel_name, self.vods_clips, self.date_type, self.date]

    def link_data_isvalid(self, data):
        """ returns True if the input data is valid
        Returns False otherwise."""
        vods_clips = ["clips", "vods"]
        date_types = ["all", "latest", "date", "daterange"]
        if len(data[0]) >= 4:
            if data[1] in vods_clips:
                if data[2] in date_types:
                    return ((len(data[3]) == 3) and (None in data[3])) \
                           or ((len(data[3]) == 2) and (None not in data[3]))
        return False

    def set_data(self, data):
        """ Gets all the links for the data provided"""
        if self.link_data_isvalid(data):
            self.link_data = data
            self.channel_name = data[0]
            self.vods_clips = data[1]
            self.date_type = data[2]
            self.date = data[3]
        else:
            self.link_data = [None, None, None, None]

    def get_links(self):
        index, start, end = 0, None, None
        if self.date_type == "latest":
            index = int(f"-{self.date[2]}")
        elif self.date_type == "date" or self.date_type == "daterange":
            start = self.date[0]
            end = self.date[1]
        print("Starting program:")
        file_name = get_all_vods_clips.get_vods_clips(self.channel_name, self.vods_clips, index = index, start = start, end = end)
        print(f"{self.vods_clips[:-1]} links located in '/output/data/{file_name}'")
