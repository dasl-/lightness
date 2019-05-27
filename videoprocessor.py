import numpy as np
import cv2
import pafy
import pprint
import time
import os
import time
import sys
import urllib

class VideoProcessor:
    video_settings = None
    video_stream = None
    frames_save_path = None

    thumbnail_url = None
    thumbnail = None

    video_fps = None
    video_frames = []

    DATA_DIRECTORY = 'lightness_data'
    DATA_FILE_FORMAT = '%title@%resolution__%color.%extension.npy'
    VIDEO_FILE_FORMAT = '%title@%resolution.%extension'

    def __init__(self, url, video_settings):
        self.video_settings = video_settings
        self.video_stream = self.get_video_stream(url)
        self.frames_save_path = self.get_frames_save_path()

        print("frames path: " + self.frames_save_path)

    def get_and_display_thumbnail(self, video_player):
        try:
            req = urllib.request.urlopen(self.thumbnail_url)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            self.thumbnail = cv2.imdecode(arr, -1)
            self.display_thumbnail(video_player)
        except:
            pass

    def display_thumbnail(self, video_player):
        slice_width = (self.thumbnail.shape[1] / self.video_settings.display_width)
        slice_height = (self.thumbnail.shape[0] / self.video_settings.display_height)
        avg_color_frame = self.get_avg_color_frame(slice_width, slice_height, self.thumbnail)
        video_player.playFrame(avg_color_frame)

    def preprocess_and_play(self, video_player):
        self.get_and_display_thumbnail(video_player)

        if os.path.exists(self.frames_save_path):
            self.video_fps, self.video_frames = np.load(self.frames_save_path)
        else:
            self.process_video()

        video_player.playVideo(self.video_frames, self.video_fps)

    def get_video_stream(self, url):
        p = pafy.new(url)

        # pick lowest resolution because it will be less resource intensive to process
        best_stream = None
        lowest_x_dimension = None

        print("Options:")
        for stream in p.videostreams:
            print("    " + stream.extension + "@" + stream.resolution + " " +
                str(stream._info['fps']) + "fps " + str(round(stream._info['filesize']/1024/1024, 2)) + "MB")
            if (not best_stream or
                (
                    stream.dimensions[0] <= lowest_x_dimension and
                    stream.extension == 'webm' # prefer webm because mp4s sometimes refuse to play
                )
            ):
                best_stream = stream
                lowest_x_dimension = stream.dimensions[0]
        print("Using: " + str(best_stream))
        # pprint.pprint(best_stream.__dict__)

        self.thumbnail_url = p.thumb

        return best_stream

    def save_frames(self):
        np.save(
            self.frames_save_path,
            [self.video_fps, self.video_frames]
        )

    def get_frames_save_path(self):
        filename = self.DATA_FILE_FORMAT \
            .replace('%title', self.video_stream.title) \
            .replace('%resolution', self.video_stream.resolution) \
            .replace('%color', "color" if self.video_settings.is_color else "bw") \
            .replace('%extension', self.video_stream.extension)

        save_path = (self.get_data_directory() + "/" + filename)
        return save_path

    # download video rather than streaming to avoid errors like:
    # [tls @ 0x1388940] Error in the pull function.
    # [matroska,webm @ 0x1396ff0] Read error
    # [tls @ 0x1388940] The specified session has been invalidated for some reason.
    # [tls @ 0x1388940] The specified session has been invalidated for some reason.
    def download_video(self):
        filename = self.VIDEO_FILE_FORMAT \
            .replace('%title', self.video_stream.title) \
            .replace('%resolution', self.video_stream.resolution) \
            .replace('%extension', self.video_stream.extension)

        save_path = (self.get_data_directory() + "/" + filename)

        print("video path: " + save_path)
        if not os.path.exists(save_path):
            self.video_stream.download(save_path)
        return save_path

    def get_data_directory(self):
        save_dir = sys.path[0] + "/" + self.DATA_DIRECTORY
        os.makedirs(save_dir, exist_ok=True)
        return save_dir

    def get_next_frame(self, vid_cap):
        success = True
        # add one because we need to call .grab() once even if we're skipping no frames.
        for x in range(1):
            success = vid_cap.grab()
            if not success:
                return False, None
        success, frame = vid_cap.retrieve()
        if not success:
            return False, None
        return success, frame

    def process_video(self, stream=False, video_player=None):
        video_path = self.download_video()

        # start the video
        vid_cap = cv2.VideoCapture(video_path)

        fps = vid_cap.get(cv2.CAP_PROP_FPS)
        frame_width = vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        frame_height = vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        slice_width = (frame_width / self.video_settings.display_width)
        slice_height = (frame_height / self.video_settings.display_height)

        video_frames = []

        start = time.time()
        i = 0
        log_freq = 1/200
        while True:
            success, frame = self.get_next_frame(vid_cap)
            if not success:
                break

            if not self.video_settings.is_color:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            if i % int(round(log_freq ** -1)) == 0 and i != 0:
                print("Processing frame at " + str(vid_cap.get(cv2.CAP_PROP_POS_MSEC)) + " ms.")
                print ("Processing at " + str(i / (time.time() - start)) + " frames per second.")
                # print(frame.shape)

            avg_color_frame = self.get_avg_color_frame(slice_width, slice_height, frame)
            video_frames.append(avg_color_frame)

            if stream:
                video_player.playFrame(avg_color_frame)
            i += 1

        end = time.time()
        print("processing video took: " + str(end - start) + " seconds")

        vid_cap.release()
        cv2.destroyAllWindows()

        if not os.path.exists(self.frames_save_path):
            self.save_frames()

    def get_avg_color_frame(self, slice_width, slice_height, frame):
        if self.video_settings.is_color:
            avg_color_frame = np.empty((self.video_settings.display_width, self.video_settings.display_height, 3), np.uint8)
        else:
            avg_color_frame = np.empty((self.video_settings.display_width, self.video_settings.display_height), np.uint8)

        for x in range(self.video_settings.display_width):
            for y in range(self.video_settings.display_height):
                mask = np.zeros(frame.shape[:2], np.uint8)
                start_y = int(round(y * slice_height, 0))
                end_y = int(round((y + 1) * slice_height, 0))

                start_x = int(round(x * slice_width, 0))
                end_x = int(round((x + 1) * slice_width, 0))

                mask[start_y:end_y, start_x:end_x] = 1

                # mean returns a list of four 0 - 255 values
                if (self.video_settings.is_color):
                    mean = cv2.mean(frame, mask)
                    avg_color_frame[x, y, 0] = mean[0] # g
                    avg_color_frame[x, y, 1] = mean[1] # b
                    avg_color_frame[x, y, 2] = mean[2] # r
                else:
                    avg_color_frame[x, y] = cv2.mean(frame, mask)[0]

        return avg_color_frame
