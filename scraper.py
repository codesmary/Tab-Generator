import sys
import time
import os
import math
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def main(argv=sys.argv):
    #replace with getting input from the command line
    artists = ["Julia Nunes", "Conan Gray", "Remo Drive"]

    try:
        os.makedirs("songs")
    except:
        for file in os.listdir("songs"):
            os.remove(os.path.join("songs",file))

    browser = webdriver.Firefox()
    browser.get("https://www.ultimate-guitar.com/explore")

    for artist in artists:
        search = browser.find_element_by_tag_name("input")
        search.clear()
        search.send_keys(artist + Keys.RETURN)
        time.sleep(5)

        try:
            num_tabs = browser.find_element_by_class_name("_2PyWj")
        except:
            continue
       
        songs = {}
        num_tabs = int(num_tabs.text.split()[0])
        for page in range(1,math.ceil(num_tabs/50)+1):
            if page > 1:
                num_tabs -= 50
                next = browser.find_element_by_link_text(str(page))
                next.click()
                time.sleep(5)
            tabs = browser.find_elements_by_class_name("_1iQi2")
            for tab in range(1,len(tabs)):
                title = tabs[tab].text
                #remove clutter before song title (4 variations)
                #1. the artist name + "\n"
                #2. "Misc Unsigned Bands\n"
                #3. "Misc Unsigned Bands\n" and the artist name followed by a dash
                #4. Another artist, followed by ft. or feat. and the artist name
                title = remove(title,r'((^(' + artist + r')+(\n)+)|((^(Misc Unsigned Bands)+(\n)+)*(' + artist + r'\s[-]\s)+)|((.*?((ft.|feat.) '+ artist + r')))+(\n)+)')
                #remove clutter after song title (3 variations)
                #1. (ver #) and all following text
                #2. * and all following text (* indicates a simplified tab)
                #3. "\n" and all following text (song title will be contained in the first line)
                title = remove(title,r'(\s*[(\*\n]+[\s\S]*)|(\n+[\s\S]*)')
                print(title)
                #if the song text doesn't match a song in the song set
                    #click on the link
                    #create a file
                    #write the lyrics to a file
                    #store the file in the songs directory
                    #click on the back button
    
    browser.close()

def remove(song,filler):
    remove = re.compile(filler)
    remove_matches = remove.search(song)
    if remove_matches != None:
        song = song.replace(remove_matches.group(),"")
    return song

if __name__ == "__main__":
    main()
