from datetime import datetime
import RPi.GPIO as GPIO
from time import sleep
from threading import Thread


class IOContext(Thread):
    TICK_PERIOD = .1

    def __init__(self):
        super().__init__()
        self.tickables = set()
        GPIO.setmode(GPIO.BCM)
        self.start()

    def run(self):
        while True:
            for tickable in self.tickables:
                tickable.tick()
            sleep(self.TICK_PERIOD)

    def register(self, tickable):
        self.tickables.add(tickable)

io = IOContext()


class Button(object):
    def __init__(self, pin):
        super().__init__()
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN)
        self.listeners = set()
        self.oldState = bool(GPIO.input(self.pin))
        self.lastChange = datetime.now()

        io.register(self)

    def addButtonListener(self, listener):
        self.listeners.add(listener)

    def tick(self):
        curState = bool(GPIO.input(self.pin))
        diff = (datetime.now() - self.lastChange).total_seconds()
        if self.oldState is not curState:
            self.lastChange = datetime.now()
            for listener in self.listeners:
                if curState is True:
                    listener.r_trig(diff)
                else:
                    listener.f_trig(diff)
        else:
            for listener in self.listeners:
                listener.hold(diff, curState)
        self.oldState = curState


class Listener(object):

    def r_trig(self, diff):
        assert 0, "r_trig() not implemented"

    def f_trig(self, diff):
        assert 0, "f_trig() not implemented"

    def hold(self, diff, value):
        assert 0, "hold() not implemented"
