#!env python3

from hl_io import IoContext, Button, Listener, Led
from time import sleep


class Player(Listener):
    PAUSE = 1  # state
    PLAY = 2  # state

    HOLD_PERIOD = 2  # seconds

    def __init__(self, led):
        super().__init__()
        self.led = led
        self.state = self.PLAY
        self.reset = True

    def r_trig(self, diff):
        self.reset = True

    def f_trig(self, diff):
        if diff < self.HOLD_PERIOD:
            if self.state is self.PLAY:
                self.pause()
            else:
                self.play()

    def hold(self, diff, value):
        if value is True and diff >= self.HOLD_PERIOD and self.reset is True:
            self.reset = False
            print("TRACK BACK")

    def play(self):
        self.state = self.PLAY
        print("PLAY")
        self.led.on()

    def pause(self):
        self.state = self.PAUSE
        print("PAUSE")
        self.led.off()


def main():
    io = IoContext()

    green = Led(22)
    red = Led(23)

    player = Player(green)
    player.play()

    b = Button(io, 24)
    b.addButtonListener(player)

    try:
        while True:
            red.flash(.2, 3)
            sleep(.1)
    except KeyboardInterrupt:
        player.pause()
        io.cleanup()


if __name__ == "__main__":
    main()
