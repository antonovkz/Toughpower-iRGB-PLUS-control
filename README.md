
# Fan Control and Monitoring Scripts for Thermaltake Toughpower iRGB PLUS PSU

This repository contains Python scripts for controlling and monitoring a power supply unit (PSU) via HID USB. Each script has a specific function, ranging from adjusting fan modes to reading key performance metrics like temperature, voltage, and current. These tools are useful for anyone looking to manage the cooling and performance of their PSU or monitor its operational status.

## Scripts Overview

### 1. `fan_auto.py`
This script automatically adjusts the PSU fan speed based on the current temperature. It continuously monitors the PSU temperature and adjusts the fan's speed proportionally. If the temperature is below a set threshold, the fan remains off (passive mode), but if it exceeds this limit, the fan turns on and speeds up as needed.

**Features:**
- Automatic fan activation and speed control based on temperature.
- Passive mode when the temperature is below a defined threshold.
- Dynamic speed adjustment to maintain optimal cooling.

### 2. `fan_speed_control.py`
This script allows manual control over the PSU fan mode via the command line. Users can choose between several fan modes:
- **Silent:** Low-speed, quiet operation.
- **Performance:** High-speed, more cooling.
- **Passive:** Fan off unless a critical temperature is reached.
- **Manual:** Set the fan speed to a specific percentage.

**Features:**
- Flexible fan mode selection via command-line arguments.
- Manual control over fan speed in `manual` mode.

### 3. `read_data.py`
This script retrieves and displays various operational parameters of the PSU, such as:
- Input and output voltages for 12V, 5V, and 3.3V rails.
- Output currents for each of these rails.
- PSU temperature and fan speed.
- Total power consumption (calculated from the voltages and currents).

**Features:**
- Real-time monitoring of key PSU metrics.
- Calculation of total power consumption.

## Requirements

- Python 3.x
- `pywinusb` library (`pip install pywinusb`)
- Compatible PSU with HID USB support (ensure to replace the Vendor ID (VID) and Product ID (PID) with your specific device's details)

## Usage

### 1. Automatic Fan Control
To run the automatic fan control script, execute:
```bash
python fan_auto.py
```
The script will start monitoring the PSU temperature and adjust the fan speed accordingly.

### 2. Manual Fan Mode Control
To manually control the fan mode, use:
```bash
python fan_speed_control.py --mode <mode> [--speed <value>]
```

**Options:**
- `<mode>`: Choose from `silent`, `performance`, `passive`, `manual`
- `--speed <value>`: Set fan speed in percentage (0-100) for `manual` mode. Required when `--mode manual` is used.

**Examples:**
- Set fan to silent mode:
  ```bash
  python fan_speed_control.py --mode silent
  ```
- Set fan to 75% speed in manual mode:
  ```bash
  python fan_speed_control.py --mode manual --speed 75
  ```
  - Set fan to passive mode:
  ```bash
  python fan_speed_control.py --mode passive
  ```

### 3. PSU Monitoring
To monitor the PSU and retrieve all relevant metrics, run:
```bash
python read_data.py
```
The script will display the current temperature, fan speed, voltages, currents, and calculate power consumption.

## Customization

Before using these scripts, make sure to modify the `VID` and `PID` constants to match your specific power supply's Vendor ID and Product ID.

## Notes

- Make sure your PSU is connected to the computer and detected correctly.
- Running these scripts may require administrative privileges, depending on your system configuration.
- Use the scripts responsibly to avoid setting unsafe fan speeds or modes.

## Troubleshooting

- If you encounter issues with the scripts not detecting the PSU, ensure the correct VID and PID are set.
- Verify that the `pywinusb` library is installed and compatible with your Python version.
- Ensure that your PSU is compatible with HID USB communication.
