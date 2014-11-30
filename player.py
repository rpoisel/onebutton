#!env python3

from hl_io import Button, Listener, Led
from time import sleep


class Player(Listener):
    PAUSE = 1  # state
    PLAY = 2  # state

    HOLD_PERIOD = 2  # seconds

    def __init__(self):
        super().__init__()
        self.state = self.PLAY
        self.reset = True

    def r_trig(self, diff):
        self.reset = True

    def f_trig(self, diff):
        if diff < self.HOLD_PERIOD:
            self.state = self.PLAY if self.state is self.PAUSE else self.PAUSE
            if self.state is self.PLAY:
                print("PLAY")
            else:
                print("PAUSE")

    def hold(self, diff, value):
        if value is True and diff >= self.HOLD_PERIOD and self.reset is True:
            self.reset = False
            print("TRACK BACK")


def main():
    b = Button(24)
    b.addButtonListener(Player())
    green = Led(22)
    red = Led(23)

    try:
        while True:
            green.flash(.1, 5)
            red.flash(.2, 3)
            sleep(.1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
