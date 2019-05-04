import numpy as np
import cv2
import pafy
import pprint
import random
import time
import argparse
import math
import os
import time

# gamma 2.8, brightness .4
scale_red = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 12, 12, 12, 12, 13, 13, 13, 14, 14, 14, 14, 15, 15, 15, 16, 16, 16, 17, 17, 18, 18, 18, 19, 19, 19, 20, 20, 21, 21, 21, 22, 22, 23, 23, 24, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 29, 29, 30, 30, 31, 31, 32, 32, 33, 33, 34, 34, 35, 36, 36, 37, 37, 38, 38, 39, 40, 40, 41, 42, 42, 43, 43, 44, 45, 45, 46, 47, 47, 48, 49, 50, 50, 51, 52, 52, 53, 54, 55, 55, 56, 57, 58, 58, 59, 60, 61, 62, 62, 63, 64, 65, 66, 67, 67, 68, 69, 70, 71, 72, 73, 74, 75, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 98, 99, 100, 101, 102]
# gamma 2.8, brightness .15
scale_green = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 13, 13, 13, 13, 13, 14, 14, 14, 14, 15, 15, 15, 15, 15, 16, 16, 16, 16, 17, 17, 17, 17, 18, 18, 18, 18, 19, 19, 19, 20, 20, 20, 20, 21, 21, 21, 21, 22, 22, 22, 23, 23, 23, 24, 24, 24, 24, 25, 25, 25, 26, 26, 26, 27, 27, 27, 28, 28, 28, 29, 29, 30, 30, 30, 31, 31, 31, 32, 32, 32, 33, 33, 34, 34, 34, 35, 35, 36, 36, 36, 37, 37, 38, 38]
# gamma 2.8, brightness .22
scale_blue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 12, 13, 13, 13, 13, 14, 14, 14, 14, 15, 15, 15, 15, 16, 16, 16, 17, 17, 17, 17, 18, 18, 18, 19, 19, 19, 20, 20, 20, 20, 21, 21, 21, 22, 22, 22, 23, 23, 23, 24, 24, 25, 25, 25, 26, 26, 26, 27, 27, 28, 28, 28, 29, 29, 30, 30, 30, 31, 31, 32, 32, 33, 33, 33, 34, 34, 35, 35, 36, 36, 37, 37, 38, 38, 38, 39, 39, 40, 40, 41, 41, 42, 42, 43, 43, 44, 45, 45, 46, 46, 47, 47, 48, 48, 49, 49, 50, 51, 51, 52, 52, 53, 54, 54, 55, 55, 56]

# remember to make sure if r, g, or b has a zero in the scale they all do, otherwise dim pixels will be just that color
def getGamma(gamma, max_in, max_out):
    gamma_list = []
    for i in range (0, max_in+1):
        gamma_list.append(int(math.floor((pow(float(i / max_in), gamma) * max_out + 0.5))))

    return gamma_list;

scale_red = getGamma(3, 255, int(255 * .4));
scale_green = getGamma(3, 255, int(255 * .15));
scale_blue = getGamma(3, 255, int(255 * .22));

for i in range (0,256):
    if (min(scale_red[i], scale_green[i], scale_blue[i]) == 0):
        scale_red[i] = 0
        scale_green[i] = 0
        scale_blue[i] = 0
    else:
        break

def parseArgs():
    parser = argparse.ArgumentParser(description='convert a video.')
    parser.add_argument('--url', dest='url', action='store', default='https://www.youtube.com/watch?v=xmUZ6nCFNoU',
        help='youtube video url. default: The Smashing Pumpkins - Today.')
    parser.add_argument('--out-pi', dest='should_output_pi', action='store_true', default=False,
        help='Display output on raspberry pi.')
    parser.add_argument('--out-frame', dest='should_output_frame', action='store_true', default=False,
        help='Display output on opencv frame.')
    parser.add_argument('--display-width', dest='display_width', action='store', type=int, default=19, metavar='N',
        help='Number of pixels / units')
    parser.add_argument('--display-height', dest='display_height', action='store', type=int, default=4, metavar='N',
        help='Number of pixels / units')
    parser.add_argument('--skip-frames', dest='num_skip_frames', action='store', type=int, default=0, metavar='N',
        help='Number of frames to skip every output iteration from the youtube video. Default: 0 (skip no frames)')
    parser.add_argument('--color', dest='is_color', action='store_true', default=False,
        help='color output? (default is black and white)')
    parser.add_argument('--brightness', dest='brightness', action='store', type=int, default=2, metavar='N',
        help='Global brightness value. Max of 31.')
    parser.add_argument('--stream', dest='should_preprocess_video', action='store_false', default=True,
        help='If set, the video will be streamed instead of pre-processed')

    args = parser.parse_args()
    return args


def setupOutputPi():
    from driver import apa102
    # Add 8 because otherwise the last 8 LEDs don't powered correctly. Weird driver glitch?
    pixels = apa102.APA102(
        num_led=(args.display_width * args.display_height + 8),
        global_brightness=args.brightness, mosi = 10, sclk = 11, order='rbg'
    )
    pixels.clear_strip()
    return pixels

def showOutputPi(avg_color_frame):
    for x in range(args.display_width):
        for y in range(args.display_height):
            if args.is_color:
                r = scaleOutput(avg_color_frame[x, y, 2], scale_red)
                b = scaleOutput(avg_color_frame[x, y, 1], scale_blue)
                g = scaleOutput(avg_color_frame[x, y, 0], scale_green)
                color = pixels.combine_color(r, g, b)
            else:
                r = scaleOutput(avg_color_frame[x, y], scale_red)
                b = scaleOutput(avg_color_frame[x, y], scale_blue)
                g = scaleOutput(avg_color_frame[x, y], scale_green)
                color = pixels.combine_color(r, g, b)
            setPixel(x, y, color)
    pixels.show()

def setPixel(x, y, color):
    if (y % 2 == 0):
        pixel_index = (y * args.display_width) + (args.display_width - x - 1)
    else:
        pixel_index = (y * args.display_width) + x

    pixels.set_pixel_rgb(pixel_index, color)

def scaleOutput(val, gamma_scale):
    return gamma_scale[int(val)]

def show_output_for_frames(avg_color_frames, fps, should_output_pi, should_output_frame):
    for avg_color_frame in avg_color_frames:
        show_output_for_frame(avg_color_frame, should_output_pi, should_output_frame)
        # time.sleep((1/fps)/2)

def showOutputFrame(avg_color_frame): #todo: fix this for running with --color
    canvas_width = 600
    canvas_height = 400

    img = np.zeros((canvas_height, canvas_width, 1), np.uint8)
    slice_height = int(canvas_height / args.display_height)
    slice_width = int(canvas_width / args.display_width)
    for x in range(args.display_width):
        for y in range(args.display_height):
            img[(y * slice_height):((y + 1) * slice_height), (x * slice_width):((x + 1) * slice_width)] = avg_color_frame[x, y]

    cv2.imshow('image',img)
    cv2.waitKey(1)

def show_output_for_frame(avg_color_frame, should_output_pi, should_output_frame):
    if should_output_pi:
        showOutputPi(avg_color_frame)
    if should_output_frame:
        showOutputFrame(avg_color_frame)

def get_video_stream(should_preprocess_video):
    p = pafy.new(args.url)

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
    pprint.pprint(best_stream.__dict__)
    return best_stream

def save_frames(video_stream, avg_color_frames, is_color, num_skip_frames):
    np.save(get_frames_save_path(video_stream, is_color, num_skip_frames), avg_color_frames)

def get_frames_save_path(video_stream, is_color, num_skip_frames):
    save_dir = "/tmp/led"
    os.makedirs(save_dir, exist_ok = True)
    color_str = ""
    if is_color:
        color_str += "color"
    else:
        color_str += "bw"
    save_path = (save_dir + "/" + video_stream.title + "@" + video_stream.resolution + "__" + color_str +
        "__skip" + str(num_skip_frames) + "." + video_stream.extension + ".npy")
    return save_path

# download video rather than streaming to avoid errors like:
# [tls @ 0x1388940] Error in the pull function.
# [matroska,webm @ 0x1396ff0] Read error
# [tls @ 0x1388940] The specified session has been invalidated for some reason.
# [tls @ 0x1388940] The specified session has been invalidated for some reason.
def download_video(video_stream):
    save_dir = "/tmp/led"
    os.makedirs(save_dir, exist_ok = True)

    save_path = save_dir + "/" + video_stream.title + "@" + video_stream.resolution + "." + video_stream.extension
    print("video path: " + save_path)
    if not os.path.exists(save_path):
        video_stream.download(save_path)
    return save_path


def get_next_frame(vid_cap, num_skip_frames):
    success = True
    for x in range(num_skip_frames + 1): # add one because we need to call .grab() once even if we're skipping no frames.
        success = vid_cap.grab()
        if not success:
            return False, None
    success, frame = vid_cap.retrieve()
    if not success:
        return False, None
    return success, frame

def process_video(video_stream, args):
    video_path = download_video(video_stream)

    # start the video
    vid_cap = cv2.VideoCapture(video_path)

    avg_color_frames = []
    while (True):
        success, frame = get_next_frame(vid_cap, args.num_skip_frames)
        if not success:
            break

        if not args.is_color:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)


        frame_width = vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        frame_height = vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        slice_height = int(frame_height / args.display_height)
        slice_width = int(frame_width / args.display_width)

        if args.is_color:
            avg_color_frame = np.zeros((args.display_width, args.display_height, 3), np.uint8)
        else:
            avg_color_frame = np.zeros((args.display_width, args.display_height), np.uint8)

        for x in range(args.display_width):
            for y in range(args.display_height):
                mask = np.zeros(frame.shape[:2], np.uint8)
                mask[(y * slice_height):((y + 1) * slice_height), (x * slice_width):((x + 1) * slice_width)] = 1
                # mean returns a list of four 0 - 255 values
                if (args.is_color):
                    mean = cv2.mean(frame, mask)
                    avg_color_frame[x, y, 0] = mean[0]
                    avg_color_frame[x, y, 1] = mean[1]
                    avg_color_frame[x, y, 2] = mean[2]
                else:
                    avg_color_frame[x, y] = cv2.mean(frame, mask)[0]

        print(vid_cap.get(cv2.CAP_PROP_POS_MSEC))
        print(frame.shape)
        print(vid_cap.get(cv2.CAP_PROP_FPS))
        #pprint.pprint(avg_color_frame)

        if args.should_preprocess_video:
            avg_color_frames.append(avg_color_frame)
        else:
            show_output_for_frame(avg_color_frames, args.should_output_pi, args.should_output_frame)

    vid_cap.release()
    if args.should_preprocess_video:
        save_frames(video_stream, avg_color_frames, args.is_color, args.num_skip_frames)
        show_output_for_frames(avg_color_frame, video_stream._info['fps'], args.should_output_pi, args.should_output_frame)


args = parseArgs()
pixels = None
if (args.should_output_pi):
    pixels = setupOutputPi()

video_stream = get_video_stream(args.should_preprocess_video)
frames_save_path = get_frames_save_path(video_stream, args.is_color, args.num_skip_frames)
print("frames path: " + frames_save_path)
if os.path.exists(frames_save_path):
    avg_color_frames = np.load(frames_save_path)
    show_output_for_frames(avg_color_frames, video_stream._info['fps'], args.should_output_pi, args.should_output_frame)
else:
    process_video(video_stream, args)

cv2.destroyAllWindows()
