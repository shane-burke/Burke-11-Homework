#!/usr/bin/env python
# coding: utf-8

# # Rock and Mineral Clubs
# 
# Scrape all of the rock and mineral clubs listed at https://rocktumbler.com/blog/rock-and-mineral-clubs/ (but don't just cut and paste!)
# 
# Save a CSV called `rock-clubs.csv` with the name of the club, their URL, and the city they're located in.
# 
# **Bonus**: Add a column for the state. There are a few ways to do this, but knowing that `element.parent` goes 'up' one element might be helpful.
# 
# * _**Hint:** The name of the club and the city are both inside of td elements, and they aren't distinguishable by class. Instead you'll just want to ask for all of the tds and then just ask for the text from the first or second one._
# * _**Hint:** If you use BeautifulSoup, you can select elements by attributes other than class or id - instead of `doc.find_all({'class': 'cat'})` you can do things like `doc.find_all({'other_attribute': 'blah'})` (sorry for the awful example)._
# * _**Hint:** If you love `pd.read_html` you might also be interested in `pd.concat` and potentially `list()`. But you'll have to clean a little more!_

# In[1]:


import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import re


# In[2]:


driver = webdriver.Chrome()


# In[3]:


url = 'https://rocktumbler.com/blog/rock-and-mineral-clubs'
driver.get(url)


# In[4]:


rock_clubs = []
sections = driver.find_elements_by_tag_name("section")[1:-2]

for section in sections:
    
    state_heading = section.find_elements_by_tag_name("h3")[0].text.strip()
    #print(state_heading)
    
    state = re.findall(r'^(.+) Rock and Mineral Clubs',state_heading)[0]
    #print(state)
        
    #the green headings are their own tables, so we'll use the second table per section
    rows = section.find_elements_by_tag_name("table")[1].find_elements_by_tag_name("tr")  
    for row in rows:
        club = row.find_elements_by_tag_name("td")[0].text.strip()
        city = row.find_elements_by_tag_name("td")[1].text.strip()
        club_link = row.find_element_by_tag_name("a").get_attribute("href")
        #print(club, "||", city, "||", club_link)
        
        rock_clubs.append({'state': state, 
                           'club': club,
                           'city': city,
                          'club link': club_link})


# In[5]:


print(rock_clubs)


# In[6]:


df = pd.DataFrame(rock_clubs)
df


# In[7]:


df.to_csv('rock-clubs.csv', index=False)


# In[ ]:




