# chronoOS
![WATCH(2)](https://github.com/AtomicUnleashed/chronoOS/assets/159086295/9f50cede-0516-4985-88e9-4de3dccc027b)


Atomic's Modular Operating System for any barebones, Pi Pico W powered smartwatch.

Released July 11th, 2024.

Features:

ACATS
  Asteroid Close Approach Tracking System

  - Using JPL's ssd API, can give a heads up on the closest asteroid passing within 5 lunar distances.
  - Gives Name, Date of Approach, Velocity, and Approach Distance.

ISS Tracker

  - Using the WhereTheISS API, it give live data on the ISS wherebouts.
  - Gives Altitude, Latitude, Longitude, and Velocity.
  - Requires Constant Internet Connection.

Local Weather Station

  - Using the OpenWeatherMap API, gives local weather information along with a brief description of the weather.
  - Gives Wind Information and Outside Air Tempreture & Humidity in both Imperial and Metric Units.

Local Tempreture Sensor

  - Using the Pi Pico's onboard Tempreture Sensor, gives live readings of the tempreture in the area around you.
  - Gives the tempreture around you in Fahrenheit, Celsius, and Kelvin.

Hardware Dependencies

  - At minimum, all you need is a Pi Pico W, 128x64 SSH1306 OLED, and 10K Ohm Potentiometer.

Software Dependencies

  - Requests, SSD1306 Driver(https://github.com/stlehmann/micropython-ssd1306), JSON.
  - Everything else is modular, chronoOS is designed to be modified to your specifications!
