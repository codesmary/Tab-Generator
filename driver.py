import sys
import time
import os
import math
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def main(argv=sys.argv):
    #replace with getting input from the command line
    artists = ["Julia Nunes", "Conan Gray", "Remo Drive"]

    try:
        os.makedirs("songs")
    except:
        pass
    browser = webdriver.Firefox()
    browser.get("https://www.ultimate-guitar.com/explore")

    #deal with possibility of artist not existing

    for artist in artists:
        search = browser.find_element_by_tag_name("input")
        search.clear()
        search.send_keys(artist + Keys.RETURN)
        
        time.sleep(5)

        num_tabs = browser.find_element_by_class_name("_2PyWj")
        num_tabs = int(num_tabs.text.split()[0])

        #click forward to pages [2,n], incrementing by 1 page
        #for each number of divisible elements of 50 in the
        #total number of tabs
        print(artist + " " + str(num_tabs) + " " + str(math.ceil(num_tabs/50)))
        for page in range(1,math.ceil(num_tabs/50)+1):
            if page != 1:
                next = browser.find_element_by_partial_link_text("page=" + str(page))
                next.click()
        #set of found songs for the artist
        #search their name in the search bar
            #for each of their songs
                #if the song title is not already in found songs and 
                #if the song title has parenthesis at the end, cut those 
                #off and check to see that the original song title isn't 
                #already in found songs
                    #click on the link
                    #write the lyrics to a file
                    #store the file in the created song directory
                    #click the back button
        #elem.back()
        time.sleep(5)
    
    browser.close()

if __name__ == "__main__":
    main()
