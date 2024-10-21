import time
from pywinusb import hid

# Device Constants
VID = 0x264a  # Replace with your power supply's Vendor ID
PID = 0x2329  # Replace with your power supply's Product ID
SET_RGB_OFF_CMD = [0x30, 0x42, 0x19, 0x00, 0x00, 0x00]

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

    report.send(data)
    return True

def main():
    all_hids = hid.HidDeviceFilter(vendor_id=VID, product_id=PID).get_devices()
    if not all_hids:
        print("Device not found.")
        return

    device = all_hids[0]
    device.open()

    try:
        print("Device connected.")
        if not send_command(device, SET_RGB_OFF_CMD):
            device.close()
            return
        print("RGB lighting off command sent.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        device.close()
        print("Device disconnected.")

if __name__ == "__main__":
    main()
