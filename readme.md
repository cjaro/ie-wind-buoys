# Wind Speed Table Reference Problem

1. Reference an online table that contains coordinates of a buoy 
  
    a. Table can be found at https://www.marine.ie/site-area/data-services/real-time-observations/irish-weather-buoy-network-imos
  
2. Read data associated with buoy table
3. Accept coordinates (parsed from location from user input)
4. Reference nearest buoy data, return wind speed

## How to run this project

1. Set up a virtual environment & activate it:
```commandline
$ python3 -m venv my-venv
$ source my-venv/bin/activate
```
2. Install dependencies
```commandline
pip install -r requirements.txt
```
3. Run the script
```commandline
python3 main.py
```