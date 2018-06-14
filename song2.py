from word import Word
import re

class Song:
    def __init__(self, title, raw_tab):
        lyrics = self.generate_tab(raw_tab)
        if lyrics != None:
            self.valid = True
            self.lyrics = lyrics
            self.title = title

#TODO then change back to single spacing, and fix the formatting so that these are also captured
#TODO capture endstanza
#TODO turn position fields into boolean functions contained in word class, so net does not have to generate them on the fly
    #preline, midline, postline, endline, endstanza

    #store lyrics in a vector containing word objects, which are a container for the chord/word at that position in the line
    def generate_tab(self, tab):
        lyrics = []
        line = re.compile(r"^([ ]*([a-gA-GIiJjMmNnSsUu./\\\-#*1-9\[\]()][ ]*)+)\n([A-zÀ-ú0-9,:;''’\".()\-\?! ]+\n{1,2})", re.MULTILINE)
        line_matches = line.finditer(tab)
        match_len = 0
        for match in line_matches:
            chords = match.group(1)
            words = match.group(3)
            chord_ptr = 0
            word_ptr = 0
            for char in range(min(len(chords),len(words)) - 1):
                if words[char + 1] in [' ','\n']:
                    #remove whitespace from beginning of chord and capture multicharacter chord
                    end = char + 1
                    chord = chords[chord_ptr:end]
                    end -= 1
                    while end < len(chords) - 1 and chords[end] not in [' ','\n']:
                        end += 1
                        chord += chords[end]
                    chord = chord.strip()
 
                    word = words[word_ptr:char+1].replace(' ','')
                    if not chord or ('N' in chord.upper() and 'C' in chord.upper()):
                        chord = None
                    if not word:
                        word = None
                    elif '\n' not in word:
                        word += ' '
                    chord_ptr = end + 1
                    word_ptr = char + 1
                    if chord or word:
                        if not word:
                            lyrics.append(Word(chord,word,'preline'))
                        else:
                            lyrics.append(Word(chord,word,'midline'))
            
            if len(chords) > len(words):
                lyrics[-1].pos = 'endstanza' if words[-2:] == '\n\n' else 'endline'

                #add new lines to the last word
                for i in range(-1,-3,-1):
                    if words[i] == '\n':
                        lyrics[-1].word += '\n'

                remaining = chords[chord_ptr:].split()
                if remaining:
                    for chord in remaining:
                        if 'N' not in chord.upper() or 'C' not in chord.upper():
                            lyrics.append(Word(chord,None,'postline'))
            elif len(words) > len(chords):
                remaining = words[word_ptr:].split()
                #add new lines to the last word
                for i in range(-1,-3,-1):
                    if remaining and words[i] == '\n':
                        remaining[-1] += '\n'
                rem_chords = chords[chord_ptr:].strip()
                if 'N' in rem_chords.upper() and 'C' in rem_chords.upper():
                    rem_chords = None
                for word in range(len(remaining)):
                    #assign the remaining chords to the next word that
                    #hasn't been matched up with any chords yet
                    if word == 0 and rem_chords:
                        chord = rem_chords
                    else:
                        chord = None
                    #add spacing to words in middle
                    if remaining[word][-1] != '\n':
                        remaining[word] += ' '
                    lyrics.append(Word(chord,remaining[word],'midline'))

                lyrics[-1].pos = 'endstanza' if words[-2:] == '\n\n' else 'endline'

                chord = chords[chord_ptr:].strip()
                if not remaining and chord and not ('N' in chord.upper() and 'C' in chord.upper()):
                    lyrics.append(Word(chord,None,'postline'))
            else:
                lyrics[-1].word += '\n'

                if chords[-1] != ' ':
                    ptr = -1
                    while chords[ptr] != ' ':
                        ptr -= 1
                    lyrics[-1].chord = chords[ptr:].strip()
                lyrics[-1].pos = 'endstanza' if words[-2:] == '\n\n' else 'endline'

            match_len += len(match.group())
        
        match_percentage = match_len / len(tab)
        if match_percentage < 0.65:
            print('unsuccessful tab: ' + str(match_percentage) + '%')
            return None
        else:
            self.print_lyrics(lyrics)
            return lyrics

    def print_lyrics(self, lyrics):
        word_offset = 0
        chord_line = [' '] * 70
        word_line = []
        for lyric_index in range(len(lyrics)):
            lyric = lyrics[lyric_index]
            chord = lyric.chord + ' ' if lyric.chord != None else ''
            word = lyric.word
            c_length = len(chord)
            if lyric.pos == 'preline':
                for i in range(c_length):
                    chord_line[word_offset + i] = chord[i]
                word_offset += c_length
                word_line.append(' ' * c_length)
            elif lyric.pos == 'midline':
                for i in range(c_length):
                    chord_line[word_offset + i] = chord[i]
                w_length = len(word)
                word_line.append(word)
                word_offset += w_length
            elif lyric.pos == 'postline': #shout out to posty

                for i in range(c_length):
                    chord_line[word_offset + i] = chord[i]
                word_offset += c_length

                if ((lyric_index + 1) % len(lyrics) != 0 and lyrics[lyric_index + 1].pos is not 'postline') or (lyric_index + 1) % len(lyrics) == 0:
                    end_slice = len(chord_line) - 1
                    while chord_line[end_slice] == ' ' and end_slice > -1:
                        end_slice -= 1
                    end_slice += 1
                    chord_line = chord_line[:end_slice]
                    chord_line = ''.join(chord_line) + '\n'
                    word_line = ''.join(word_line)
                    print(chord_line + word_line, end = '')

                    word_offset = 0
                    chord_line = [' '] * 70
                    word_line = []
            elif lyric.pos == 'endline' or lyric.pos == 'endstanza':
                for i in range(c_length):
                    chord_line[word_offset + i] = chord[i]
                w_length = len(word.replace('\n',''))
                word_line.append(word)
                word_offset += w_length
                
                if ((lyric_index + 1) % len(lyrics) != 0 and lyrics[lyric_index + 1].pos is not 'postline') or (lyric_index + 1) % len(lyrics) == 0:
                    end_slice = len(chord_line) - 1
                    while chord_line[end_slice] == ' ' and end_slice > -1:
                        end_slice -= 1
                    end_slice += 1
                    chord_line = chord_line[:end_slice]
                    chord_line = ''.join(chord_line) + '\n'
                    word_line = ''.join(word_line)
                    print(chord_line + word_line, end = '')

                    word_offset = 0
                    chord_line = [' '] * 70
                    word_line = []
