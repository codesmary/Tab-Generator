from word import Word
import re

class Song:
    def __init__(self, title, raw_tab):
        lyrics = self.generate_tab(raw_tab)
        if lyrics != None:
            self.valid = True
            self.lyrics = lyrics
            self.title = title

    #store lyrics in a vector containing word objects, which are a container for the chord/word at that position in the line
    def generate_tab(self, tab):
        lyrics = []
        line = re.compile(r"^([ ]*([a-gA-GIiJjMmNnSsUu./\\#*1-9\[\]()][ ]*)+)\n([A-zÀ-ú0-9,:;''’\".()\-\?! ]+([ ]?\n){0,2})", re.MULTILINE)
        line_matches = line.finditer(tab)
        match_len = 0
        for match in line_matches:
            chords = match.group(1)
            words = match.group(3)

            #add padding to the end of chords, as there is no '\n' character, and the padding
            #will later be stripped. this helps in the chord capturing process
            chords += ' '
            
            #add padding to the last verse
            if '\n' not in words:
                words += '\n'

            chord_ptr = 0
            word_ptr = 0
            wordAdded = False
            for char in range(min(len(chords),len(words)) - 1):
                #if beginning of line or end of word and chord
                if (char == 0 and words[char] in [' ','\n']) or (chords[char + 1] in [' ','\n'] and words[char + 1] in [' ','\n']):
                    #remove whitespace from beginning of chord and capture multicharacter chord
                    end = char + 1
                    chord = chords[chord_ptr:end]
                    end -= 1
                    while end < len(chords) - 1 and chords[end] not in [' ','\n']:
                        end += 1
                        chord += chords[end]
                    chord = chord.strip()
 
                    word = words[word_ptr:char+1]
                    word = word.split()
                    if len(word) > 1:
                        word = words[word_ptr:char+1]
                        word = word.strip()
                    else:
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
                            word = Word(chord,None,'midline' if wordAdded else 'preline')
                            lyrics.append(word)
                        else:
                            word = Word(chord,word,'midline')
                            lyrics.append(word)
                            wordAdded = True
            
            if len(chords) > len(words):
                last_word = words[word_ptr:]
                last_word = last_word.strip()
                if last_word:
                    last_word_len = len(last_word)
                    end_ptr = word_ptr + last_word_len
                    while chords[end_ptr] not in [' ','\n']:
                        end_ptr += 1
                    chord = chords[chord_ptr:end_ptr].strip()
                    if chord:
                        chord_ptr = end_ptr
                    else:
                        chord = None
                    lyrics.append(Word(chord, last_word))

                lyrics[-1].pos = 'endstanza' if words[-2:] == '\n\n' else 'endline'
                lyrics[-1].word += '\n' * (words.count('\n') - lyrics[-1].word.count('\n'))

                remaining = chords[chord_ptr:].split()
                if remaining:
                    for chord in remaining:
                        if 'N' not in chord.upper() or 'C' not in chord.upper():
                            lyrics.append(Word(chord,None,'postline'))
            elif len(words) > len(chords):
                remaining = words[word_ptr:].split()

                new_lines = '\n' * words.count('\n')
                if remaining:
                    remaining[-1] += new_lines
                else:
                    lyrics[-1].word += new_lines
                
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
                lyrics[-1].pos = 'endstanza' if words[-2:] == '\n\n' else 'endline'
                
                if chords[chord_ptr:]:
                    chord = chords[chord_ptr:].strip()
                    lyrics.append(Word(chord,None,'postline'))

            match_len += len(match.group())
        
        match_percentage = match_len / len(tab)
        match_percentage = 1
        if match_percentage < 0.65:
            print('unsuccessful tab: ' + str(match_percentage) + '%')
            return None
        else:
            return lyrics

    def print_lyrics(self, lyrics):
        word_offset = 0
        chord_line = [' '] * 100
        word_line = []
        for lyric_index in range(len(lyrics)):
            lyric = lyrics[lyric_index]
            chord = lyric.chord + ' ' if lyric.chord else ''
            word = lyric.word
            c_length = len(chord)
            
            if lyric.pos == 'preline':
                c_length = len(chord)
                for i in range(c_length):
                    chord_line[word_offset + i] = chord[i]
                word_offset += c_length
                word_line.append(' ' * c_length)
            elif lyric.pos == 'midline':
                for i in range(c_length):
                    chord_line[word_offset + i] = chord[i]    
                if lyric.word:
                    w_length = len(word)
                    if w_length < c_length:
                        word += ' ' * (c_length - w_length)
                    word_line.append(word)
                    new_len = max(w_length,c_length)
                else:
                    new_len = c_length
                    word_line.append(' ' * c_length)
                word_offset += new_len
            elif lyric.pos == 'postline':
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
                    chord_line = [' '] * 100
                    word_line = []
            elif lyric.pos == 'endline' or lyric.pos == 'endstanza':
                for i in range(c_length):
                    chord_line[word_offset + i] = chord[i]
                w_length = len(word.replace('\n',''))
                word_line.append(word)
                word_offset += max(w_length,c_length)
                
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
                    chord_line = [' '] * 100
                    word_line = []
