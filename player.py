#!env python3

import sys
from hl_io import IoContext, Button, Listener, Led
from time import sleep
from mpd import MPDClient
from socket import error as SocketError


class Player(object):
    UNKNOWN = 0  # state
    PAUSE = 1  # state
    PLAY = 2  # state

    HOST = 'localhost'
    PORT = '6600'

    def __init__(self, led):
        self.led = led

        self.mpdClient = MPDClient()
        self.mpdClient.connect(
            host=self.HOST, port=self.PORT)

    @property
    def state(self):
        state = self.mpdClient.status()["state"]
        if state == "pause":
            return self.PAUSE
        elif state == "play":
            return self.PLAY
        return self.UNKNOWN

    def play(self):
        self.mpdClient.play()
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


def main():
    io = IoContext()

    green = Led(22)
    red = Led(23)

    try:
        player = Player(green)
    except SocketError as exc:
        io.cleanup()
        print("Could not connect to MPD: " + str(exc))
        sys.exit(1)
    buttonListener = ButtonListener(player)
    player.play()

    button = Button(io, 24)
    button.addButtonListener(buttonListener)

    try:
        while True:
            red.flash(.2, 3)
            sleep(.2)
    except KeyboardInterrupt:
        player.pause()
        io.cleanup()


if __name__ == "__main__":
    main()
