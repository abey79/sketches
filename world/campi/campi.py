"""This is part of the Automatic #plotloop Machine project.

Details: https://bylr.info/articles/2022/12/22/automatic-plotloop-machine/
"""

import RPi.GPIO as GPIO
from fastapi import FastAPI
from fastapi.responses import FileResponse
from picamera2 import Picamera2
from RpiMotorLib import RpiMotorLib

app = FastAPI()

# Initialize the motor
PIN_ENABLE = 5
PIN_MS1 = 6
PIN_MS2 = 13
PIN_DIR = 26
PIN_STEP = 19

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_ENABLE, GPIO.OUT, initial=GPIO.HIGH)
GPIO.output(PIN_ENABLE, GPIO.HIGH)
motor_control = RpiMotorLib.A3967EasyNema(PIN_DIR, PIN_STEP, (PIN_MS1, PIN_MS2))

# Initialize the camera
picam2 = Picamera2()
still_config = picam2.create_still_configuration(controls={"ExposureValue": 0})
picam2.configure(still_config)
picam2.start()


@app.get("/img/")
def get_picture(ev: int = 0):
    picam2.set_controls({"ExposureValue": ev})
    array = picam2.capture_file("/tmp/temp.jpg")
    return FileResponse("/tmp/temp.jpg", media_type="image/png")


@app.get("/motor/{cm}")
def run_motor(cm: int):
    GPIO.output(PIN_ENABLE, GPIO.LOW)
    kwargs = dict(
        stepdelay=0.005,
        steps=round(17.9 * cm),
        clockwise=True,
        verbose=False,
        steptype="Full",
        initdelay=0.05,
    )
    motor_control.motor_move(**kwargs)
    GPIO.output(PIN_ENABLE, GPIO.HIGH)
    return kwargs


@app.on_event("shutdown")
def shutdown_event():
    GPIO.cleanup()
