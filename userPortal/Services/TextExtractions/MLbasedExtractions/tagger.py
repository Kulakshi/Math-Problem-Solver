import nltk
from sklearn.model_selection import train_test_split
import os
import json
import codecs
import re
import pycrfsuite
import spacy
from keras.models import load_model
import numpy as np
from sklearn.metrics import classification_report
import joblib

from collections import Counter
import string

paths = [r'F:\Academic\ML\Eval\Set1_myData\\',
         r'F:\Academic\ML\Eval\Set2_semEval\\',
         r'F:\Academic\ML\Eval\Set3_mix\\']

features = []
data = []
def train():
    for path, subdirs, files in os.walk(paths[1]):
        for filename in files:
            # print(filename)
            f=codecs.open("F:\Academic\ML\SemEvelData\conll\\"+filename,encoding='utf-8')
            line = f.readline()
    ##        print(line)
            texts = []
            while line :
    ##            print("While" + filename)
                if(len(line.split(' ')) > 1):
                    line = line.replace('\n', '')
                    line = line.replace('\r', '')
                    word = line.split(' ')[0]
                    tag = line.split(' ')[1]
                    if tag == 'B-e_1' or tag == 'I-e_1':
                        tag = 'e_1'
                    text = (word, tag)
                    texts.append(text)
    ##                print(text)
                line = f.readline()
            features.append(texts)


    for i, doc in enumerate(features):
        # Obtain the list of tokens in the document
        tokens = [t.encode('utf-8') for t, label in doc]
    ##    print(tokens)
        # Perform POS tagging
        for i, token in enumerate(tokens):
            tokens[i] = str(tokens[i])
        tagged = nltk.pos_tag(tokens)
        # Take the word, POS tag, and its label
        data.append([(w, pos, label) for (w, label), (word, pos) in zip(doc, tagged)])


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


def hasLetters(inputString):
    hasLetters = re.search('[a-zA-Z]', inputString)
    return hasLetters is not None


def hasPunctuation(inputString):
    return any(char in string.punctuation for char in inputString)


def getWordPattern(inputString):
    pattern = ''
    for c in inputString:
        if c.isalpha():
            if c.isupper():
                pattern = pattern + 'A'
            else:
                pattern = pattern + 'a'
        elif c.isdigit():
            pattern = pattern + '0'
        else:
            pattern = pattern + c
    return pattern


def getSummarizedWordPattern(inputString):
    pattern = getWordPattern(inputString)
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if i > 0 and (c == 'd' or c == 'X' or c == 'x'):
            if pattern[i - 1] == c:
                pattern = pattern[:i - 1] + pattern[i:]
            else:
                i = i + 1
        else:
            i = i + 1
    return pattern


def word2features(doc, i):
    token = str(doc[i][0])
    postag = doc[i][1]
    shape = doc[i][2]
    features = []
    ldelim = ['(', '[', '{', '|']
    rdelim = [')', ']', '}', '|']
    r = re.compile(r'[Xx]+')
    tokens = [word for word, pos, shape in doc]
    bigrm = list(nltk.bigrams(tokens))
    ##    print(token.encode('utf-8'))
    shapeDetail = (len(str(r.match(str(token)).group())) == len(str(token))) if (
                r.match(str(token)) is not None) else False
    chNgrams = []
    doc_chars = [c for w in tokens for c in str(w)]
    for j, c in enumerate(set(token)):
        chNgrams.append('token' + str(j) + 'thCh=' + str(c))
        chNgrams.append('token' + str(j) + 'thChFerq=' + str(Counter(doc_chars)[c]))
        if j > 0:
            chNgrams.append('token' + str(j - 1) + "_" + str(j) + 'thCh=' + str(token[j - 1]) + "" + str(c))
    if len(token) > 0:
        # Common features for all words

        features = [
            'bias',
            'token=' + token,
            "UnigramFreq=" + str(Counter(tokens)[token]),

            'word.isChar=%s' % (len(token) == 1),

            'token.isupper=%s' % token.isupper(),
            'token.islower=%s' % token.islower(),
            'token.isFirstLetterCapital=%s' % token[0].isupper(),
            'token.isNonInitCapitals=%s' % ((len([l for l in token[1:] if l.isupper()]) > 0) and token[0].islower()),

            'token.isalpha=%s' % token.isalpha(),
            'token.isdigit=%s' % token.isdigit(),
            'token.isldelim=%s' % (token in ldelim),
            'token.isrdelim=%s' % (token in rdelim),
            'token.isMixofLettersDigits=%s' % (hasNumbers(token) and hasLetters(token)),
            'token.hasPunctuation=%s' % hasPunctuation(token),
            'token.wordPattern=' + shape,
            'token.wordPatternSum=' + getSummarizedWordPattern(shape),

            'token[-3:]=' + token[-3:],
            'token[-2:]=' + token[-2:],

            'postag=' + postag,
        ]  # + chNgrams

        # Features for token that are not
        # at the beginning of a document
        if i > 0 and len(str(doc[i - 1][0])) > 0:
            token1 = str(doc[i - 1][0])
            postag1 = str(doc[i - 1][1])
            shape1 = doc[i - 1][2]
            features.extend([
                '-1:token=' + token1,
                "-1:Bigram=" + token1 + " " + token,
                "-1:UnigramFreq=" + str(Counter(tokens)[token1]),

                '-1:token.isChar=%s' % (len(token1) == 1),

                '-1:token.isupper=%s' % token1.isupper(),
                '-1:token.islower=%s' % token1.islower(),
                '-1:token.isNonInitCapitals=%s' % (
                            (len([l for l in token1[1:] if l.isupper()]) > 0) and token1[0].islower()),
                '-1:token.isFirstLetterCapital=%s' % token1[0].isupper(),

                '-1:token.isalpha=%s' % token1.isalpha(),
                '-1:token.isdigit=%s' % token1.isdigit(),
                '-1:token.isldelim=%s' % (token1 in ldelim),
                ##                '-1:token.isrdelim=%s' % (token1 in rdelim),
                '-1:token.isMixofLettersDigits=%s' % (hasNumbers(token1) and hasLetters(token1)),
                '-1:token.hasPunctuation=%s' % hasPunctuation(token1),
                '-1:token.wordPattern=' + shape1,
                '-1:token.wordPatternSum=' + getSummarizedWordPattern(shape1),

                '-1:token[-3:]=' + token1[-3:],
                '-1:token[-2:]=' + token1[-2:],

                '-1:postag=' + postag1,
            ])
        else:
            # Indicate that it is the 'beginning of a document'
            features.append('BOS')

        if i > 1 and len(str(doc[i - 2][0])) > 0:
            token1 = str(doc[i - 1][0])
            token2 = str(doc[i - 2][0])
            postag2 = str(doc[i - 2][1])
            shape2 = doc[i - 2][2]
            features.extend([
                '-2:token=' + token2,
                "-2:Bigram=" + token2 + " " + token1,
                "-2:UnigramFreq=" + str(Counter(tokens)[token2]),

                '-2:token.isChar=%s' % (len(token2) == 1),

                '-2:token.isupper=%s' % token2.isupper(),
                '-2:token.islower=%s' % token2.islower(),
                '-2:token.isNonInitCapitals=%s' % (
                            (len([l for l in token2[1:] if l.isupper()]) > 0) and token2[0].islower()),
                '-2:token.isFirstLetterCapital=%s' % token2[0].isupper(),

                '-2:token.isalpha=%s' % token2.isalpha(),
                '-2:token.isdigit=%s' % token2.isdigit(),
                '-2:token.isldelim=%s' % (token2 in ldelim),
                ##                '-2:token.isrdelim=%s' % (token2 in rdelim),
                '-2:token.isMixofLettersDigits=%s' % (hasNumbers(token2) and hasLetters(token2)),
                '-2:token.hasPunctuation=%s' % hasPunctuation(token2),
                '-2:token.wordPattern=' + shape2,
                '-2:token.wordPatternSum=' + getSummarizedWordPattern(shape2),

                '-2:token[-3:]=' + token2[-3:],
                '-2:token[-2:]=' + token2[-2:],

                '-2:postag=' + postag2,

                ##
            ])
        # Features for words that are not
        # at the end of a document
        if i < len(doc) - 1 and len(str(doc[i + 1][0])) > 0:
            token1 = str(doc[i + 1][0])
            postag1 = str(doc[i + 1][1])
            shape1 = doc[i + 1][2]
            features.extend([
                "+1:Bigram=" + token + " " + token1,
                ##                "+1:BigramFreq=" + str(Counter(bigrm)[(token,token1)]),
                '+1:token=' + token1,
                "+1:UnigramFreq=" + str(Counter(tokens)[token1]),

                '+1:token.isChar=%s' % (len(token1) == 1),
                '+1:token.isupper=%s' % token1.isupper(),
                '+1:token.islower=%s' % token1.islower(),
                '+1:token.isNonInitCapitals=%s' % (
                            (len([l for l in token1[1:] if l.isupper()]) > 0) and token1[0].islower()),
                '+1:token.isFirstLetterCapital=%s' % token1[0].isupper(),

                '+1:token.isalpha=%s' % token1.isalpha(),
                '+1:token.isdigit=%s' % token1.isdigit(),
                ##                '+1:token.isldelim=%s' % (token1 in ldelim),
                '+1:token.isrdelim=%s' % (token1 in rdelim),
                '+1:token.isMixofLettersDigits=%s' % (hasNumbers(token1) and hasLetters(token1)),
                '+1:token.hasPunctuation=%s' % hasPunctuation(token1),
                '+1:token.wordPattern=' + shape1,
                '+1:token.wordPatternSum=' + getSummarizedWordPattern(shape1),

                '+1:token[-3:]=' + token1[-3:],
                '+1:token[-2:]=' + token1[-2:],

                '+1:postag=' + postag1,
            ])
        else:
            # Indicate that it is the 'end of a document'
            features.append('EOS')

        if i < len(doc) - 2 and len(str(doc[i + 2][0])) > 0:
            token1 = str(doc[i + 1][0])
            token2 = str(doc[i + 2][0])
            shape2 = doc[i + 2][2]
            postag2 = str(doc[i + 2][1])
            features.extend([
                '+2:token=' + token2,
                "+2:UnigramFreq=" + str(Counter(tokens)[token2]),
                "+2:Bigram=" + token1 + " " + token2,

                '+2:token.isChar=%s' % (len(token2) == 1),

                '+2:token.isupper=%s' % token2.isupper(),
                '+2:token.islower=%s' % token2.islower(),
                '+2:token.isNonInitCapitals=%s' % (
                            (len([l for l in token2[1:] if l.isupper()]) > 0) and token2[0].islower()),
                '+2:token.isFirstLetterCapital=%s' % token2[0].isupper(),

                '+2:token.isalpha=%s' % token2.isalpha(),
                '+2:token.isdigit=%s' % token2.isdigit(),
                ##                '+1:token.isldelim=%s' % (token2 in ldelim),
                '+1:token.isrdelim=%s' % (token2 in rdelim),
                '+2:token.isMixofLettersDigits=%s' % (hasNumbers(token2) and hasLetters(token2)),
                '+2:token.hasPunctuation=%s' % hasPunctuation(token2),
                '+2:token.wordPattern=' + shape2,
                '+2:token.wordPatternSum=' + getSummarizedWordPattern(shape2),

                '+2:token[-3:]=' + token2[-3:],
                '+2:token[-2:]=' + token2[-2:],

                '+2:postag=' + postag2,
                ##
            ])
    return features


#=======================================
# def word2features(doc, i):
#     token = doc[i][0]
#     postag = doc[i][1]
#     shape = doc[i][2]
#     features = []
#     if len(token)>0:
#         # print(token)
#         # Common features for all words
#         features = [
#             'bias',
#             'token.lower=' + token.lower(),
#             'token[-3:]=' + token[-3:],
#             'token[-2:]=' + token[-2:],
#             'token.isupper=%s' % token.isupper(),
#     ##        'word.istitle=%s' % token.istitle(),
#             'token.isdigit=%s' % token.isdigit(),
#             'postag=' + postag,
#             'shape=' + shape,
#     ##        'token.contains=%s' % ('=' in token), <- reduced accuracy (.96 to .94)
#             'word.isFirstLetterCapital=%s' %  token[0].isupper,
#             'word.isChar=%s' % (len(token)==1),
#             'word.isLong=%s' % (len(token)>=5)
#         ]
#
#         # Features for token that are not
#         # at the beginning of a document
#         if i > 0 and len(doc[i-1][0]) > 0:
#             token1 = doc[i-1][0]
#             postag1 = doc[i-1][1]
#             shape1 = doc[i-1][2]
#             features.extend([
#                 '-1:token.lower=' + token1.lower(),
#     ##            '-1:token.istitle=%s' % token1.istitle(),
#                 '-1:token.isupper=%s' % token1.isupper(),
#                 '-1:token.isdigit=%s' % token1.isdigit(),
#                 '-1:postag=' + postag1,
#                 '-1:shape=' + shape1,
#                 '-1:token.isFirstLetterCapital=%s' % token1[0].isupper,
#                 '-1:token.contains=%s' % ('=' in token1),
#     ##            '-1:token.contains=%s' % ('∩' in token1),
#     ##            '-1:token.contains=%s' % ('∪' in token1),
#                 '-1:token.contains=%s' % ('n(' in token1),
#                 '-1:token.isChar=%s' % (len(token1)==1),
#                 '-1:postag=' + postag1,
#             ])
#         else:
#             # Indicate that it is the 'beginning of a document'
#             features.append('BOS')
#
#         # Features for words that are not
#         # at the end of a document
#         if i < len(doc)-1 and len(doc[i+1][0]) > 0:
#             token1 = doc[i+1][0]
#             postag1 = doc[i+1][1]
#             shape1 = doc[i+1][2]
#             features.extend([
#                 '+1:token.lower=' + token1.lower(),
#     ##            '+1:token.istitle=%s' % token1.istitle(),
#                 '+1:token.isupper=%s' % token1.isupper(),
#                 '+1:token.isdigit=%s' % token1.isdigit(),
#                 '+1:postag=' + postag1,
#                 '+1:shape=' + shape1,
#                 '+1:token.contains=%s' % ('=' in token1),
#                 '+1:token.contains=%s' % ('.' in token1),
#     ##            '+1:token.contains=%s' % ('∪' in token1),
#                 '+1:token.isFirstLetterCapital=%s' % token1[0].isupper,
#                 '+1:token.isChar=%s' % (len(token1)==1)
#             ])
#         else:
#             # Indicate that it is the 'end of a document'
#             features.append('EOS')
#
#     return features




# A function for extracting features in documents
def extract_features(doc):
    return [word2features(doc, i) for i in range(len(doc))]

# A function fo generating the list of labels for each document
def get_labels(doc):
    return [label for (token, postag, label) in doc]








#=======================================
def load_crf():
    # tagger = pycrfsuite.Tagger()
    # tagger.open('F:\Academic\crf.model')
    tagger = joblib.load('F:\Academic\ML\Eval\converters\CRFdump')
    return tagger
def test():
    X = [extract_features(doc) for doc in data]
    y = [get_labels(doc) for doc in data]
    tagger = load_crf()
    # tagger.open('F:\Academic\crf.model')
    # tagger.open('F:\Academic\ML\Eval\converters\Mix_data\ML1\crf.model')

    y_pred = [tagger.tag(xseq) for xseq in X]

    # Let's take a look at a random sample in the testing set
    ##i = 4
    ##for x, y in zip(y_pred[i], [x[1].split("=")[1] for x in X_test[i]]):
    ##    print("%s (%s)" % (y.encode('utf-8'), x.encode('utf-8')))


    #=======================================
    # Create a mapping of labels to indices
    ##labels = {"B-e_1": 1, "I-e_1": 1,"O": 0}
    labels = {"e_1": 1, "O": 0}

    # Convert the sequences of tags into a 1-dimensional array

    predictions = np.array([labels[tag] for row in y_pred for tag in row])
    truths = np.array([labels[tag] for row in y for tag in row])


    # Print out the classification report
    print(classification_report(
        truths, predictions,
    ##    target_names=["B-e_1", "I-e_1","O"]))
        target_names=["e_1", "O"]))

def preprocess(document):
    dotWord = re.compile(r'([.])\w+')
    document = addPostSpaces(document, dotWord)

    equationWord = re.compile(r'([=])[\w\d]+')
    document = addPostSpaces(document, equationWord)

    equationWord = re.compile(r'([,])[\w\d]+')
    document = addPostSpaces(document, equationWord)

    equationWord = re.compile(r'[\w\d\)\]]+([=])')
    document = addPreSpaces(document,equationWord)

    equationWord = re.compile(r'[\w\d\)\]]+([,])')
    document = addPreSpaces(document,equationWord)

    return document

def addPostSpaces(document, regex):
    result = regex.search(document)
    finalStr = ''
    rest = document
    while result is not None:
        i = result.start()
        finalStr += rest[0:i + 1] + ' '
        rest = rest[i + 1:len(rest)]
        result = regex.search(rest)
    finalStr += rest
    return finalStr


def addPreSpaces(document, regex):
    result = regex.search(document)
    finalStr = ''
    rest = document
    while result is not None:
        i = result.end()
        finalStr += rest[0:i - 1] + ' '
        rest = rest[i - 1:len(rest)]
        result = regex.search(rest)
    finalStr += rest
    return finalStr

def tag(document):
    document = preprocess(document)
    words = nltk.word_tokenize(document)
    # tags = nltk.pos_tag(words)
    sent = ' '.join(words)

    spacy_nlp = spacy.load('en_core_web_sm')
    spacy_tagged = spacy_nlp(sent)
    tags = []
    for token in spacy_tagged:
        tags.append((token.text, token.pos_,token.shape_))

    tagger = pycrfsuite.Tagger()
    tagger.open('F:\Academic\ML\Eval\converters\crf3.model')
    # tagger.open('F:\Academic\ML\Eval\converters\99Acc_myData_3Labels\crf.model')

    y_pred = tagger.tag(extract_features(tags))
    taggedText = []
    for (word, pos, shape), tag in zip(tags, y_pred):
        taggedText.append((word, tag))
    return taggedText