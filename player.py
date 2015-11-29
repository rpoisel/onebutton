#!env python3

import sys
import signal
import os
from time import sleep
from datetime import datetime

from mpd import MPDClient, ConnectionError

from hl_io import IoContext, Button, Listener, Led


class Player(object):
    UNKNOWN = 0  # state
    PAUSE = 1  # state
    PLAY = 2  # state
    STOP = 3  # state

    HOST = 'localhost'
    PORT = '6600'

    def __init__(self, green, red):
        self.green = green
        self.red = red
        self.mpdClient = None
        self.__ensureConnected()

    def __ensureConnected(self):
        while self.__isConnected() is False:
            try:
                print("Connecting to MPD ...")
                self.mpdClient = MPDClient()
                self.mpdClient.connect(
                    host=self.HOST, port=self.PORT)
                print("Connected. ")
            except (ConnectionError, ConnectionRefusedError):
                print("Could not connect to MPD. Retrying ...")
                self.red.flash(.2, 1)
                sleep(.5)

    def __isConnected(self):
        if self.mpdClient is None:
            return False
        try:
            self.mpdClient.ping()
        except (ConnectionError, BrokenPipeError):
            return False
        return True

    @property
    def state(self):
        self.__ensureConnected()
        state = self.mpdClient.status()["state"]
        if state == "pause":
            return self.PAUSE
        elif state == "play":
            return self.PLAY
        elif state == "stop":
            return self.STOP
        return self.UNKNOWN

    def play(self):
        self.__ensureConnected()
        while self.state is not self.PLAY:
            self.mpdClient.play()
            sleep(.1)
        self.green.on()

    def pause(self):
        self.__ensureConnected()
        self.mpdClient.pause()
        self.green.off()

    def track_back(self):
        self.__ensureConnected()
        self.mpdClient.previous()
        self.green.flash(.2, 3,
                         turnOn=True if self.state is self.PLAY else False)


class PlayerListener(Listener):

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
        if value and diff >= self.HOLD_PERIOD and self.reset:
            self.reset = False
            self.player.track_back()


class SystemShutdownListener(Listener):

    DBL_CLICK_PERIOD = .7  # seconds

    def __init__(self, led):
        super().__init__()
        self.led = led
        self.lastRTrig = None
        self.clickCnt = 1

    def r_trig(self, diff):
        currentTime = datetime.now()
        if self.lastRTrig is not None:
            diff = (currentTime - self.lastRTrig).total_seconds()
            if diff < SystemShutdownListener.DBL_CLICK_PERIOD:
                self.clickCnt += 1
                if self.clickCnt > 2:
                    self.led.flash(.2, 3, turnOn=True)
                    print("Shutting system down")
                    os.system("systemctl poweroff")
                    self.clickCnt = 0
            else:
                self.clickCnt = 1
        self.lastRTrig = currentTime

    def f_trig(self, diff):
        pass

    def hold(self, diff, value):
        pass


shutdown = False


def main():
    global shutdown
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    io = IoContext()

    green = Led(22)
    red = Led(23)

    player = Player(green, red)
    playerListener = PlayerListener(player)

    shutdownListener = SystemShutdownListener(red)

    button = Button(io, 24)
    button.addButtonListener(playerListener)
    button.addButtonListener(shutdownListener)

    print("System initialized. Playing ...")
    player.play()

    try:
        while shutdown is False:
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
