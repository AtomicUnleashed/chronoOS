# Atomic's modular barebones "chronoOS"
# Released July 11th, 2024
# Feel free to modify as you please, this is your own custom OS after all!

from machine import Pin, I2C, ADC, RTC
from ssd1306 import SSD1306_I2C
from picozero import Pot, Button
import network
import rp2
import sys
import usocket as socket
import ustruct as struct
import time
import utime
import json
import requests
import urequests

# NOTE: ALL NETWORK INFO, LOCATION INFO AND API KEYS HAVE BEEN REPLACES WITH "#" REPLACE WITH OWN INFORMATION!

ssid = "#"
pw = '#'

NTP_HOST = 'pool.ntp.org'

rtc = RTC()

S_WIDTH = 128
S_HEIGHT = 64

menu_select = 0

i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=200000)
oled = SSD1306_I2C(S_WIDTH, S_HEIGHT, i2c)

def gettime():
    def GetTimeNTP():
        NTP_DELTA = 2208988800
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1B
        addr = socket.getaddrinfo(NTP_HOST, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            s.settimeout(10)
            res = s.sendto(NTP_QUERY, addr)
            msg = s.recv(48)
        finally:
            s.close()
        
        ntp_time = struct.unpack("!I", msg[40:44])[0]
        
        return utime.gmtime(ntp_time - NTP_DELTA + (3600 * -4))
    
    def SetTimeRTC():
        tm = GetTimeNTP()
        rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
        
    SetTimeRTC()
    print("TIME RECIEVED:", rtc.datetime())

def connect(ssid, pw):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, pw)
    
    while not wlan.isconnected():
        time.sleep(0.1)

def get_apidata():
    def get_JSON(url):
        reply = requests.get(url)
        content = reply.json()
        reply.close()
        
        return content
    
    #replace these with own api key and location
    city = '#'
    country_code = '#'
    w_api_key = '#'
    
    #ACATS Required Data
    y,m,d,dw,h,mm,sec = rtc.datetime()[0:7]
    
    wdata = get_JSON(str('http://api.openweathermap.org/data/2.5/weather?q=' + city + ',' + country_code + '&APPID=' + w_api_key))
    neo_data = get_JSON(str('https://ssd-api.jpl.nasa.gov/cad.api?dist-max=5LD&date-min=' + str(y) + '-' + str("{:02d}".format(m)) + '-' + str(d) + '&sort=dist&diameter=Y'))
    
    desc = wdata.get('weather')[0].get('main')
    wind = wdata.get('wind').get('speed') * 2.237
    wind_d = wdata.get('wind').get('deg')
    humi = wdata.get('main').get('humidity')
    rawtemp = wdata.get('main').get('temp') - 273.15
    
    tempC = rawtemp
    tempF = (rawtemp * (9 / 5.0) + 32)
    
    astcount = neo_data.get('count')
    
    data = neo_data.get('data')
    
    name_a = data[0][0]
    date_a = data[0][3]
    vel_a = data[0][7]
    dist_a = data[0][4]
    dia_a = data[0][11]
    
    return (name_a, date_a, vel_a, dist_a, dia_a, city, country_code, desc, wind, wind_d, humi, tempC, tempF)

def startup():
    #PLACEHOLDER SPLASH TEXT
    oled.text("Welcome to", 20, 10)
    oled.text("chronoOS", 30, 20)
    oled.text("'Aurora'", 30, 30)
    oled.text("By AT0MIC, 2024", 0, 45)
    oled.show()
    time.sleep(3)

def ms():
    dial = ADC(Pin(26))
    dp = dial.read_u16() / 655.35
    if dp < 20:
        ms = 0
    if dp > 20 and dp < 40:
        ms = 1
    if dp > 40 and dp < 60:
        ms = 2
    if dp > 60 and dp < 80:
        ms = 3
    if dp > 80:
        ms = 4
        
    time.sleep(0.1)
    return ms
    
def main_menu():
    #functionality goes here
    y,m,d,dw,h,mm,sec = rtc.datetime()[0:7]
    wd = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]
    dow = wd[dw]
    
    #permatext
    oled.fill(0)
    oled.text("Menu", 0, 0)
    oled.rect(10, 20, 105, 30, 1)
    oled.rect(8, 18, 109, 34, 1)
    
    #function text
    oled.text(str("{:02d}".format(h)) + ":" + str("{:02d}".format(mm)) + ":" + str("{:02d}".format(sec)), 30, 23)
    oled.text((str("{:02d}".format(m)) + "/" + str("{:02d}".format(d)) + "/" + str(y)), 22, 38)
    
    time.sleep(1)
    oled.show()

def temp_menu():
    #functionality
    adc_sensor = ADC(4)
    tc = 27 - (((adc_sensor.read_u16()) * (3.3 / 65535.0)) - 0.706) / 0.001721
    tf = tc * (9 / 5) + 32
    tk = tc + 273.15
    
    #permatext
    oled.fill(0)
    oled.text("Nearby Temp.", 0, 0)
    
    #function text
    oled.text(str("> " + "{:.2f}".format(tc) + "C"), 5, 15)
    oled.text(str("> " + "{:.2f}".format(tf) + "F"), 5, 30)
    oled.text(str("> " + "{:.2f}".format(tk) + "K"), 5, 45)
    
    time.sleep(1)
    oled.show()

def weather_menu(c, cc, de, wi, wd, hi, tc, tm):

    #functionality
    dire = 'NULL'
    
    if wd >= 0 and wd <= 23 and wd >= 337 and wd <= 360:
        dire = 'N'
    elif wd >= 24 and wd <= 68:
        dire = 'NE'
    elif wd >= 69 and wd <= 113:
        dire = 'E'
    elif wd >= 114 and wd <= 158:
        dire = 'SE'
    elif wd >= 159 and wd <= 203:
        dire = 'S'
    elif wd >= 204 and wd <= 248:
        dire = 'SW'
    elif wd >= 249 and wd <= 293:
        dire = 'W'
    elif wd >= 294 and wd <= 336:
        dire = 'NW'
    
    if wd == 0:
        dire = 'N'
    
    #permatext
    oled.fill(0)
    oled.text("Weather", 0, 0)
    
    #draw graphics
    oled.rect(61, 0, 66, 54, 1)
    
    #function text
    oled.text(de, 3, 40)
    oled.text("WS: " + str(int(wi)) + 'mph', 62, 3)
    oled.text('WD: ' + dire, 62, 13)
    oled.text('HU: '+ str(hi) + '%', 62, 23)
    oled.text(str("{:.2f}".format(tc)) + 'C', 62, 33)
    oled.text(str("{:.2f}".format(tm)) + 'F', 62, 43)
    
    time.sleep(1)
    oled.show()

def iss_menu():
    def get_JSON(url):
        reply = requests.get(url)
        content = reply.json()
        reply.close()
        
        return content
    
    #functionality
    iss_data = get_JSON('https://api.wheretheiss.at/v1/satellites/25544')
    
    long = iss_data.get('longitude')
    lat = iss_data.get('latitude')
    alt = iss_data.get('altitude')
    velo = iss_data.get('velocity')
    
    #permatext
    oled.fill(0)
    oled.text("ISS Tracker", 0, 0)
    
    #function text
    oled.text("> Lat: " + str("{:.3f}".format(lat)), 5, 15)
    oled.text("> Lon: " + str("{:.3f}".format(long)), 5, 25)
    oled.text("> Alt: " + str("{:.2f}".format(alt)) + "km", 5, 35)
    oled.text("> Vel: " + str(int(velo)) + "m/s", 5, 45)
    
    time.sleep(1)
    oled.show()

def ACATS_menu(na, da, va, dia, diaa):
    #permatext
    oled.fill(0)
    oled.text("A.C.A.T.S.", 0, 0)
    
    eta = da.split(" ", 1)
    
    #function text
    oled.text("Name: " + na, 0, 15)
    oled.text("ETA: " + eta[0], 0, 25)
    oled.text("Vel: " + str("{:.2f}".format(float(va))) + "km/s", 0, 35)
    oled.text("Dist: " + str("{:.0f}".format(float(dia) * 149597870.691)) + "km", 0, 45)
    
    oled.show()

# run once - IMPORTANT FOR NETWORK/PROCESSOR/APIs
startup()
connect(ssid, pw)
gettime()
na, da, va, dia, diaa, c, cc, de, wi, wd, hi, tc, tf = get_apidata()

while True:
    menu_select = ms()
    
    if menu_select == 0:
        main_menu()
    elif menu_select == 1:
        temp_menu()
    elif menu_select == 2:
        weather_menu(c, cc, de, wi, wd, hi, tc, tf)
    elif menu_select == 3:
        iss_menu()
    elif menu_select == 4:
        ACATS_menu(na, da, va, dia, diaa)
