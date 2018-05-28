from word import Word
import re

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
            #print(str(len(chords)) + ' ' + str(len(words)))
            #print(chords)
            #print(words)
            for char in range(min(len(chords),len(words))-1):
                if words[char+1] == ' ' or words[char+1] == '\n':
                    end = char+1
                    chord = chords[chord_ptr:end]
                    end -= 1
                    while end < len(chords) - 1 and chords[end] != ' ' and chords[end] != '\n':
                        end += 1
                        chord += chords[end]
                    chord = chord.strip()
                    word = words[word_ptr:char+1].replace(' ','')
                    if len(chord) == 0 or ('N' in chord.upper() and 'C' in chord.upper()):
                        chord = None
                    if len(word) == 0:
                        word = None
                    elif word[-1] != '\n':
                        word += ' '
                    chord_ptr = end + 1
                    word_ptr = char + 1
                    if chord != None or word != None:
                        if word == None:
                            lyrics.append(Word(chord,word,'beg'))
                        else:
                            lyrics.append(Word(chord,word))
            if len(chords) > len(words):
                remaining = chords[chord_ptr:].split()
                if len(remaining) > 0:
                    #remove trailing white space
                    lyrics[-1].word = lyrics[-1].word[:-1]
                    for chord in remaining:
                        if 'N' not in chord.upper() or 'C' not in chord.upper():
                            lyrics.append(Word(chord,None,'mid'))
                    lyrics[-1].pos = 'end'
                else:
                    lyrics[-1].word = lyrics[-1].word[:-1] + '\n'
            elif len(words) > len(chords):
                remaining = words[word_ptr:].split()
                if len(remaining) > 0 and words[-1] == '\n':
                    remaining[-1] += '\n'
                if len(remaining) > 0 and words[-2] == '\n':
                    remaining[-1] += '\n'
                for word in range(len(remaining)):
                    rem_chords = chords[chord_ptr:].strip()
                    if word == 0 and len(rem_chords) > 0:
                        chord = rem_chords
                        if 'N' in chord.upper() and 'C' in chord.upper():
                            chord = None
                    else:
                        chord = None
                    if remaining[word][-1] != '\n':
                        remaining[word] += ' '
                    lyrics.append(Word(chord,remaining[word]))
                chord = chords[chord_ptr:].strip()
                if len(remaining) == 0 and len(chord) > 0 and not ('N' in chord.upper() and 'C' in chord.upper()):
                    lyrics[-1].word = lyrics[-1].word[:-1]
                    lyrics.append(Word(chord,None,end))
            else:
                lyrics[-1].word += '\n'
                if chords[-1] != ' ':
                    ptr = -1
                    while chords[ptr] != ' ':
                        ptr -= 1
                    lyrics[-1].chord = chords[ptr:].strip()
            match_len += len(match.group())
        #if a small percentage of the tab was correct matches, then return error
        if match_len / len(tab) < 0.7:
            print('unsuccessful tab: ' + str(match_len/len(tab)) + '%')
            return None
        else:
            for lyric in lyrics:
                if lyric.word != None:
                    print(('(' + lyric.chord + ')' if lyric.chord != None else "") + lyric.word,end="")
                else:
                    #how None's will be interpreted in tab creation
                    if lyric.pos == 'beg':
                        print('(' + lyric.chord + ') ',end='')
                    elif lyric.pos == 'mid':
                        print(' (' + lyric.chord + ')',end='')
                    else:
                        print(' (' + lyric.chord + ')\t\n',end='')
            return lyrics
