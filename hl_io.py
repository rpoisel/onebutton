from datetime import datetime
import RPi.GPIO as GPIO
from time import sleep
from threading import Thread


class IoContext(Thread):
    TICK_PERIOD = .1

    def __init__(self):
        super().__init__()
        self.tickables = set()
        GPIO.setmode(GPIO.BCM)
        self.start()
        self.running = True

    def run(self):
        while True:
            for tickable in self.tickables:
                tickable.tick()
            sleep(self.TICK_PERIOD)
            if not self.running:
                break

    def register(self, tickable):
        self.tickables.add(tickable)

    def cleanup(self):
        self.running = False


class Button(object):
    def __init__(self, ctx, pin):
        super().__init__()
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN)
        self.listeners = set()
        self.oldState = bool(GPIO.input(self.pin))
        self.lastChange = datetime.now()

        ctx.register(self)

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


class Led(object):

    def __init__(self, pin):
        super().__init__()
        self.pin = pin
        self.thread = None
        GPIO.setup(self.pin, GPIO.OUT)

    def __del__(self):
        GPIO.cleanup(self.pin)

    def flash(self, period, count):
        if self.thread is None:
            self.period = period
            self.count = count
            self.thread = Thread(target=self.run)
            self.thread.start()

    def on(self):
        GPIO.output(self.pin, GPIO.LOW)

    def off(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def run(self):
        for x in range(0, self.count):
                GPIO.output(self.pin, GPIO.LOW)
                sleep(self.period)
                GPIO.output(self.pin, GPIO.HIGH)
                sleep(self.period)
        self.thread = None
