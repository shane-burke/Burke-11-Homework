#!/usr/bin/env python
# coding: utf-8

# # Texas Tow Trucks (`.apply` and `requests`)
# 
# We're going to scrape some [tow trucks in Texas](https://www.tdlr.texas.gov/tools_search/).

# ## Import your imports

# In[1]:


import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import re
import time


# ## Search for the TLDR Number `006565540C`, and scrape the information on that company
# 
# Using [license information system](https://www.tdlr.texas.gov/tools_search/), find information about the tow truck number above, displaying the
# 
# - The business name
# - Owner/operator
# - Phone number
# - License status (Active, Expired, Etc)
# - Physical address
# 
# If you can't figure a 'nice' way to locate something, your two last options might be:
# 
# - **Find a "parent" element, then dig inside**
# - **Find all of a type of element** (like we did with `td` before) and get the `[0]`, `[1]`, `[2]`, etc
# - **XPath** (inspect an element, Copy > Copy XPath)
# 
# These kinds of techniques tend to break when you're on other result pages, but... maybe not! You won't know until you try.
# 
# > - *TIP: When you use xpath, you CANNOT use double quotes or Python will get confused. Use single quotes.*
# > - *TIP: You can clean your data up if you want to, or leave it dirty to clean later*
# > - *TIP: The address part can be tough, but you have a few options. You can use a combination of `.split` and list slicing to clean it now, or clean it later in the dataframe with regular expressions. Or other options, too, probably*

# In[2]:


driver = webdriver.Chrome()


# In[3]:


url = "https://www.tdlr.texas.gov/tools_search/"
tdlr_no = "006565540C"

driver.get(url)


# In[4]:


#Type in the TDLR number
tdlr_input = driver.find_element_by_id("mcrdata")
tdlr_input.send_keys(tdlr_no)

#Submit the form
submit_button = driver.find_element_by_id("submit3")
submit_button.click()


# In[5]:


#Table with contact info
info_table = driver.find_elements_by_tag_name("table")[4]

name = info_table.find_elements_by_tag_name("td")[2].text.strip()
owner = info_table.find_elements_by_tag_name("td")[4].text.strip()
phone = info_table.find_elements_by_tag_name("td")[6].text.strip()

#Table with status
info_table2 = driver.find_elements_by_tag_name("table")[5]

license_status = info_table2.find_elements_by_tag_name("td")[1].find_element_by_tag_name("font").text.strip()

address_info = info_table2.find_elements_by_tag_name("td")[-1].text.strip()
phys_address = re.findall(r'Physical:\n(.+\n.+)', address_info)[0]
phys_address = phys_address.replace('\n', ', ')


# In[6]:


print(name, "||", owner, "||", phone, "||", license_status, "||", phys_address)
#going to clean these up in the data frame


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# # Adapt this to work inside of a single cell
# 
# Double-check that it works. You want it to print out all of the details.

# In[7]:


def get_company_info(tdlr_no):
    
    url = "https://www.tdlr.texas.gov/tools_search/"
    #tdlr_no = "006565540C"

    driver.get(url)

    #Type in the TDLR number
    tdlr_input = driver.find_element_by_id("mcrdata")
    tdlr_input.send_keys(tdlr_no)

    #Submit the form
    submit_button = driver.find_element_by_id("submit3")
    submit_button.click()

    #Table with contact info
    info_table = driver.find_elements_by_tag_name("table")[4]

    name = info_table.find_elements_by_tag_name("td")[2].text.strip()
    owner = info_table.find_elements_by_tag_name("td")[4].text.strip()
    phone = info_table.find_elements_by_tag_name("td")[6].text.strip()

    #Table with status
    info_table2 = driver.find_elements_by_tag_name("table")[5]

    license_status = info_table2.find_elements_by_tag_name("td")[1].find_element_by_tag_name("font").text.strip()

    address_info = info_table2.find_elements_by_tag_name("td")[-1].text.strip()
    phys_address = re.findall(r'Physical:\n(.+\n.+)', address_info)[0]
    phys_address = phys_address.replace('\n', ', ')
    
    return {'name' : name, 
            'owner' : owner, 
            'phone' : phone, 
            'license_status' : license_status,
            'physical_address' : phys_address}


# In[8]:


get_company_info("006565540C")


# # Using .apply to find data about SEVERAL tow truck companies
# 
# The file `trucks-subset.csv` has information about the trucks, we'll use it to find the pages to scrape.
# 
# ### Open up `trucks-subset.csv` and save it into a dataframe

# In[9]:


df_subset = pd.read_csv("trucks-subset.csv")
df_subset


# ## Go through each row of the dataset, displaying the URL you will need to scrape for the information on that row
# 
# You don't have to actually use the search form for each of these - look at the URL you're on, it has the number in it!
# 
# For example, one URL might look like `https://www.tdlr.texas.gov/tools_search/mccs_display.asp?mcrnumber=006565540C`.
# 
# - *TIP: Use .apply and a function*
# - *TIP: You'll need to build this URL from pieces*
# - *TIP: You probably don't want to `print` unless you're going to fix it for the next question 
# - *TIP: pandas won't showing you the entire url! Run `pd.set_option('display.max_colwidth', None)` to display aaaalll of the text in a cell*

# In[10]:


def url_define(df_subset):
    tdlr_no = df_subset['TDLR Number']
    url = f'https://www.tdlr.texas.gov/tools_search/mccs_display.asp?mcrnumber={tdlr_no}'
    return url


# In[11]:


pd.set_option('display.max_colwidth', None)
df_subset.apply(url_define, axis=1)


# In[ ]:





# ### Save this URL into a new column of your dataframe, called `url`
# 
# - *TIP: Use a function and `.apply`*
# - *TIP: Be sure to use `return`*

# In[12]:


df_subset['url'] = df_subset.apply(url_define, axis=1)
df_subset


# ## Go through each row of the dataset, printing out information about each tow truck company.
# 
# Now will be **scraping** inside of your function.
# 
# - The business name
# - Owner/operator
# - Phone number
# - License status (Active, Expired, Etc)
# - Physical address
# 
# Just print it out for now.
# 
# - *TIP: use .apply*
# - *TIP: You'll be using the code you wrote before, but converted into a function*
# - *TIP: Remember how the TDLR Number is in the URL? You don't need to do the form submission if you don't want!*
# - *TIP: Make sure you adjust any variables so you don't scrape the same page again and again*

# In[13]:


def get_company_info(df_subset):
    url = df_subset['url']
    driver.get(url)
    
    #Table with contact info
    info_table = driver.find_elements_by_tag_name("table")[4]

    name = info_table.find_elements_by_tag_name("td")[2].text.strip()
    name = re.findall(r'Name: (.+)$', name)[0]
    
    owner = info_table.find_elements_by_tag_name("td")[4].text.strip()
    owner = re.findall(r'Officer: (.+) /', owner)[0]
    
    phone = info_table.find_elements_by_tag_name("td")[-2].text.strip()
    phone = re.findall(r'Phone: (.+)$', phone)[0]
    

    #Table with status
    info_table2 = driver.find_elements_by_tag_name("table")[5]

    license_status = info_table2.find_elements_by_tag_name("td")[1].find_element_by_tag_name("font").text.strip()

    address_info = info_table2.find_elements_by_tag_name("td")[-1].text.strip()
    phys_address = re.findall(r'Physical:\n(.+\n.+)', address_info)[0]
    phys_address = phys_address.replace('\n', ', ')
    
    return {'name' : name, 
            'owner' : owner, 
            'phone' : phone, 
            'license_status' : license_status,
            'physical_address' : phys_address}


# In[14]:


subset_info = df_subset.apply(get_company_info, axis=1)
subset_info = list(subset_info)


# In[15]:


df_subset_info = pd.DataFrame(subset_info)
df_subset_info


# ## Scrape the following information for each row of the dataset, and save it into new columns in your dataframe.
# 
# - The business name
# - Owner/operator
# - Phone number
# - License status (Active, Expired, Etc)
# - Physical address
# 
# It's basically what we did before, but using the function a little differently.
# 
# - *TIP: Same as above, but you'll be returning a `pd.Series` and the `.apply` line is going to be a lot longer*
# - *TIP: Save it to a new dataframe!*
# - *TIP: Make sure you change your `df` variable names correctly if you're cutting and pasting - there are a few so it can get tricky*

# In[16]:


df_subset_final = df_subset.join(df_subset_info)
df_subset_final


# ### Save your dataframe as a CSV named `tow-trucks-extended.csv`

# In[17]:


df_subset_final.to_csv("tow-trucks-extended.csv", index=False)


# ### Re-open your dataframe to confirm you didn't save any extra weird columns

# In[18]:


pd.read_csv("tow-trucks-extended.csv")


# ## Process the entire `tow-trucks.csv` file
# 
# We just did it on a short subset so far. Now try it on all of the tow trucks. **Save as the same filename as before**

# In[19]:


df_full = pd.read_csv("tow-trucks.csv")
df_full


# In[20]:


df_full['url'] = df_full.apply(url_define, axis=1)
df_full.head()


# In[21]:


full_info = list(df_full.apply(get_company_info, axis=1))
df_full_info = pd.DataFrame(full_info)
df_full_info.head(5)


# In[22]:


df_full_final = df_full.join(df_full_info)
df_full_final.head(5)


# In[23]:


df_full_final.to_csv("tow-trucks-extended.csv", index=False)


# In[ ]:




