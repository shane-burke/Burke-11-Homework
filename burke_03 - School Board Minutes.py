#!/usr/bin/env python
# coding: utf-8

# # School Board Minutes
# 
# Scrape all of the school board minutes from http://www.mineral.k12.nv.us/pages/School_Board_Minutes
# 
# Save a CSV called `minutes.csv` with the date and the URL to the file. The date should be formatted as YYYY-MM-DD.
# 
# **Bonus:** Download the PDF files
# 
# **Bonus 2:** Use [PDF OCR X](https://solutions.weblite.ca/pdfocrx/index.php) on one of the PDF files and see if it can be converted into text successfully.
# 
# * **Hint:** If you're just looking for links, there are a lot of other links on that page! Can you look at the link to know whether it links or minutes or not? You'll want to use an "if" statement.
# * **Hint:** You could also filter out bad links later on using pandas instead of when scraping
# * **Hint:** If you get a weird error that you can't really figure out, you can always tell Python to just ignore it using `try` and `except`, like below. Python will try to do the stuff inside of 'try', but if it hits an error it will skip right out.
# * **Hint:** Remember the codes at http://strftime.org
# * **Hint:** If you have a date that you've parsed, you can use `.dt.strftime` to turn it into a specially-formatted string. You use the same codes (like %B etc) that you use for converting strings into dates.
# 
# ```python
# try:
#   blah blah your code
#   your code
#   your code
# except:
#   pass
# ```
# 
# * **Hint:** You can use `.apply` to download each pdf, or you can use one of a thousand other ways. It'd be good `.apply` practice though!

# In[1]:


import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import re
import numpy as np


# In[2]:


driver = webdriver.Chrome()


# In[3]:


url = 'http://www.mineral.k12.nv.us/pages/School_Board_Minutes'
driver.get(url)


# In[4]:


#Getting the date and PDF links 

meetings = []

minutes_block = driver.find_element_by_id("livesite-page-content-left")
minutes_list = minutes_block.find_elements_by_tag_name('p')[4:]

for minute_date in minutes_list:
    date = ''
    pdf_link = ''
    
    try:
        date = minute_date.find_elements_by_tag_name('span')[0].text.strip()
            
        #because June 16 is formatted with the link in a separate span than the text
        if date == "":
            date = minute_date.find_elements_by_tag_name('span')[3].text.strip()
    
    #strangely coded exceptions without a span or a tag
    except:
        if minute_date.text.strip() == "March 27, 2018":
            date = minute_date.text.strip()
        elif minute_date.text.strip()  == "May 21, 2019 CANCELLED":
            date = minute_date.text.strip()
        else:
            pass
    
    try:
        pdf_link =  minute_date.find_element_by_tag_name('a').get_attribute('href')
    except: 
        pdf_link = "not available"
      
    #print(date)
    
    if date != '':
        if "cancel" not in date.lower():
            meetings.append({'date': date, 
                         'pdf link': pdf_link})

meetings


# In[5]:


df = pd.DataFrame(meetings)
df


# In[6]:


#Cleaning it up

#Fixing 2108 date in there
df[df.date.str.contains('2108')]
#shows it's row 51

#Replacing in the dataframe
df.iloc[51,0] = df.iloc[51,0].replace('2108', '2018')


# In[7]:


#Turning it into date time

df['date'] = pd.to_datetime(df['date'])
df


# In[ ]:





# ## Getting the PDFs

# In[13]:


#Selenium was not working on the buttons in Google's PDF viewer, and StackOverflow's explanations on disabling it seemed a bit complex.
#Instead I looked into urllib's request function.
#These are the sources I looked at for help on this:
#https://stackoverflow.com/questions/24844729/download-pdf-using-urllib
#https://www.codegrepper.com/code-examples/delphi/download+pdf+from+link+using+python

import urllib

def download_file(download_url, filename):
    response = urllib.request.urlopen(download_url)    
    file = open(filename + ".pdf", 'wb')
    file.write(response.read())
    file.close()

#downloading only first 10
for pdf in df['pdf link'][0:10]:
    if pdf != "not available":
        filename = re.findall(r'^http://www.mineral.k12.nv.us/files/(.+).pdf', pdf)[0]
        download_file(pdf, filename)
        print(f'{filename} download complete')


# In[ ]:


#I was able to convert the first page of one of the PDFs with PDF OCR X (but more requires an upgrade from the community version)


# In[ ]:




