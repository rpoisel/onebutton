#!env python3

import sys
import signal
from time import sleep
from socket import error as SocketError

from mpd import MPDClient, ConnectionError

from hl_io import IoContext, Button, Listener, Led


class Player(object):
    UNKNOWN = 0  # state
    PAUSE = 1  # state
    PLAY = 2  # state
    STOP = 3  # state

    HOST = 'localhost'
    PORT = '6600'

    def __init__(self, led):
        self.led = led
        self.connect()

    def connect(self):
        connected = False
        while connected is False:
            try:
                self.mpdClient = MPDClient()
                self.mpdClient.connect(
                    host=self.HOST, port=self.PORT)
                connected = True
            except (ConnectionError, ConnectionRefusedError):
                print("Could not connect to MPD. Retrying ...")
                sleep(.5)

    @property
    def state(self):
        state = self.mpdClient.status()["state"]
        if state == "pause":
            return self.PAUSE
        elif state == "play":
            return self.PLAY
        elif state == "stop":
            return self.STOP
        return self.UNKNOWN

    def play(self):
        while self.state is not self.PLAY:
            self.mpdClient.play()
            sleep(.1)
        self.led.on()

    def pause(self):
        self.mpdClient.pause()
        self.led.off()

    def track_back(self):
        self.mpdClient.previous()
        self.led.flash(.2, 3,
                       turnOn=True if self.state is self.PLAY else False)


class ButtonListener(Listener):

    HOLD_PERIOD = 2  # seconds

    def __init__(self, player):
        super().__init__()
        self.player = player
        self.reset = True

    def r_trig(self, diff):
        self.reset = True

    def f_trig(self, diff):
        if diff < self.HOLD_PERIOD:
            if self.player.state is Player.PLAY:
                self.player.pause()
            else:
                self.player.play()

    def hold(self, diff, value):
        if value is True and \
                diff >= self.HOLD_PERIOD and \
                self.reset is True:
            self.reset = False
            self.player.track_back()


shutdown = False


def main():
    global shutdown
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    io = IoContext()

    green = Led(22)
    red = Led(23)

    player = Player(green)
    buttonListener = ButtonListener(player)

    button = Button(io, 24)
    button.addButtonListener(buttonListener)

    print("System initialized. Playing ...")
    player.play()

    try:
        while shutdown is False:
            red.flash(.2, 3)
            sleep(.2)
    except KeyboardInterrupt:
        pass
    finally:
        print("Shutting down. ")
        if player is not None:
            player.pause()
        if io is not None:
            io.cleanup()
        sys.exit(0)


def sig_handler(signum, frame):
    global shutdown
    shutdown = True


if __name__ == "__main__":
    main()
