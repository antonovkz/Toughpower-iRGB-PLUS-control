import time
from pywinusb import hid
import math

VID = 0x264a
PID = 0x2329

MIN_TEMP = 37.0            # Temperature at which the fan turns on
MAX_TEMP = 59.0            # Temperature at which the fan reaches maximum speed
MIN_FAN_SPEED_PERCENT = 20.0   # Minimum fan speed in percent
MAX_FAN_SPEED_PERCENT = 50.0  # Maximum fan speed in percent
SLEEP_TIMEOUT = 15             # Interval between temperature checks in seconds
PASSIVE_DELTA = 3.0           # Temperature difference to return to passive mode

def send_command(device, cmd):
    reports = device.find_output_reports()
    if not reports:
        print("No available reports for sending.")
        return False
    report = reports[0]
    report_id = report.report_id
    data = [report_id] + cmd + [0x00] * (64 - len(cmd))
    if len(data) != 65:
        print("Error: The length of the data to be sent is not equal to 65 bytes.")
        return False
    report.send(data)
    return True

def read_response(device, timeout=0.1):
    response = []
    def data_handler(data):
        nonlocal response
        response.extend(data)
    device.set_raw_data_handler(data_handler)
    time.sleep(timeout)
    device.set_raw_data_handler(None)
    return response

def get_data(device, b):
    cmd = [0x31, b]
    if not send_command(device, cmd):
        return float('nan')
    response = read_response(device)
    if response and len(response) >= 5:
        bytes_data = response[3:5]
        value = (bytes_data[1] << 8) | bytes_data[0]
        exponent = (value & 0x7800) >> 11
        sign = (value & 0x8000) >> 15
        fraction = value & 0x07FF
        if sign == 1:
            exponent -= 16
        result = (2.0 ** exponent) * fraction
        return result
    else:
        return float('nan')

def percent_to_param2(percent):
    if percent <= 0:
        return 0
    elif percent >= 100:
        return 100
    else:
        param2 = 9 + int(((percent - 1) / 99) * 91)
        return param2

def temp_to_fan_speed_percent(temp):
    if temp <= MIN_TEMP:
        return MIN_FAN_SPEED_PERCENT
    elif temp >= MAX_TEMP:
        return MAX_FAN_SPEED_PERCENT
    else:
        fan_speed_percent = ((temp - MIN_TEMP) / (MAX_TEMP - MIN_TEMP)) * (MAX_FAN_SPEED_PERCENT - MIN_FAN_SPEED_PERCENT) + MIN_FAN_SPEED_PERCENT
        return fan_speed_percent

def main():
    all_hids = hid.HidDeviceFilter(vendor_id=VID, product_id=PID).get_devices()
    if not all_hids:
        print("Device not found.")
        return
    device = all_hids[0]
    device.open()
    try:
        print("Device connected.")
        fan_active = False
        while True:
            temp = get_data(device, 0x3A)
            fanRpm = get_data(device, 0x3B)

            if math.isnan(temp) or temp < 20.0:
                print("Failed to get temperature.")
                time.sleep(SLEEP_TIMEOUT)
                continue
            print(f"Power supply temperature: {temp:.2f} °C")
            print(f"Fan speed: {fanRpm:.2f} RPM")

            if not fan_active:
                if temp >= MIN_TEMP:
                    fan_active = True
                    print("Turning on the fan.")
            else:
                if temp <= (MIN_TEMP - PASSIVE_DELTA):
                    fan_active = False
                    print("Switching to passive mode.")

            if fan_active:
                fan_speed_percent = temp_to_fan_speed_percent(temp)
                param1 = 0x04
                param2 = percent_to_param2(fan_speed_percent)
                mode_description = f'Fan speed: {fan_speed_percent:.2f}%'
            else:
                param1 = 0x03
                param2 = 0x00
                mode_description = 'Passive mode'

            SET_FAN_MODE_CMD = [0x30, 0x41, param1, int(param2)]
            if not send_command(device, SET_FAN_MODE_CMD):
                print("Failed to send command.")
            else:
                print(f"Mode set: {mode_description}")
            time.sleep(SLEEP_TIMEOUT)
    except KeyboardInterrupt:
        print("User interruption.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        device.close()
        print("Device disconnected.")

if __name__ == "__main__":
    main()
