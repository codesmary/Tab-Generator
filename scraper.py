import sys
import time
import os
import math
import re
import shelve
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from song import Song

''' 
Global variables 
'''
BROWSER = None
DEBUG_MODE = True
LONG_STALL = 100
SHORT_STALL = 50
WAIT_STALL = 10

'''
Changes the Ultimate Guitar search bar drop down menu to 'Artists' option instead
of 'Tabs'. This ensures the tab discography scraped is composed of only songs by
the user-selected artist.
pre: Assumes the 'Artists' option is 75 px below the drop down arrow for search
type selection
'''
def change_search_criteria_to_artists():
    global BROWSER
    
    print('Changing search criteria to artists')
    drop_down_menu = BROWSER.find_element_by_class_name('_1487a')
    ActionChains(BROWSER).move_to_element(drop_down_menu).perform()
    ActionChains(BROWSER).move_by_offset(0,75).perform()
    ActionChains(BROWSER).click().perform()

'''
Closes the pop-up ad on the explore page, if present. Assumes the 'x' button is in 
the upper right corner.
pre: The browser is navigated to the https://www.ultimate-guitar.com/explore page
'''
def close_ad():
    global BROWSER

    print('Closing ad')
    try:
        ad = BROWSER.find_element_by_class_name('countdown')
        ad_width = ad.size['width']
        ad_height = ad.size['height']
        ActionChains(BROWSER).move_to_element_with_offset(ad, ad_width - 10, ad_height/4).perform()
        ActionChains(BROWSER).click().perform()
    except:
        pass

'''
To be called from the tabs page for a given artist. Clicks on the link for the
song with a given tab index, returns back to the tab page, and returns the 
song object scraped from the tab page.
@param songs: A set that maintains a list of song titles successfully scraped
@param artist: The name of the current artist whose tabs are being searched
@param tab_index: Index of the current tab to be scraped in the table on the website
'''
def first_scrape(songs, artist, tab_index):
    global BROWSER

    BROWSER.set_page_load_timeout(SHORT_STALL)
    tab_list_class_name = '_1iQi2'
    tabs = BROWSER.find_elements_by_class_name(tab_list_class_name)
    tab_info = tabs[tab_index]
    title = remove(tab_info.text, r'(\s*[(\*\n]+[\s\S]*)|(\n+[\s\S]*)')
    if title not in songs and 'Ukulele' in tab_info.text:
        print('***Scraping ukulele tab for ' + title + ' by ' + artist + '***')
        song_link = tab_info.find_element_by_partial_link_text(title)
        song_link.click()
        wait = WebDriverWait(BROWSER,WAIT_STALL)
        wait.until(EC.url_contains('tab'))
        tab_class_name = '_1YgOS'
        tab_element = BROWSER.find_element_by_class_name(tab_class_name)
        tab = tab_element.text
        song = Song(title,tab)
        if not song.is_valid():
            print('\tScrape failed for ' + title)
        BROWSER.back()
        wait = WebDriverWait(BROWSER,WAIT_STALL)
        wait.until(EC.url_contains('artist'))
    else:
        print('Skipping tab for ' + title + ' by ' + artist + ': ', end='')
        if title in songs:
            print('Scraped identical song')
        elif not 'Ukulele' in tab_info.text:
            print('Not a ukulele tab')
        song = None

    return song

'''
Determines if another page exists after the current page of tabs.
pre: The browser is directed to the artist's discography of tabs
'''
def has_next_page(page):
    global BROWSER
    
    valid_page = True
    if page > 1:
        try:
            BROWSER.find_element_by_link_text('NEXT')
        except:
            valid_page = False

    return valid_page

'''
Returns a selenium webdriver run in Google Chrome, populated with
the url. The browser doesn't load images or present a gui to speed
up the web scraping. Removing the headless argument will return a gui 
and is helpful for debugging with visual cues.
@param url: Url link that the browser redirects to
'''
def initialize_browser(url):
    global DEBUG_MODE
    global BROWSER

    print('Initializing browser...')
    options = webdriver.ChromeOptions()
    prefs = {'profile.managed_default_content_settings.images':2}
    options.add_experimental_option('prefs',prefs)
    if not DEBUG_MODE:
        options.add_argument('headless')
    browser = webdriver.Chrome(chrome_options=options)
    browser.set_page_load_timeout(LONG_STALL)
    browser.get(url)
    BROWSER = browser
    close_ad()

'''
If the page to be navigated to to retrieve the tab is greater than one,
presses the appropriate button and waits until the page loads
pre: The browser is already directed to tab search results for a given artist,
so buttons exist at the bottom of the page with the page numbers
@param page: The page number that the desired tab is located in, 1-indexed
'''
def navigate_to_page(page):
    global BROWSER

    if page > 1:
        print('Navigating to page ' + str(page))
        BROWSER.set_page_load_timeout(LONG_STALL)
        next = BROWSER.find_element_by_link_text(str(page))
        next.click()
        wait = WebDriverWait(BROWSER,WAIT_STALL)
        wait.until(EC.url_contains('page=' + str(page)))

'''
Returns a list of artist names, prompted from the user.
'''
def prompt_user_for_artists():
    artists = re.split(', |,', input('Enter a comma delimited list of the artists you want to scrape ukulele songs from!\n'))
    print('Great! Searching for ' + ', '.join(artists))
    return artists

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
    global BROWSER

    print('Closing browser')
    BROWSER.close()
    initialize_browser('https://www.ultimate-guitar.com/explore')
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
@param tab_header: The string scraped from the tabs page, contains the song name, the tab type, and possibly the rating
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
pre: Assumes the resulting list of artists is sorted by relevance to search query
@param artist: The name of the artist
'''
def search_for_artist_tabs(artist):
    global BROWSER

    print('Searching for artist ' + artist)

    change_search_criteria_to_artists()
    
    tab_search_bar = BROWSER.find_element_by_tag_name('input')
    tab_search_bar.clear()
    tab_search_bar.send_keys(artist + Keys.RETURN)
    wait = WebDriverWait(BROWSER,WAIT_STALL)
    wait.until(EC.url_contains('search'))

    try:
        #this is the most relatable variable name
        invalid_artist = '_2doOH'
        BROWSER.find_element_by_class_name(invalid_artist)
        raise ValueError('The artist ' + artist + ' does not exist in the Ultimate Guitar database')
    except:
        pass

    desired_artist = BROWSER.find_element_by_class_name('_33Vdc')
    desired_artist.click()

'''
Aggregator of tab data for a number of artists. Searches for all of the artists on
Ultimate Guitar, a website for storing musical tabs. Iterates through their collection
of songs, which can span multiple pages, and appends these tabs to a tab_training_data 
text file. The location of the tab titles in the file text is stored in a shelf called 
"seed_indices" under the key "seeds". The intention is to scrape these tabs from Ultimate 
Guitar in order for the "tab_corpus.txt" file to be used as training data. After the 
LSTM has been trained on this collection of tabs, it is recommended to randomly select 
one of the integer values stored in the "seeds" list to retrieve a string from the 
"tab_corpus.txt" file to be used as a starting point for text generation, as this will 
guarantee the generated output begins with a song title, generally having the appearance 
of a tab.
'''
def main():
    global BROWSER
    num_songs = 0
    training_data_ptr = 0
    seed_indices = []
    data_shelf = shelve.open('seeds')
    tab_training_data = open('tab_corpus.txt','w')

    artists = prompt_user_for_artists()
    initialize_browser('https://www.ultimate-guitar.com/explore')

    for artist in artists:
        songs = set()
        BROWSER.set_page_load_timeout(LONG_STALL)
        
        try:
            search_for_artist_tabs(artist)
        except ValueError as ve:
            print(ve)
            continue

        page = 1
        while has_next_page(page):
            navigate_to_page(page)
            tabs = BROWSER.find_elements_by_class_name('_1iQi2')
            num_tabs_on_page = len(tabs)
            
            starting_tab_index = 0
            for tab_index in range(num_tabs_on_page):
                starting_tab_index += 1
                if 'CHORDS & TABS' in tabs[tab_index].text:
                    break

            for tab_index in range(starting_tab_index, num_tabs_on_page):
                try:
                    song = first_scrape(songs,artist,tab_index)
                except Exception as e:
                    print(e)
                    song = recursive_scrape(songs,artist,page,tab_index)
                
                if song and song.is_valid():
                    num_songs += 1
                    songs.add(song.title)
                    new_tab = song.get_song()
                    seed_indices.append(training_data_ptr)
                    training_data_ptr += len(new_tab)
                    tab_training_data.write(new_tab)

            page += 1

    data_shelf['seed_indices'] = seed_indices
    print('Closing browser')
    data_shelf.close()
    tab_training_data.close()
    BROWSER.close()
    print('Successfully scraped ' + str(num_songs) + ' songs!')
    if num_songs < 50:
        print('\tTry to scrape at least 50 songs for the best tab generation results!')
    print('Stored as list of Song objects under the \'training_data\' key in the \'tab_data\' shelf')

if __name__ == '__main__':
    main()
