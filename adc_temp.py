import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)

diff = AnalogIn(ads, ADS.P0, ADS.P1)

def calculate_thermal_resistance(r1,r2,r3,vs,g):
    g = -g
    top = (r1*r3)+((g/vs)*(r1+r2)*r3)
    bottom = r2 - ((g/vs)*(r1+r2))
    return top/bottom

def calculate_temperature(rt):
    coeff = [(-5.775*(10**-5)),0.39083,100-rt]
    return np.roots(coeff)

while True:
    print(f"Voltage Diff:{diff.voltage}V")
    rt = calculate_thermal_resistance(1167,1176,1185,3.256,diff.voltage)
    print(f"{rt} Ohms")
    temp = calculate_temperature(rt)
    print(f"{temp[1]} C")
    time.sleep(1)
