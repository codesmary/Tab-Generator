from word import Word
import re

class Song:
    def __init__(self, raw_tab):
        lyrics = self.generate_tab(raw_tab)
        if lyrics != None:
            self.valid = True
            self.lyrics = lyrics

    def generate_tab(tab):
        line = re.compile(r"^[ ]*(([A-Gmb#0-9][ ]*?)+)(\n([A-zÀ-ú0-9,;'’\".()\-\? ]+)\n?)?$")
        line_matches = line.search(tab)
        if line_matches == None:
            return line_matches
        else:
            #go through the matches
            #if: it's just the chords (group 1)
            #save the chords with equal width words that
            #are blank
            #else: save the chords with the words
            #determine matching based on substring matching
            #group 4 is the lyrics
            #account for chords that occur before or after the line
            #can be multiple chords
            #add the word objects to a list and return
