import os
import glob
import time

class Thermometers:
    
    def __init__(self) -> None:
        # Load the 1-wire GPIO and thermal modules into the kernel
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        # Set the base directory for 1-wire devices and list the folders for temperature sensors
        base_dir = '/sys/bus/w1/devices/'
        device_folders = glob.glob(base_dir + '28*')  # 28* is the device ID prefix for temperature sensors

        if device_folders:
            # Construct the path to the sensor data file for each device
            self.deviceFolders = [device_folder + '/w1_slave' for device_folder in device_folders]
        else:
            # Raise an error if no sensors are found
            raise RuntimeError("No temperature sensors found!")

    def readRawTemp(self, device_file):
        # Read the raw data from the sensor's data file
        with open(device_file, 'r') as f:
            return f.readlines()

    def readTempCelcius(self, device_file):
        # Read the raw temperature data until it confirms that it's valid (ends with 'YES')
        lines = self.readRawTemp(device_file)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.05)  # Wait briefly before reading again
            lines = self.readRawTemp(device_file)

        # Extract the temperature data (in millidegrees) from the second line
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]  # Get the temperature string after 't='
            return float(temp_string) / 1000.0  # Convert millidegrees to degrees Celsius
        return None  # Return None if temperature data could not be found

    def readAllTemperatures(self):
        # Read temperatures from all connected sensors and return as a dictionary
        temperatures = {}
        for device_file in self.deviceFolders:
            try:
                # Attempt to read the temperature from the sensor
                temp_celsius = self.readTempCelcius(device_file)
                # Store temperature or error message if the read fails
                temperatures[device_file] = temp_celsius if temp_celsius is not None else "Error reading temperature"
            except Exception as e:
                # Store the exception message if an error occurs
                temperatures[device_file] = str(e)
        return temperatures

# Main sensor reading function
def oneWire_reading_process(sample_time: float, registry: dict):
    # Create an instance of the Thermometers class to interact with the sensors
    Sensors = Thermometers()

    try:
        while True:
            start_time = time.time()  # Record the start time of the loop

            # Get all sensor data and save them to the external registry
            allTemperatures = Sensors.readAllTemperatures()
            registry.clear()  # Clear the registry before updating it with new data
            registry.update(allTemperatures)  # Update the registry with the latest temperature readings

            # Print out the temperature data from each sensor
            for sensor, temperature in allTemperatures.items():
                print("Sensor {} temperature: {}".format(sensor, temperature))

            # Calculate the time taken for the sensor reading loop
            elapsed_time = time.time() - start_time
            remaining_time = sample_time - elapsed_time  # Ensure the total loop time matches sample_time seconds

            # If there is remaining time, sleep to maintain the desired sample interval
            if remaining_time > 0:
                time.sleep(remaining_time)
            else:
                # Warn if sensor reading takes longer than the sample time
                print("Warning: Sensor reading took longer than {} seconds, increase the interval to solve this.".format(sample_time))
        
    except Exception as e:
        # Print the exception message if an error occurs during the loop
        print("An error occurred: {}".format(e))
