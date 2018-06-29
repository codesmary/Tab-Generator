import sys
import time
import os
import math
import re
import shelve
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from song import Song

chromeOptions = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
chromeOptions.add_experimental_option("prefs",prefs)
browser = webdriver.Chrome(chrome_options=chromeOptions)
LONG_STALL = 100
SHORT_STALL = 50
WAIT_STALL = 10

def main():
    artists = ['Julia Nunes', 'Conan Gray']
    training_data = []
    data_shelf = shelve.open('song_data')
    browser.get('https://www.ultimate-guitar.com/explore')

    for artist in artists:
        #maintain a set of songs for each artist to avoid
        #duplicate song data
        songs = set()
        
        #reset timeout to default with each artist
        browser.set_page_load_timeout(LONG_STALL)
        print(LONG_STALL)

        #search tab website for artist
        search = browser.find_element_by_tag_name('input')
        search.clear()
        search.send_keys(artist + Keys.RETURN)
        
        #stall program until the artist page has loaded
        #indicated by visibility of number of tabs element
        wait = WebDriverWait(browser,WAIT_STALL)
        tab_locator = (By.CLASS_NAME,'_2PyWj')
        wait.until(EC.visibility_of_element_located(tab_locator))
        #time.sleep(2)

        #first number in web element is number of tabs
        num_tabs = browser.find_element_by_class_name('_2PyWj')
        num_tabs = int(num_tabs.text.split()[0])

        #iterate through pages of tabs, 50 tabs per page
        last_page = math.ceil(num_tabs/50)+1
        for page in range(1, last_page):
            if page > 1:
                #reset timeout to default with each new page
                browser.set_page_load_timeout(LONG_STALL)
                print(LONG_STALL)
                num_tabs -= 50
                next = browser.find_element_by_link_text(str(page))
                next.click()
                wait = WebDriverWait(browser,WAIT_STALL)
                wait.until(EC.url_contains('https://www.ultimate-guitar.com/search.php?page=' + str(page)))
                #time.sleep(1)
            tabs = browser.find_elements_by_class_name('_1iQi2')
            #time.sleep(1)
            for tab in range(1,len(tabs)):
                try:
                    song = first_scrape(songs,artist,tab)
                except Exception as e:
                    print(e)
                    song = recursive_scrape(songs,artist,page,tab)
                if song:
                    training_data.append(song)
    
    data_shelf['training_data'] = training_data
    data_shelf.close()
    browser.close()
    
def first_scrape(songs, artist, tab_index):
    global browser
    tabs = browser.find_elements_by_class_name('_1iQi2')
    #time.sleep(1)
    tab = tabs[tab_index]
    #remove clutter from title and click on links to
    #ukulele songs that are new
    title = tab.text
    title = remove(title,r'((^(' + artist + r')+(\n)+)|((^(Misc Unsigned Bands)+(\n)+)*(' + artist + r'\s[-]\s)+)|((.*?((ft.|feat.) '+ artist + r')))+(\n)+)')
    title = remove(title,r'(\s*[(\*\n]+[\s\S]*)|(\n+[\s\S]*)')

    if title not in songs and 'Ukulele' in tab.text:
        #assert that a simple scrape should take no
        #longer than a short stall to switch between pages
        browser.set_page_load_timeout(SHORT_STALL)
        print(SHORT_STALL)
        song_link = tab.find_element_by_partial_link_text(title)
        #time.sleep(2)
        song_link.click()
        wait = WebDriverWait(browser,WAIT_STALL)
        wait.until(EC.url_contains('tab'))
        #time.sleep(3)
        lyrics = browser.find_element_by_class_name('_1YgOS')
        #time.sleep(2)
        lyrics = lyrics.text
        #TODO delete temp writing
        file = open("test_song.txt",'w')
        file.write(lyrics)
        file.close()
        song = Song(title,lyrics)
        browser.back()
        
        wait = WebDriverWait(browser,WAIT_STALL)
        wait.until(EC.url_contains('search'))
        
        #time.sleep(2)
        
    else:
        song = None

    return song

def recursive_scrape(songs, artist, page, tab_index):
    global browser
    #reset timeout to long stall to initialize page
    browser.set_page_load_timeout(LONG_STALL)
    print(LONG_STALL)
    browser.close()
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images":2}
    chromeOptions.add_experimental_option("prefs",prefs)
    browser = webdriver.Chrome(chrome_options=chromeOptions)
    browser.get('https://www.ultimate-guitar.com/explore')
    #time.sleep(1)
    search = browser.find_element_by_tag_name('input')
    search.clear()
    search.send_keys(artist + Keys.RETURN)
    wait = WebDriverWait(browser,WAIT_STALL)
    tab_locator = (By.CLASS_NAME,'_2PyWj')
    wait.until(EC.visibility_of_element_located(tab_locator))
    #time.sleep(1)
    if page > 1:
        next = browser.find_element_by_link_text(str(page))
        next.click()
        wait = WebDriverWait(browser,WAIT_STALL)
        wait.until(EC.url_contains('https://www.ultimate-guitar.com/search.php?page=' + str(page)))
        #time.sleep(1)
    try:
        song = first_scrape(songs,artist,tab_index)
    except:
        song = recursive_scrape(songs,artist,page,tab_index)
    
    return song

def remove(song, filler):
    remove = re.compile(filler)
    remove_matches = remove.search(song)
    if remove_matches is not None:
        song = song.replace(remove_matches.group(),'')
    return song

if __name__ == '__main__':
    main()
