from word import Word
import re

#rewrite to fix formatting
class Song:
    def __init__(self, title, raw_tab):
        lyrics = self.generate_tab(raw_tab)
        if lyrics != None:
            self.valid = True
            self.lyrics = lyrics
            self.title = title

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
            print(str(len(chords)) + ' ' + str(len(words)))
            print('chords: ' + chords)
            print('words: ' + words)
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
                            lyrics.append(Word(chord,word,'beg'))
                        else:
                            lyrics.append(Word(chord,word))
            if len(chords) > len(words):
                remaining = chords[chord_ptr:].split()
                if remaining:
                    #remove spacing associated with last word
                    if lyrics:
                        update_word = -1
                        while lyrics[update_word].word == None:
                            update_word -= 1
                        lyrics[update_word].word = lyrics[update_word].word.strip()

                    for chord in remaining:
                        if 'N' not in chord.upper() or 'C' not in chord.upper():
                            lyrics.append(Word(chord,None,'mid'))
                    
                    #associate formatting of last string in word with chord
                    if words[-1] == '\n' and words[-2] == '\n':
                        lyrics[-1].pos = 'end_stanza'
                    else:
                        lyrics[-1].pos = 'end_line'
                else:
                    lyrics[-1].word = lyrics[-1].word[:-1] + '\n'
            elif len(words) > len(chords):
                remaining = words[word_ptr:].split()
                #add new lines to the last word
                for i in range(-1,-3,-1):
                    print('char: '+words[i])
                    if remaining and words[i] == '\n':
                        remaining[-1] += '\n'
                rem_chords = chords[chord_ptr:].strip()
                for word in range(len(remaining)):
                    #assign the remaining chords to the next word that
                    #hasn't been matched up with any chords yet
                    if word == 0 and rem_chords:
                        chord = rem_chords
                        if 'N' in chord.upper() and 'C' in chord.upper():
                            chord = None
                    else:
                        chord = None
                    #add spacing to words in middle
                    if remaining[word][-1] != '\n':
                        remaining[word] += ' '
                    lyrics.append(Word(chord,remaining[word]))
                #if chords remain, update their end formatting and strip formatting from last word
                chord = chords[chord_ptr:].strip()
                if not remaining and chord and not ('N' in chord.upper() and 'C' in chord.upper()):
                    lyrics[-1].word = lyrics[-1].word.strip()
                    if words[-1] == '\n' and words[-2] == '\n':
                        end_type = end_stanza
                    else:
                        end_type = end_line
                    lyrics.append(Word(chord,None,end_type))
            else:
                lyrics[-1].word += '\n'
                if chords[-1] != ' ':
                    ptr = -1
                    while chords[ptr] != ' ':
                        ptr -= 1
                    lyrics[-1].chord = chords[ptr:].strip()
            match_len += len(match.group())
        #if a small percentage of the tab was correct matches, then return error
        if match_len / len(tab) < 0.65:
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
                    elif lyric.pos == 'end_line':
                        print(' (' + lyric.chord + ')\t\n',end='')
                    elif lyric.pos == 'end_stanza':
                        print(' (' + lyric.chord + ')\t\n\n',end='')
            return lyrics
