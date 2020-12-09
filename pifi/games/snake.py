import numpy as np
import random
import time
import collections
import simpleaudio
import traceback
import json
import secrets
from pygame import mixer
from pifi.logger import Logger
from pifi.playlist import Playlist
from pifi.videoplayer import VideoPlayer
from pifi.games.gamecolorhelper import GameColorHelper
from pifi.games.scoredisplayer import ScoreDisplayer
from pifi.games.scores import Scores
from pifi.games.unixsockethelper import UnixSocketHelper, SocketClosedException, SocketConnectionHandshakeException
from pifi.directoryutils import DirectoryUtils

class Snake:

    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    GAME_TITLE = "snake"

    __GAME_OVER_REASON_SNAKE_STATE = 'game_over_reason_snake_state'
    __GAME_OVER_REASON_SKIP_REQUESTED = 'game_over_reason_skip_requested'
    __GAME_OVER_REASON_CLIENT_SOCKET_SIGNAL = 'game_over_reason_client_socket_signal'

    __SNAKE_STARTING_LENGTH = 4

    __SNAKE_COLOR_CHANGE_FREQ = 0.05

    __APPLE_COLOR_CHANGE_FREQ = 0.2

    __logger = None

    # SnakeSettings
    __settings = None

    __game_color_helper = None

    __num_ticks = None

    __game_color_mode = None

    # doubly linked list representing all the coordinate pairs in the snake
    __snake_linked_list = None

    # set datastructure representing all the coordinate pairs in the snake
    __snake_set = None

    __direction = None

    __apple = None

    __apple_sound = None
    __background_music = None
    __background_music_options = [
        'dragon_quest4_05_town.wav',
        'dragon_quest4_04_solitary_warrior.wav',
        'dragon_quest4_19_a_pleasant_casino.wav',
        'radia_senki_reimei_hen_06_unknown_village_elfas.wav', #todo: has a blip in the loop
        'the_legend_of_zelda_links_awakening_04_mabe_village_loop.wav',
    ]

    __playlist = None

    __playlist_video_id = None

    __scores = None

    __unix_socket_helper = None


    def __init__(self, settings, unix_socket, playlist_video_id):
        self.__logger = Logger().set_namespace(self.__class__.__name__)
        self.__settings = settings
        self.__game_color_helper = GameColorHelper()
        self.__video_player = VideoPlayer(self.__settings)
        self.__logger.info("Doing init with SnakeSettings: {}".format(vars(self.__settings)))
        self.__scores = Scores()
        self.__unix_socket_helper = UnixSocketHelper().set_server_socket(unix_socket)
        self.__playlist = Playlist()
        self.__playlist_video_id = playlist_video_id

        # why do we use both simpleaudio and pygame mixer? see: https://github.com/dasl-/pifi/blob/master/utils/sound_test.py
        mixer.init(frequency = 22050, buffer = 512)
        self.__apple_sound = simpleaudio.WaveObject.from_wave_file(DirectoryUtils().root_dir + "/assets/snake/sfx_coin_double7_75_pct_vol.wav")

    def newGame(self):
        self.__reset()
        self.__show_board()

        if not self.__accept_socket():
            self.__end_game(self.__GAME_OVER_REASON_CLIENT_SOCKET_SIGNAL)
            return


        background_music_file = secrets.choice(self.__background_music_options)
        self.__background_music = mixer.Sound(DirectoryUtils().root_dir + "/assets/snake/{}".format(background_music_file))
        self.__background_music.play(loops = -1)

        while True:
            # TODO : sleep for a variable amount depending on how long each loop iteration took. Should
            # lead to more consistent tick durations?
            time.sleep(-0.02 * self.__settings.difficulty + 0.21)

            move = None
            if self.__unix_socket_helper.is_ready_to_read():
                try:
                    move = self.__unix_socket_helper.recv_msg()
                except (SocketClosedException, ConnectionResetError) as e:
                    self.__end_game(self.__GAME_OVER_REASON_CLIENT_SOCKET_SIGNAL)
                    break

                move = int(move)
                if move not in (self.UP, self.DOWN, self.LEFT, self.RIGHT):
                    move = self.UP

            if move is not None:
                new_direction = move
                if (
                    (self.__direction == self.UP or self.__direction == self.DOWN) and
                    (new_direction == self.UP or new_direction == self.DOWN)
                ):
                    pass
                elif (
                    (self.__direction == self.LEFT or self.__direction == self.RIGHT) and
                    (new_direction == self.LEFT or new_direction == self.RIGHT)
                ):
                    pass
                else:
                    self.__direction = new_direction
            self.__tick()
            if self.__is_game_over():
                self.__end_game(self.__GAME_OVER_REASON_SNAKE_STATE)
                break
            if self.__should_skip_game():
                self.__end_game(self.__GAME_OVER_REASON_SKIP_REQUESTED)
                break

    def __tick(self):
        self.__num_ticks += 1
        old_head_y, old_head_x = self.__snake_linked_list[0]

        if self.__direction == self.UP:
            new_head = ((old_head_y - 1) % self.__settings.display_height, old_head_x)
        elif self.__direction == self.DOWN:
            new_head = ((old_head_y + 1) % self.__settings.display_height, old_head_x)
        elif self.__direction == self.LEFT:
            new_head = (old_head_y, (old_head_x - 1) % self.__settings.display_width)
        elif self.__direction == self.RIGHT:
            new_head = (old_head_y, (old_head_x + 1) % self.__settings.display_width)

        self.__snake_linked_list.insert(0, new_head)

        # Must call this before placing the apple to ensure the apple is not placed on the new head
        self.__snake_set.add(new_head)

        if new_head == self.__apple:
            self.__eat_apple()
        else:
            old_tail = self.__snake_linked_list[-1]
            del self.__snake_linked_list[-1]
            if old_tail != new_head:
                # Prevent edge case when the head is "following" the tail.
                # If the old_tail is the same as the new_head, we don't want to remove the old_tail from the set
                # because  the call to `self.__snake_set.add(new_head)` would have been a no-op above.
                self.__snake_set.remove(old_tail)

        self.__show_board()

    def __eat_apple(self):
        play_obj = self.__apple_sound.play()
        self.__place_apple()

    def __place_apple(self):
        # TODO: make better
        while True:
            x = random.randint(0, self.__settings.display_width - 1)
            y = random.randint(0, self.__settings.display_height - 1)
            if (y, x) not in self.__snake_set:
                break
        self.__apple = (y, x)

    def __is_game_over(self):
        return len(self.__snake_set) < len(self.__snake_linked_list)

    def __show_board(self):
        frame = np.zeros([self.__settings.display_height, self.__settings.display_width, 3], np.uint8)
        snake_rgb = self.__game_color_helper.get_rgb(self.__game_color_mode, self.__SNAKE_COLOR_CHANGE_FREQ, self.__num_ticks)
        apple_rgb = self.__game_color_helper.get_rgb(GameColorHelper.GAME_COLOR_MODE_RAINBOW, self.__APPLE_COLOR_CHANGE_FREQ, self.__num_ticks)

        for (y, x) in self.__snake_linked_list:
            frame[y, x] = snake_rgb

        if self.__apple is not None:
            frame[self.__apple[0], self.__apple[1]] = apple_rgb

        self.__video_player.play_frame(frame)

    def __reset(self):
        self.__direction = self.RIGHT
        self.__num_ticks = 0
        self.__game_color_helper.reset()
        self.__game_color_mode = self.__game_color_helper.determine_game_color_mode(self.__settings)
        height_midpoint = int(round(self.__settings.display_height / 2, 1))
        width_midpoint = int(round(self.__settings.display_width / 2, 1))
        self.__reset_datastructures()

        for x in range(self.__SNAKE_STARTING_LENGTH):
            coordinate = (height_midpoint, width_midpoint - x)
            self.__snake_linked_list.append(coordinate)
            self.__snake_set.add(coordinate)

        self.__place_apple()

    def __reset_datastructures(self):
        self.__snake_linked_list = collections.deque()
        self.__apple = None
        self.__snake_set = set()

    def __end_game(self, reason):
        if self.__background_music:
            self.__background_music.fadeout(500)
        score = (len(self.__snake_linked_list) - self.__SNAKE_STARTING_LENGTH) * self.__settings.difficulty
        if reason == self.__GAME_OVER_REASON_SNAKE_STATE:
            self.__do_scoring(score)

        self.__unix_socket_helper.close()
        self.__clear_board()
        mixer.quit()
        simpleaudio.stop_all()

        self.__logger.info("game over. score: {}. Reason: {}".format(score, reason))
        self.__reset_datastructures()

    def __do_scoring(self, score):
        simpleaudio.WaveObject.from_wave_file(DirectoryUtils().root_dir + "/assets/snake/LOZ_Link_Die.wav").play()
        is_high_score = self.__scores.is_high_score(score, self.GAME_TITLE)
        score_id = self.__scores.insert_score(score, self.GAME_TITLE)
        if is_high_score:
            highscore_message = json.dumps({
                'message_type': 'high_score',
                'score_id' : score_id
            })
            try:
                self.__unix_socket_helper.send_msg(highscore_message)
            except Exception as e:
                self.__logger.error('Unable to send high score message: {}'.format(traceback.format_exc()))

        time.sleep(0.3)
        for x in range(1, 9): # blink board
            self.__clear_board()
            time.sleep(0.1)
            self.__show_board()
            time.sleep(0.1)

        score_color = [255, 0, 0] # red
        score_tick = 0
        if is_high_score:
            score_color = self.__game_color_helper.get_rgb(
                game_color_mode = GameColorHelper.GAME_COLOR_MODE_RAINBOW,
                color_change_freq = 0.2,
                num_ticks = score_tick
            )
            (simpleaudio.WaveObject
                .from_wave_file(DirectoryUtils().root_dir + "/assets/snake/SFX_LEVEL_UP_40_pct_vol.wav")
                .play())
        score_displayer = ScoreDisplayer(self.__settings, self.__video_player, score)
        score_displayer.display_score(score_color)

        for i in range(1, 100):
            # if someone clicks "New Game" while the score is being displayed, immediately start a new game
            # instead of waiting for the score to stop being displayed
            #
            # also make the score display in rainbow if it was a high score.
            time.sleep(0.05)

            if is_high_score:
                score_tick += 1
                score_color = self.__game_color_helper.get_rgb(
                    game_color_mode = GameColorHelper.GAME_COLOR_MODE_RAINBOW,
                    color_change_freq = 0.2,
                    num_ticks = score_tick
                )
                score_displayer.display_score(score_color)

            if i % 5 == 0 and self.__should_skip_game():
                break

    def __clear_board(self):
        frame = np.zeros([self.__settings.display_height, self.__settings.display_width, 3], np.uint8)
        self.__video_player.play_frame(frame)

    def __should_skip_game(self):
        if self.__playlist.should_skip_video_id(self.__playlist_video_id):
            return True
        return False;

    def __accept_socket(self):
        while True:
            try:
                self.__unix_socket_helper.accept()
            except SocketConnectionHandshakeException as e:
                # Error during handshake, there may be other websocket initiated connections in the backlog that want accepting.
                # Try again to avoid a situation where we accidentally had more backlogged requests than we ever call
                # accept on. For example, if people spam the "new game" button, we may have several websockets that called
                # `connect` on the unix socket, but only one instance of the snake process will ever call `accept` (the rest got
                # skipped by the playlist). Thus, if we did not loop through and accept all these queued requests, we would never
                # eliminate this backlog of queued stale requests.
                self.__logger.info('Calling accept again due to handshake error: {}'.format(traceback.format_exc()))
                continue
            except Exception as e2:
                # Error during `accept`, so no indication that there are other connections that want accepting.
                # The backlog is probably empty. Could have been timeout waiting for client to connect.
                self.__logger.error('Caught exception during accept: {}'.format(traceback.format_exc()))
                return False

            # Sanity check that the client that ended up connected to our socket is the one that was actually intended.
            # This could be mismatched if two client new game requests happened in quick succession.
            # 1) First "new game" request opens websocket and calls `connect` on the unix socket
            # 2) second "new game" request opens websocket and calls `connect` on unix socket
            # 3) First "new game" queues up in the playlist table
            # 4) Second "new game" queues up in the playlist table, causing the one queued in (3) to be skipped
            # 5) Snake process starts running, corresponding to the playlist item queued up in (4)
            # 6) Snake calls `accept` and is now connected via the unix socket to the websocket from (1)
            # 7) observe that client is from first "new game" request and server is from second "new game" request. Mismatch.
            try:
                client_playlist_video_id = json.loads(self.__unix_socket_helper.recv_msg())['playlist_video_id']
                if client_playlist_video_id != self.__playlist_video_id:
                    raise Exception("Server was playing playlist_video_id: {}, but client was playing playlist_video_id: {}."
                        .format(self.__playlist_video_id, client_playlist_video_id))
            except Exception as e:
                self.__logger.info('Calling accept again due to playlist_video_id mismatch error: {}'.format(traceback.format_exc()))
                continue

            return True
