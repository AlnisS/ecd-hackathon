import time
import board
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
from analogio import AnalogIn

analog_in_1 = AnalogIn(board.A1)
analog_in_2 = AnalogIn(board.A2)
analog_in_3 = AnalogIn(board.A3)
analog_in_4 = AnalogIn(board.A4)

i2c_bus = board.I2C()  # uses board.SCL and board.SDA

ina219 = INA219(i2c_bus)


ina219.set_calibration_16V_400mA()

# change configuration to use 32 samples averaging for both bus voltage and shunt voltage
ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S

def get_voltage(pin):
    return (pin.value * 3.3) / 65536

while True:
    current = ina219.current  # current in mA

#     voltage_1 = get_voltage(analog_in_1)
#     voltage_2 = get_voltage(analog_in_2)
#     voltage_3 = get_voltage(analog_in_3)
#     voltage_4 = get_voltage(analog_in_4)

    voltage_1_raw = analog_in_1.value
    voltage_2_raw = analog_in_2.value
    voltage_3_raw = analog_in_3.value
    voltage_4_raw = analog_in_4.value

    solenoid = 0 # not reading switch for now

    error = ""

    if ina219.overflow:
        error += "ina219_math_overflow;"

    if error == "":
        error = "ok"

    sample_time = time.monotonic()

    # note: 1 current read, 4 analog voltage reads, and the extra if statements etc. take 2 ms to execute

    print((sample_time, current, voltage_1_raw, voltage_2_raw, voltage_3_raw, voltage_4_raw, solenoid, error))

#     print("Shunt Current  :{:6.1f} mA".format(current))
#     print("Pressure       :{:4.0f}   psi".format(psi))
#     print("Voltage 1      :{:10.5f} V".format(voltage_1))
#     print("")
#     print((current,psi,voltage_1))

    time.sleep(0.05)
