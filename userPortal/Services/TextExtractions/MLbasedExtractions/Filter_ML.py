from . import tagger, parser, rnntagger


def filter(text):
    taggedText = tagger.tag(text)
    # taggedText = rnntagger.tag(text)
    exps = readTaggedText(taggedText, 3)


    return exps

def readTaggedText(taggedText, numOfLabels = 2):
    exps = []
    length = len(taggedText)
    i = 0
    while i < length:
        if taggedText[i][1] == 'e_1' if numOfLabels == 2 else 'B-e_1':
            exp = ''
            efs = False
            while i < len(taggedText) and taggedText[i][1] != 'O':
                exp += taggedText[i][0]
                if i + 1 < len(taggedText):
                    i += 1
                else:
                    efs = True
                    break
            if exp != '' : exps.append(exp)
            if (efs):
                break
        i = i + 1
    return exps