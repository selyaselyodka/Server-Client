**adc_temp.py** reads ADC values off of a chosen pin and outputs them in the terminal
server.py is the server-side transmitter on the Raspberry Pi. Uses oneWrieTempReading.py to run (defunct)
rpi_client.py is the client-side receiver for data values. Run this on the laptop you wish to receive data on. Make sure you are connected to the rpi Wifi (romps: password hello)
server_modbus.py is the WIP server-side transmitter on the Raspberry Pi that reads oneWire values from port 240

