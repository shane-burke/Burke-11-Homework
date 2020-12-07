#!/usr/bin/env python
# coding: utf-8

# # Scraping one page per row
# 
# Let's say we're interested in our members of Congress, because who isn't? Read in `congress.csv`.

# In[1]:


import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import re
import time


# In[2]:


df = pd.read_csv("congress.csv")
df.head(10)


# # Let's scrape one
# 
# The `slug` is the part of the URL that's particular to that member of Congress. So `/james-abdnor/A000009` really means `https://www.congress.gov/member/james-abdnor/A000009`.
# 
# Scrape his name, birthdaye, party, whether he's currently in congress, and his bill count (don't worry if the bill count is dirty, you can clean it up later).

# In[3]:


driver = webdriver.Chrome()


# In[4]:


#First try at scraping his information. I used the XML page to get more precise info, but I ended up changing to the following function because the bios were not standardized enough to scrape.

url = "https://www.congress.gov/member/james-abdnor/A000009"
driver.get(url)

#Bill count information
bill_count_block = driver.find_element_by_class_name("results-number").text.strip()
bill_count = re.findall(r'of (\d,?\d?\d?\d?\d?)', bill_count_block)[0]

#Navigating to the member bio page, to get to the XML page
member_bio = driver.find_element_by_class_name("member_bio_link")
member_bio.click()
driver.switch_to.window(driver.window_handles[-1])

#Using the XML page for most of the information and most precise birthday
xml_page = driver.find_element_by_xpath("/html/body/div[2]/div/div/div/div[2]/div/div/div[2]/div/div/div[1]/div/div[2]/a")
xml_page.click()
driver.switch_to.window(driver.window_handles[-1])
xml_page_text = driver.find_element_by_class_name("pretty-print").text.strip()
first_name = re.findall(r'<firstnames>(.+)</firstnames>', xml_page_text)[0]
last_name = re.findall(r'<lastname>(.+)</lastname>', xml_page_text)[0]
party = re.findall(r'<term-party>(.+)</term-party>', xml_page_text)[0]
birth_date = re.findall(r'born in .+, .+, .+, (\w+ \d+, \d\d\d\d);', xml_page_text)[0]

end_time_served = re.findall(r'<time-served>\d\d\d\d-(.+?)</time-served>', xml_page_text)[0]
if end_time_served == '':
    current = "current"
else: 
    current = "former"

print(first_name, "||", last_name, "||", birth_date, "||", party, "||", current, "||", bill_count)

#Closing the extra windows
driver.close()
driver.switch_to.window(driver.window_handles[-1])
driver.close()
driver.switch_to.window(driver.window_handles[0])


# In[5]:


#Changed it to be a bit simpler -- the XML was not working with everyone and was a lot more page loading

url = "https://www.congress.gov/member/james-abdnor/A000009"
driver.get(url)

info = driver.find_element_by_tag_name("h1").text.strip()

birth_year = re.findall(r'\((\d\d\d\d) - \d+?\)', info)[0]
name = re.findall(r'[Representative/Senator] (.+) \(', info)[0]

overview = driver.find_element_by_class_name("overview").text.strip()
party = re.findall(r'Party (\w+)', overview)[0]


if "Present" in info:
    current = "current"
else: 
    current = "not current"

bill_count_block = driver.find_element_by_class_name("results-number").text.strip()
bill_count = re.findall(r'of (\d,?\d?\d?\d?\d?)', bill_count_block)[0]

#print(info)
#print(overview)

print(name)
print(birth_year)
print(party)
print(current)
print(bill_count)


# # Build a function
# 
# Write a function called `scrape_page` that makes a URL out of the the `slug`, like we're going to use `.apply`.

# In[6]:


def scrape_page(slug):
    
    url = f'https://www.congress.gov/member/{slug}'
    
    return url


# In[7]:


scrape_page("james-abdnor/A000009")


# # Do the scraping
# 
# Rewrite `scrape_page` to actually scrape the URL. You can use your scraping code from up above. Start by testing with just one row (I put a sample call below) and then expand to your whole dataframe.
# 
# Save the results as `scraped_df`.
# 
# * **Hint:** Be sure to use `return`!
# * **Hint:** Make sure you return a `pd.Series`

# In[8]:


def scrape_page(df):
    time.sleep(.25) #added small time delay 
    slug = df['slug']
    
    url = f'https://www.congress.gov/member/{slug}'
    driver.get(url)

    info = driver.find_element_by_tag_name("h1").text.strip()

    birth_year = re.findall(r'\((\d\d\d\d)', info)[0]
    name = re.findall(r'[Representative/Senator] (.+) \(', info)[0]

    overview = driver.find_element_by_class_name("overview").text.strip()
    party = re.findall(r'Party (\w+)', overview)[0]


    if "Present" in info:
        current = "current"
    else: 
        current = "not current"

    bill_count_block = driver.find_element_by_class_name("results-number").text.strip()
    bill_count = re.findall(r'of (\d,?\d?\d?\d?\d?)', bill_count_block)[0]

    
    return {'name': name, 
            'birth_year': birth_year, 
            'party': party, 
            'current': current, 
            'bill_count': bill_count, 
            'slug': slug}


# In[9]:


# Test with this
scrape_page({'slug': 'neil-abercrombie/A000014'})


# In[10]:


#Testing with 5
scraped_test = df.head().apply(scrape_page, axis=1)
scraped_test


# In[11]:


#Converting to list that can be turned to dataframe easily
scraped_test = list(scraped_test)
scraped_test


# In[12]:


pd.DataFrame(scraped_test)


# In[13]:


### Doing the whole dataframe


# In[19]:


#running it here:
#scraped = df.apply(scrape_page, axis=1)
scraped



# In[20]:


df_scraped = pd.DataFrame(list(scraped))
df_scraped


# ## Join with your original dataframe
# 
# Join your new data with your original data, adding the `_scraped` suffix on the new columns. You can use either `.join` or `.merge`, but be sure to read the docs to know the difference!

# In[25]:


df_final = df.join(df_scraped.add_suffix('_scraped'))
del df_final['slug_scraped']
df_final


# ## Save it
# 
# Save your combined results to `congress-plus-scraped.csv`.

# In[26]:


df_final.to_csv("congress-plus-scraped.csv", index=False)


# In[ ]:




