# This code is a web automation tool that scrapes the local bitcoin volume data from coindance website

from selenium import webdriver
from selenium.webdriver.common.by import By

import time


driver = webdriver.Chrome()

# Navigate to the website
driver.get('https://coin.dance/volume/localbitcoins')
	
div_elements = driver.find_elements("css selector", '.col-sm-12.col-lg-6 a')
# Extract href from each link
urls = [element.get_attribute('href') for element in div_elements]

for url in urls:
    # print(url)

    driver.get(url)
    time.sleep(2)  # 2 seconds delay
   
    # <g class="raphael-group-19-toolbar-master"><g class="raphael-group-24-toolbar"><rect fill-opacity="0" fill="#eeeeee" stroke="#eeeeee" stroke-opacity="0" stroke-width="1" width="22.25" height="22.25" x="547.75" y="6" ry="0" rx="0"></rect><g class="raphael-group-26-button" stroke-linecap="round"><rect x="550.5" y="8.5" width="17" height="17" ry="2.3" rx="2.3" fill="#ffffff" stroke="#bbbbbb" stroke-width="1" stroke-opacity="1" fill-opacity="1"></rect><path d="M554.8,17L563.2,17M554.8,20L563.2,20M554.8,14L563.2,14" fill="#ffffff" stroke="#9a9a9a" stroke-linecap="round" fill-opacity="1" stroke-opacity="1" stroke-width="1"></path><rect x="550.5" y="8.5" width="17" height="17" ry="2.3" rx="2.3" fill="#c0c0c0" stroke="#c0c0c0" fill-opacity="0.000001" stroke-opacity="0.000001" stroke-width="1" style="cursor: pointer;"></rect></g></g></g>
    dropdown = driver.find_element(By.CLASS_NAME, 'raphael-group-26-button')
    # print(element)
    dropdown.click() 

    span_element = driver.find_elements("css selector",'span[type="span"]')
    print(span_element)
    for e in span_element:
        # Check if the <div> contains the text "Export As CSV"
        if "Export As CSV" in e.text:
            # Click the <div> element
            # print(e)
            e.click()
            time.sleep(2)

# <div type="div" style="left: 0px; top: 0px; padding: 0px; border: none; margin: 0px; outline: none; position: static; z-index: 20; display: block; overflow: hidden; height: 100%; width: 100%; background: rgb(255, 255, 255); color: rgb(0, 0, 0); cursor: pointer;"><span type="span" style="left: 0px; top: 0px; padding: 3px 8px; border: none; margin: 0px; outline: none; position: static; z-index: 20; font-family: Verdana, sans; font-size: 10px; color: rgb(0, 0, 0); display: inline; float: left; background: rgb(255, 255, 255); cursor: pointer;">Export As CSV</span></div> 


    # # Handle the download process
    # # ...

    # # Go back to the main page to click the next image
    # driver.back()

# Close the browser when done
driver.quit()
