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
        #remove all the files in the songs directory
        #is this line necessary
        pass

    browser = webdriver.Firefox()
    browser.get("https://www.ultimate-guitar.com/explore")

    for artist in artists:
        search = browser.find_element_by_tag_name("input")
        search.clear()
        search.send_keys(artist + Keys.RETURN)
        
        time.sleep(5)

        #if artist doesn't exist, continue

        #create a set of songs for this artist
        num_tabs = browser.find_element_by_class_name("_2PyWj")
        num_tabs = int(num_tabs.text.split()[0])
        for page in range(1,math.ceil(num_tabs/50)+1):
            if page > 1:
                num_tabs -= 50
                next = browser.find_element_by_partial_link_text("page=" + str(page))
                next.click()
                time.sleep(5)
            for tab in range(math.min(num_tabs,50)):
                #if the song text before optional parenthesis
                #doesn't match a song in the song set, 
                    #click on the link
                    #create a file
                    #write the lyrics to a file
                    #store the file in the songs directory
                    #click on the back button
    
    browser.close()

if __name__ == "__main__":
    main()
