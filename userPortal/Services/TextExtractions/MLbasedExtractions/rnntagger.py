import numpy as np
from keras.preprocessing.sequence import pad_sequences
import spacy
spacy_nlp = spacy.load('en_core_web_sm')

import json
import os
from keras.models import load_model

# ======================
# Read data from csv
# ======================
def collectExpressions(taggedText):
    exps = []
    length = len(taggedText)
    i = 0
    while i < length:
        if taggedText[i][1] == 'B-e_1':
            exp = ''
            efs = False
            while i < len(taggedText) and taggedText[i][1] != 'O':
                exp += taggedText[i][0]
                if i + 1 < len(taggedText):
                    i += 1
                    if (taggedText[i][1] == 'B-e_1'):
                        break
                else:
                    efs = True
                    break
            if exp != '': exps.append(exp)
            if (efs):
                break
        i = i + 1
    return exps

def tag(text):
    spacy_tagged = spacy_nlp(text)
    words = []
    for token in spacy_tagged:
        words.append(token.text)
    word2idx = {}
    print(words)
    if os.path.isfile('F:\Academic\ML\Eval\converters\word2idx.json'):
        with open('F:\Academic\ML\Eval\converters\word2idx.json') as json_data:
            word2idx = json.load(json_data)
            for i, w in enumerate(words):
                if w not in word2idx.keys():
                    len_keys = len(word2idx.keys())
                    word2idx.update({w: len_keys})
    else:
        word2idx = {w: i for i, w in enumerate(words)}

    idx2word = {i: w for w, i in word2idx.items()}

    max_len_char = 15
    max_len = 50
    #
    # word2idx = {w: i + 2 for i, w in enumerate(words)}
    word2idx["UNK"] = 1
    word2idx["PAD"] = 0
    X_word = [word2idx[w] for w in words]
    X_word = pad_sequences(maxlen=max_len, sequences=[X_word], value=word2idx["PAD"], padding='post', truncating='post')
    chars = set([w_i for w in words for w_i in str(w)])
    char2idx = {c: i + 2 for i, c in enumerate(chars)}
    char2idx["UNK"] = 1
    char2idx["PAD"] = 0

    X_char = []
    sent_seq = []
    for i in range(max_len):
        word_seq = []
        for j in range(max_len_char):
            try:
                word_seq.append(char2idx.get(words[i][j]))
            except:
                word_seq.append(char2idx.get("PAD"))
        sent_seq.append(word_seq)
    X_char.append(np.array(sent_seq))


    model = load_model('F:\Academic\ML\Eval\converters\CH-model-Acc91')

    y_pred = model.predict([X_word, np.array(X_char).reshape((len(X_char), max_len, max_len_char))])

    idx2tag = {1: 'B-e_1', 2: 'O', 3: 'I-e_1', 0: 'PAD'}

    tagged_text = []
    for i, prob in enumerate(y_pred):
        p = np.argmax(prob, axis=-1)
        pred_tl = []
        for w, pred in zip(X_word[i], p):
            if w != 0:
                pred_tl.append((idx2word[w], idx2tag[pred]))
            tagged_text.append(pred_tl)

    return tagged_text[0]