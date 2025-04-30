from oneWireTempReading import Thermometers
import time

Sensors = Thermometers()

while True:
    inp = raw_input()
    if inp == "":
        break

    current_second = datetime.datetime.now().second
    if current_second%2 == 0:
        allTemperatures = Sensors.readAllTemperatures()
        print(allTemperatures)
