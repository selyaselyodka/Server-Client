import multiprocessing
from oneWireTempReading import oneWire_reading_process

if __name__ == '__main__':
    manager = multiprocessing.Manager()
    oneWireTempRegistry = manager.dict()

    # Create two separate processes: 5 secs sample period; save data to oneWireTempRegistry
    sensor_reading = multiprocessing.Process(target=oneWire_reading_process, args=(5, oneWireTempRegistry)) 
    sensor_reading.start()
    
    # Wait for the device cooling process to finish (optional)
    try:
        # Wait for both processes to finish
        sensor_reading.join()
    except KeyboardInterrupt:
        print("Main process interrupted. Terminating child processes...")
        sensor_reading.terminate()
        sensor_reading.join()
        print("Child processes terminated.")
    finally:
        GPIO.cleanup()
