from word import Word
import re

#need to continue testing on other songs
class Song:
    def __init__(self, raw_tab):
        lyrics = self.generate_tab(raw_tab)
        if lyrics != None:
            self.valid = True
            self.lyrics = lyrics

    def generate_tab(self, tab):
        lyrics = []
        line = re.compile(r"^([ ]*([a-gA-GIiJjMmNnSsUu./\\\-#*1-9\[\]()][ ]*)+)\n([A-zÀ-ú0-9,:;''’\".()\-\?! ]+)\n?$", re.MULTILINE)
        line_matches = line.finditer(tab)
        match_len = 0
        for match in line_matches:
            chords = match.group(1)
            words = match.group(3) + ' '
            chord_ptr = 0
            word_ptr = 0
            for char in range(min(len(chords),len(words))):
                if words[char] == ' ':
                    chord = chords[chord_ptr:char+1].strip()
                    word = words[word_ptr:char+1].strip()
                    if len(chord) == 0:
                        chord = None
                    if len(word) == 0:
                        word = None
                    else:
                        word += ' '
                    chord_ptr = char + 1
                    word_ptr = char + 1
                    if chord != None or word != None:
                        #print('chord ' + ('none' if chord==None else chord))
                        #print('word ' + ('none' if word==None else word))
                        lyrics.append(Word(chord,word))
            if len(chords) > len(words):
                lyrics[-1].word += '\n'
                remaining = chords[chord_ptr:].split()
                for chord in remaining:
                    #print('chord ' + chord)
                    #print('no word')
                    lyrics.append(Word(chord,None))
            elif len(words) > len(chords):
                remaining = words[word_ptr:].split()
                for word in range(len(remaining)):
                    rem_chords = chords[chord_ptr:].strip()
                    if word == 0 and len(rem_chords) > 0:
                        chord = rem_chords
                    else:
                        chord = None
                    #print('chord ' + ('none' if chord==None else chord))
                    #print('word ' + remaining[word])
                    lyrics.append(Word(chord,remaining[word] + ' '))
                lyrics[-1].word = lyrics[-1].word[:-1] + '\n'
            else:
                lyrics[-1].word += '\n'
            match_len += len(match.group())
        #if a small percentage of the tab was correct matches, then return error
        if match_len / len(tab) < 0.5:
            return None
        else:
            for lyric in lyrics:
                print(lyric.word,end="")
            return lyrics
