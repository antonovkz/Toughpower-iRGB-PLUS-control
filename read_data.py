import time
from pywinusb import hid
import math

# Device Constants
VID = 0x264a  # Replace with your power supply's Vendor ID
PID = 0x2329  # Replace with your power supply's Product ID

def send_command(device, cmd):
    reports = device.find_output_reports()
    if not reports:
        print("No available reports for sending.")
        return False

    report = reports[0]
    report_id = report.report_id

    data = [report_id] + cmd + [0x00] * (64 - len(cmd))

    if len(data) != 65:
        print(f"Error: Data length is {len(data)} bytes, expected 65 bytes.")
        return False

    # print(f"\nSending command: {data}")

    report.send(data)
    return True

def read_response(device, timeout=0.1):
    response = []

    def data_handler(data):
        nonlocal response
        response.extend(data)
        # print(f"Data received: {data}")

    device.set_raw_data_handler(data_handler)
    time.sleep(timeout)
    device.set_raw_data_handler(None)

    return response

def get_data(device, b):
    # Send command [0x31, b]
    cmd = [0x31, b]
    # print(f"\nRequesting data for parameter: 0x{b:02X}")
    if not send_command(device, cmd):
        return float('nan')
    
    # Read response
    response = read_response(device)
    if response and len(response) >= 5:
        # print(f"Device response for parameter 0x{b:02X}: {response}")
        # Skip the first 3 bytes, take the next 2 bytes
        bytes_data = response[3:5]
        # print(f"Data bytes: {bytes_data}")
        # Combine bytes into a value
        value = (bytes_data[1] << 8) | bytes_data[0]
        exponent = (value & 0x7800) >> 11
        sign = (value & 0x8000) >> 15
        fraction = value & 0x07FF

        # print(f"value: {value}, exponent: {exponent}, sign: {sign}, fraction: {fraction}")

        if sign == 1:
            exponent -= 16

        result = (2.0 ** exponent) * fraction
        # print(f"Result for parameter 0x{b:02X}: {result}")
        return result
    else:
        print(f"Failed to get a valid response for parameter 0x{b:02X}")
        return float('nan')

def main():
    all_hids = hid.HidDeviceFilter(vendor_id=VID, product_id=PID).get_devices()
    if not all_hids:
        print("Device not found.")
        return

    device = all_hids[0]
    device.open()

    try:
        # print("Device connected.")

        # Retrieve data
        vin = get_data(device, 0x33)
        vvOut12 = get_data(device, 0x34)
        vvOut5 = get_data(device, 0x35)
        vvOut33 = get_data(device, 0x36)
        viOut12 = get_data(device, 0x37)
        viOut5 = get_data(device, 0x38)
        viOut33 = get_data(device, 0x39)
        temp = get_data(device, 0x3A)
        fanRpm = get_data(device, 0x3B)

        # Adjust units if necessary, e.g., divide voltage values by 1000 if too large

        watts = 0
        if not math.isnan(vvOut12) and not math.isnan(viOut12):
            watts += vvOut12 * viOut12
        if not math.isnan(vvOut5) and not math.isnan(viOut5):
            watts += vvOut5 * viOut5
        if not math.isnan(vvOut33) and not math.isnan(viOut33):
            watts += vvOut33 * viOut33

        # Display data
        print(f"Power supply temperature: {temp} °C")
        print(f"Fan speed: {fanRpm} RPM")
        print(f"VIN: {vin} V")
        print(f"12V Output Voltage: {vvOut12} V")
        print(f"12V Output Current: {viOut12} A")
        print(f"5V Output Voltage: {vvOut5} V")
        print(f"5V Output Current: {viOut5} A")
        print(f"3.3V Output Voltage: {vvOut33} V")
        print(f"3.3V Output Current: {viOut33} A")
        print(f"Power consumption: {watts} W")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        device.close()
        # print("Device disconnected.")

if __name__ == "__main__":
    main()
