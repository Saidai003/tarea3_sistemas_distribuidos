import json
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from browsermobproxy import Server
from requests.exceptions import MissingSchema
import requests
import timeit
import time
import folium
import subprocess
import platform
import os
from datetime import datetime

print("""Waze Traffic and Accident Scraper

Waze Traffic and Accident Scraper will open the Mozilla Firefox browser, onto Waze's live map website.\n
It'll scrape all the traffic incidents and accidents from your preferred location,\n
by moving the mouse to that location.\n
Every incident or accident that is scraped also has its own dataset, including its geographic location,\n
the number of upvotes from Waze users, confidence, and reliability, by Waze itself.\n
You can view all that in the map that will be generated after the program finished scraping.\n

Instructions:

Choose how much seconds do you want the program to scrape traffic incidents and accidents. That time is for the user to move to another location,
to scrape traffic incidents reported by Waze's users.\n
If you press Enter, without entering any number, the number will be the default, 5 seconds, which is also the recommended value.
After the Firefox browser launched and you're done scraping, just close the browser, and wait 5 seconds.
After that, go to localhost:5000 or 127.0.0.1:5000 and you'll be presented with a map showing all the scraped traffic incidents and accidents,
and by clicking on them you'll be able to see more information like coordinates, type of incident, number of upvotes, confidence and reliability.\n
Also, you can download the scraped data as JSON, XLS (Excel), and CSV.
""")

def directory_exist(file_type):
    return os.path.isdir('./{}'.format(file_type))

def clear_screen():
    if platform.system() == "Windows":
        subprocess.Popen("cls", shell=True).communicate()
    else:  # Linux and Mac
        print("\033c", end="")

def save_config():
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_name = "config.config"
    with open(file_name, "w") as f:
        f.write(date)

def personalised_info():
    auto_or_manual = input("Do you want the software to scrape the waze map Automatically? (Answer with 'a') ")
    sec = input("Every how much seconds do you want the scraper to scrape the data? maximum is 30 seconds, while minimum is 5 seconds. By not inputting anything the value will be set to the recommended value of 5 seconds. ")
    save_config()
    return auto_or_manual, sec

def start_server():
    global server, proxy, driver
    server = Server("path/to/browsermob-proxy")
    server.start()
    proxy = server.create_proxy()

    profile = webdriver.FirefoxProfile()
    profile.set_proxy(proxy.selenium_proxy())
    driver = webdriver.Firefox(executable_path="path/to/geckodriver", firefox_profile=profile)
    driver.get("https://www.waze.com/livemap?utm_source=waze_website&utm_campaign=waze_website")

    return driver

urls = []
count = 1
good_index = []
data_parsed = {}
inner_nested_data_parsed = {}
data_list = []
key_counts_with_subtype = []

def get_data(sec):
    global count, inner_nested_data_parsed
    start = timeit.timeit()
    har = proxy.new_har("waze_{0}".format(count))
    har = str(har)
    str_1 = "https://www.waze.com/il-rtserver/web/TGeoRSS?"
    str_2 = "&types=alerts%2Ctraffic%2Cusers"
    indx_1 = har.find(str_1)
    indx_2 = har.find(str_2)
    url = har[indx_1:indx_2] + str_2
    urls.append(url)

    for d in urls:
        if d == str_2:
            print("Please move to your preferred location.")
            urls.remove(d)
            pass
        else:
            data = requests.get(url).text
            if not "DOCTYPE" in data:
                data = json.loads(data)
                end = timeit.timeit()
                print("Time Taken to fetch the data: {} seconds".format(end - start))
                urls.remove(d)
                for x in range(len(data["alerts"])):
                    if data["alerts"][x]["type"] in ["ACCIDENT", "TRAFFIC"]:
                        good_index.append(x)
                for x in good_index:
                    inner_nested_data_parsed["type_"] = (data["alerts"][x]["type"])
                    if data["alerts"][x]["subtype"]:
                        inner_nested_data_parsed["subtype"] = (data["alerts"][x]["subtype"])
                    else:
                        pass
                    inner_nested_data_parsed["country"] = (data["alerts"][x]["country"])
                    inner_nested_data_parsed["nThumbsUp"] = (data["alerts"][x]["nThumbsUp"])
                    inner_nested_data_parsed["confidence"] = (data["alerts"][x]["confidence"])
                    inner_nested_data_parsed["reliability"] = (data["alerts"][x]["reliability"])
                    inner_nested_data_parsed["location_x"] = (data["alerts"][x]["location"]["x"])
                    inner_nested_data_parsed["location_y"] = (data["alerts"][x]["location"]["y"])
                    data_parsed[count] = inner_nested_data_parsed
                    data_list.append(data_parsed)
                    inner_nested_data_parsed = {}
                    count += 1
            else:
                print("Data is inaccessible, wait {} seconds to try again.".format(sec))
    print("Scraped {} incidents.".format(count - 1))
    return data_list

def map(key_counts_with_subtype, data_list):
    global data_parsed

    location_x_start = data_list[0][1]["location_x"]
    location_y_start = data_list[0][1]["location_y"]

    m = folium.Map(location=[location_y_start, location_x_start], zoom_start=12, smooth_factor=2)

    tooltip = 'Incident Type' 

    for x in data_list:
        for key in x.keys():
            try:
                if data_list[0][key]["subtype"]:
                    key_counts_with_subtype.append(key)
            except KeyError:
                pass

    for iter_2 in range(len(data_list)):
        data_parsed = data_list[iter_2]
    for key_count in range(1, len(data_parsed) + 1):
        try:
            if key_count == key_counts_with_subtype[key_count - 1]:
                subtype = data_parsed[key_count]["subtype"]
            else:
                type_ = data_parsed[key_count]["type_"]
        except IndexError:
            type_ = data_parsed[key_count]["type_"]

        country = data_parsed[key_count]["country"]
        nThumbsUp = data_parsed[key_count]["nThumbsUp"]
        confidence = data_parsed[key_count]["confidence"]
        reliability = data_parsed[key_count]["reliability"]
        location_x = data_parsed[key_count]["location_x"]
        location_y = data_parsed[key_count]["location_y"]

        string = '<i>type: <b>{0}</b>\ncountry: <b>{1}</b>\nnThumbsUp: <b>{2}</b>\nconfidence: <b>{3}</b>\nreliability: <b>{4}</b>\nlocation x: <b>{5}</b>\nlocation y: <b>{6}</b></i>'.format(
            type_, country, nThumbsUp, confidence, reliability, location_x, location_y)

        folium.Marker([location_y, location_x], popup=folium.Popup(string, max_width=450), tooltip=tooltip).add_to(m)

    m.save('templates//map.html')

def start_script():
    if not directory_exist("json"):
        os.mkdir('json')
    auto_or_manual, sec = personalised_info()
    err = False
    if auto_or_manual == "A" or auto_or_manual == "a":
        if sec.isdigit():
            driver = start_server()
            while not err:
                try:
                    time.sleep(int(sec))
                    data_list = get_data(sec)
                    with open("data - its not the json data.txt", "w", encoding="utf-8") as f:
                        f.write(str(data_list))
                except (WebDriverException, MissingSchema):
                    err = True
                    if data_list:
                        print("Done scraping... Generating map..")
                        map(key_counts_with_subtype, data_list)
                        clear_screen()
                    else:
                        print(
                            "You didn't scrape anything. One possible explanation is that you didn't move with the mouse at all, or you closed the browser before the site completely loaded and the program didn't begin to scrape.")
                        exit()
    else:
        print("Exiting the program.")
        exit()

if __name__ == "__main__":
    start_script()
