import argparse
import time
from pywinusb import hid

VID = 0x264a
PID = 0x2329

def percent_to_param2(percent):
    if percent <= 0:
        return 0
    elif percent >= 100:
        return 100
    else:
        param2 = 9 + int(((percent - 1) / 99) * 91)
        return param2

def send_command(device, cmd):
    reports = device.find_output_reports()
    if not reports:
        print("No available reports for sending.")
        return False

    report = reports[0]
    report_id = report.report_id

    data = [report_id] + cmd + [0x00] * (64 - len(cmd))

    if len(data) != 65:
        return False

    report.send(data)
    return True

def main():
    parser = argparse.ArgumentParser(description='Control the operating mode of the power supply fan.')
    parser.add_argument('--mode', choices=['silent', 'performance', 'passive', 'manual'], required=True,
                        help='Fan operating mode: silent, performance, passive, manual.')
    parser.add_argument('--speed', type=float,
                        help='Fan speed in percent (0-100) for manual mode.')
    args = parser.parse_args()
    

    mode = args.mode
    param1 = None
    param2 = 0x00

    if mode == 'silent':
        param1 = 0x01
    elif mode == 'performance':
        param1 = 0x02
    elif mode == 'passive':
        param1 = 0x03
    elif mode == 'manual':
        param1 = 0x04
        if args.speed is None:
            print("Error: In manual mode, you must specify the speed using the --speed parameter.")
            return
        desired_percent = args.speed
        if desired_percent < 0 or desired_percent > 100:
            print("Error: Enter a speed value between 0 and 100.")
            return
        param2 = percent_to_param2(desired_percent)
    else:
        print("Error: Unknown mode.")
        return

    print(f"Selected mode: {mode}")
    print(f"Param1: {param1}, Param2: {param2}")

    SET_FAN_MODE_CMD = [0x30, 0x41, param1, param2]

    all_hids = hid.HidDeviceFilter(vendor_id=VID, product_id=PID).get_devices()
    if not all_hids:
        print("Device not found.")
        return

    device = all_hids[0]
    device.open()

    try:
        print("Device connected.")
        if not send_command(device, SET_FAN_MODE_CMD):
            device.close()
            return

        if mode == 'manual':
            print(f"Fan speed set to {desired_percent}%.")
        elif mode == 'silent':
            print("Silent fan mode enabled.")
        elif mode == 'performance':
            print("Performance fan mode enabled.")
        elif mode == 'passive':
            print("Fan turned off (passive mode).")

        time.sleep(0.1)

        print("Command sent.")
        print("Done.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        device.close()
        print("Device disconnected.")

if __name__ == "__main__":
    main()
