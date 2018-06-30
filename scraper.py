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

''' 
Global variables 
'''
browser = None
LONG_STALL = 100
SHORT_STALL = 50
WAIT_STALL = 10

'''
To be called from the tabs page for a given artist. Clicks on the link for the
song with a given tab index, returns back to the tab page, and returns the 
song object scraped from the tab page.
@param songs: A set that maintains a list of song titles successfully scraped
@param artist: The name of the current artist whose tabs are being searched
@param tab_index: Index of the current tab to be scraped in the table on the website
'''
def first_scrape(songs, artist, tab_index):
    global browser

    browser.set_page_load_timeout(SHORT_STALL)
    tab_list_class_name = '_1iQi2'
    tabs = browser.find_elements_by_class_name(tab_list_class_name)
    tab_info = tabs[tab_index]
    title = tab_info.text
    #remove extra formatting from beginning and end of tab header
    #to retrieve raw song title
    title = remove(title,r'((^(' + artist + r')+(\n)+)|((^(Misc Unsigned Bands)+(\n)+)*(' + artist + r'\s[-]\s)+)|((.*?((ft.|feat.) '+ artist + r')))+(\n)+)')
    title = remove(title,r'(\s*[(\*\n]+[\s\S]*)|(\n+[\s\S]*)')
    #only scrape tabs that have not been previously scraped and are
    #ukulele tabs
    if title not in songs and 'Ukulele' in tab_info.text:
        print('***Scraping ukulele tab for ' + title + ' by ' + artist + '***')
        song_link = tab_info.find_element_by_partial_link_text(title)
        song_link.click()
        wait = WebDriverWait(browser,WAIT_STALL)
        wait.until(EC.url_contains('tab'))
        tab_class_name = '_1YgOS'
        tab_element = browser.find_element_by_class_name(tab_class_name)
        tab = tab_element.text
        song = Song(title,tab)
        if not song:
            print('\tScrape failed for ' + title)
        browser.back()
        wait = WebDriverWait(browser,WAIT_STALL)
        wait.until(EC.url_contains('search'))
    else:
        print('Skipping tab for ' + title + ' by ' + artist + ': ', end='')
        if title in songs:
            print('Scraped identical song')
        elif not 'Ukulele' in tab_info.text:
            print('Not a ukulele tab')
        song = None

    return song

'''
Returns a selenium webdriver run in Google Chrome, populated with
the url. The browser doesn't load images or present a gui to speed
up the web scraping. Removing the headless argument will return a gui 
and is helpful for debugging with visual cues.
@param url: Url link that the browser redirects to
'''
def initialize_browser(url):
    print('Initializing browser...')
    options = webdriver.ChromeOptions()
    prefs = {'profile.managed_default_content_settings.images':2}
    options.add_experimental_option('prefs',prefs)
    options.add_argument('headless')
    browser = webdriver.Chrome(chrome_options=options)
    browser.set_page_load_timeout(LONG_STALL)
    browser.get(url)
    return browser

'''
If the page to be navigated to to retrieve the tab is greater than one,
presses the appropriate button and waits until the page loads
pre: The browser is already directed to tab search results for a given artist,
so buttons exist at the bottom of the page with the page numbers
@param page: The page number that the desired tab is located in, 1-indexed
'''
def navigate_to_page(page):
    global browser

    if page > 1:
        print('Navigating to page ' + str(page))
        browser.set_page_load_timeout(LONG_STALL)
        next = browser.find_element_by_link_text(str(page))
        next.click()
        wait = WebDriverWait(browser,WAIT_STALL)
        wait.until(EC.url_contains('page=' + str(page)))

'''
Intended to be called when the first scrape fails due to a given exception. Resets 
the browser, searches for the artist and goes to the correct page of tabs left off 
on, and attempts to run a simple scrape by calling the first_scrape function, 
but if this fails, calls itself again.
@param songs: A set that maintains a list of song titles successfully scraped
@param artist: The name of the current artist whose tabs are being searched
@param page: The page number that the desired tab is located in, 1-indexed
@param tab_index: Index of the current tab to be scraped in the table on the website
'''
def recursive_scrape(songs, artist, page, tab_index):
    global browser

    print('Closing browser')
    browser.close()
    browser = initialize_browser('https://www.ultimate-guitar.com/explore')
    search_for_artist_tabs(artist)
    navigate_to_page(page)
    
    try:
        song = first_scrape(songs,artist,tab_index)
    except Exception as e:
        print(e)
        song = recursive_scrape(songs,artist,page,tab_index)
    
    return song

'''
Returns the tab_header string, with all matches for the filler regex removed.
@param tab_header: The string scraped from the tabs page, contains the song name, the tab type, and possibly the rating and artist name
@param filler: Regex for removing the noise in tab_header besides the song name
'''
def remove(tab_header, filler):
    remove = re.compile(filler)
    remove_matches = remove.search(tab_header)
    
    if remove_matches is not None:
        tab_header = tab_header.replace(remove_matches.group(),'')
    
    return tab_header

'''
Clears the website's search bar, and navigates the browser to the
collection of tabs associated with the artist.
@param artist: The name of the artist
'''
def search_for_artist_tabs(artist):
    print('Searching for artist ' + artist)
    tab_search_bar = browser.find_element_by_tag_name('input')
    tab_search_bar.clear()
    tab_search_bar.send_keys(artist + Keys.RETURN)
    wait = WebDriverWait(browser,WAIT_STALL)
    wait.until(EC.url_contains('search'))

'''
Aggregator of tab data for a number of artists. Searches for all of the artists on
Ultimate Guitar, a website for storing musical tabs. Iterates through their collection
of songs, which can span multiple pages, and adds these song objects to a training_data 
list. This list is stored in a shelf called "tab_data" under the key "training_data".
A shelf is a way to store a state of variables from a python script in a NoSQL manner,
with the data for the variables accessible by calling their associated key.
'''
def main():
    global browser
    artists = ['Julia Nunes', 'Conan Gray'] #TODO to be replaced with user prompted artist names
    training_data = []
    data_shelf = shelve.open('tab_data')
    browser = initialize_browser('https://www.ultimate-guitar.com/explore')

    for artist in artists:
        songs = set()
        browser.set_page_load_timeout(LONG_STALL)
        search_for_artist_tabs(artist)
        num_tabs = browser.find_element_by_class_name('_2PyWj')
        num_tabs = int(num_tabs.text.split()[0])
        last_page = math.ceil(num_tabs/50) + 1

        for page in range(1, last_page):
            navigate_to_page(page)
            num_tabs_on_page = len(browser.find_elements_by_class_name('_1iQi2'))
            
            for tab in range(1, num_tabs_on_page):
                try:
                    song = first_scrape(songs,artist,tab)
                except Exception as e:
                    print(e)
                    song = recursive_scrape(songs,artist,page,tab)
                
                if song:
                    songs.add(song.title)
                    training_data.append(song)

    data_shelf['training_data'] = training_data
    data_shelf.close()
    print('Closing browser')
    browser.close()
    print('Successfully scraped ' + str(len(training_data)) + ' songs!')
    print('Stored as list of Song objects under the \'training_data\' key in the \'tab_data\' shelf')

if __name__ == '__main__':
    main()
