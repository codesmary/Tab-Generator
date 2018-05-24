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
        line = re.compile(r"^([ ]*([a-gA-GIiJjMmNnSsUu./\\\-#*1-9\[\]()][ ]*)+)\n([A-zÀ-ú0-9,:;''’\".()\-\?! ]+\n{0,2})", re.MULTILINE)
        line_matches = line.finditer(tab)
        match_len = 0
        for match in line_matches:
            chords = match.group(1)
            words = match.group(3)
            chord_ptr = 0
            word_ptr = 0
            for char in range(min(len(chords),len(words))):
                if words[char] == ' ' or words[char] == '\n':
                    end = char+1
                    chord = chords[chord_ptr:end]
                    end -= 1
                    while end < len(chords) - 1 and chords[end] != ' ' and chords[end] != '\n':
                        end += 1
                        chord += chords[end]
                    chord = chord.strip()
                    word = words[word_ptr:char+1].replace(' ','')
                    if len(chord) == 0:
                        chord = None
                    if len(word) == 0:
                        word = None
                    elif word[-1] != '\n':
                        word += ' '
                    chord_ptr = end + 1
                    word_ptr = char + 1
                    if chord != None or word != None:
                        lyrics.append(Word(chord,word))
            if len(chords) > len(words):
                lyrics[-1].word = lyrics[-1].word[:-1]
                remaining = chords[chord_ptr:].split()
                for chord in remaining:
                    lyrics.append(Word(chord,None))
            elif len(words) > len(chords):
                remaining = words[word_ptr:].split()
                if words[-1] == '\n':
                    remaining[-1] += '\n'
                if words[-2] == '\n':
                    remaining[-1] += '\n'
                for word in range(len(remaining)):
                    rem_chords = chords[chord_ptr:].strip()
                    if word == 0 and len(rem_chords) > 0:
                        chord = rem_chords
                    else:
                        chord = None
                    if remaining[word][-1] != '\n':
                        remaining[word] += ' '
                    lyrics.append(Word(chord,remaining[word]))
            else:
                lyrics[-1].word += '\n'
            match_len += len(match.group())
        #if a small percentage of the tab was correct matches, then return error
        if match_len / len(tab) < 0.5:
            return None
        else:
            for lyric in lyrics:
                if lyric.word != None:
                    print(('(' + lyric.chord + ')' if lyric.chord != None else "") + lyric.word,end="")
                else:
                    #for tab generation, None will be represented
                    #as \t\n
                    print(' (' + lyric.chord + ')\t\n')
            return lyrics
