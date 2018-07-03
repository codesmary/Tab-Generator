from __future__ import print_function
from keras.callbacks import LambdaCallback
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import numpy as np
import random
import sys
import io

file = open('tab_corpus.txt')
text = file.read()

#create a dictionary from the indeces to the models, and from the models to the indeces
chars = sorted(list(set(text)))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))

#create sequences of the models "sentences"- grab 40 character units with steps of 3 characters
maxlen = 40
step = 3
chunks = []
next_chars = []
for i in range(0, len(text) - maxlen, step):
    chunks.append(text[i: i + maxlen])
    next_chars.append(text[i + maxlen])

#create a vector, with true recorded for each occurence in the input data
x = np.zeros( (len(chunks), maxlen, len(chars)), dtype=np.bool)
y = np.zeros( (len(chunks), len(chars)), dtype=np.bool)
for i, chunk in enumerate(chunks):
    for t, char in enumerate(chunk):
        x[i, t, char_indices[char]] = 1
    y[i, char_indices[next_chars[i]]] = 1

# build the model: a single LSTM
model = Sequential([
    #batch size: number of examples used in one pass, input vector shape
    LSTM(128, input_shape=(maxlen, len(chars))),
    Dense(len(chars)), #dense layer, size of dictionary
    Activation('softmax')
])

#loss function and optimization function for rnn's with learning rate
model.compile(loss = 'categorical_crossentropy', optimizer = RMSprop(lr=0.01))

#helper function to sample an index from a probability array
def sample(probability_matrix, temperature=1.0):
    probability_matrix = np.asarray(probability_matrix).astype('float64')
    probability_matrix = np.log(probability_matrix) / temperature
    exp_preds = np.exp(probability_matrix)
    probability_matrix = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, probability_matrix, 1)
    index_of_greatest_val = np.argmax(probas)
    return index_of_greatest_val

def on_epoch_end(epoch, logs):
    # Function invoked at end of each epoch. Prints generated text.
    print('\n----- Generating text after Epoch: %d' % epoch)

    #generate a seed with a random starting index, of length maxlen
    start_index = random.randint(0, len(text) - maxlen - 1)
    for diversity in [0.2, 0.5, 1.0, 1.2]:
        print('----- diversity:', diversity)

        seed = text[start_index: start_index + maxlen]
        generated = seed
        print('----- Generating with seed: "' + seed + '"')
        sys.stdout.write(generated)

        generated_text_len = 400
        for i in range(generated_text_len):
            seed_vector = np.zeros((1, maxlen, len(chars)))
            for t, char in enumerate(seed):
                seed_vector[0, t, char_indices[char]] = 1

            #probability distribution for next character at time 0
            probability_matrix = model.predict(seed_vector, verbose=0)[0]
            #sample the next character from the probability distribution matrix, given a certain diversity
            next_index = sample(probability_matrix, diversity)
            next_char = indices_char[next_index]

            #update generated text and seed
            generated += next_char
            seed = seed[1:] + next_char

            sys.stdout.write(next_char)
            sys.stdout.flush()
        print()

print_callback = LambdaCallback(on_epoch_end=on_epoch_end)

#begin training
model.fit(x, y,
          batch_size=128,
          epochs=60,
          callbacks=[print_callback])