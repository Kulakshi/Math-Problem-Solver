import nltk
import re
from .Utils import util
roman_numbers = re.compile(r'\((?=[MDCLXVI])M*(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})\)')
simple_letter =  re.compile(r'[a-z]')

def change_alt_chars(text):
    text = text.replace('´', '\'')
    text = text.replace('’', '\'')
    text = text.replace('′', '\'')
    text = text.replace('^', '∩')
    text = text.replace('\n', ' and ')
    text = text.replace('\t', ' and ')
    text = text.replace('    ', ' and ')
    return text


def tag_based_filter_set_name_elem(text,regex):
    regex = re.compile(regex)
    tokens = nltk.pos_tag(nltk.word_tokenize(text))

    if len(tokens) > 0 :
        rule1 = "NN" not in tokens[0][1] != 'NN' and tokens[0][1] != 'NNP' and tokens[0][0] != '(' and tokens[0][0] != '[' and tokens[0][0] != 'ξ'
        rule2 = tokens[0][0] != 'A'
        rule3 = tokens[0][1] is not None
        rule4 = True
        if rule2 and rule3:
            rule4 = tokens[0][1] != '∪' and tokens[0][1] != '∩' and tokens[0][1] != '-' and tokens[0][1] != '\''

        if (rule1 and rule2 and rule4):
            words = text.split(' ')
            truncated_text = ' '.join(words[1: len(words)])
            if (not regex.match(text)) or regex.match(truncated_text):
                return tag_based_filter_set_name_elem(truncated_text, regex)
            return text
        else:
            return text



def fill_elem_sequences(equation):
    name = equation[0: equation.find("=")]
    elements = extract_elements_from_eqn(equation)
    # elements = elements_text.split(',')
    updated_elements = elements
    isNumbers = True
    isLetters = True
    for i, element in enumerate(elements):
        element = element.lstrip()
        elements[i] = element.rstrip()
        regex = re.compile(r'\.+')
        shrinkedPart = []
        if not regex.match(element) and not re.compile(r'\d+').match(element):
            isNumbers = False
        if not regex.match(element) and not re.compile(r'[A-Za-z]{1}').match(element):
            isLetters = False
        if regex.match(element):
            if elements[i - 1] is not None:
                if isNumbers:
                    if elements[i - 1] is not None and elements[i - 2] is not None:
                        gap = abs(int(elements[i - 2]) - int(elements[i - 1]))
                        if (elements[i + 1] is not None):
                            if int(elements[i + 1]) > int(elements[i - 1]):
                                j = int(elements[i - 1]) + gap
                                while j < int(elements[i + 1]):
                                    shrinkedPart.append(str(j))
                                    j = j + gap
                            if int(elements[i + 1]) < int(elements[i - 1]):
                                j = int(elements[i - 1]) - gap
                                while j > int(elements[i + 1]):
                                    shrinkedPart.append(str(j))
                                    j = j - gap
                if isLetters:
                    if elements[i - 1] is not None and elements[i - 2] is not None:
                        gap = 0
                        try:
                            gap = abs(ord(elements[i - 2]) - ord(elements[i - 1]))
                        except:
                            print("Not letters")
                            break
                        print("GAP :", gap)
                        if (elements[i + 1] is not None):
                            if ord(elements[i + 1]) > ord(elements[i - 1]):
                                j = ord(elements[i - 1]) + gap
                                while j < ord(elements[i + 1]):
                                    shrinkedPart.append(chr(j))
                                    j = j + gap
                            if ord(elements[i + 1]) < ord(elements[i - 1]):
                                j = ord(elements[i - 1]) - gap
                                while j > ord(elements[i + 1]):
                                    shrinkedPart.append(chr(j))
                                    j = j - gap
                print(updated_elements)
                print("SHRINKED : ", shrinkedPart)
                updated_elements = updated_elements[0:i] + shrinkedPart + elements[i + 1:len(elements)]
    return name + '= {' + ','.join(updated_elements) + "}"

def find_universal_set_symbol(equations, qtext, type):
    single_sets_eqns = equations
    single_set_names = extract_main_set_names(single_sets_eqns, type)
    print(single_set_names)
    names = []

    for eqn in equations:
        if (type == util.type1):
            names.append(extract_name_from_sn(eqn))
        if (type == util.type2):
            names.append(extract_name_from_elem(eqn))
    len_names = len(names)
    for i in range(len_names):
        name = names[i].replace(' ','')
        if name in qtext:
            names.append(name)

    all = '#'.join(names)
    all = all.replace(' ', '#')
    all = all.replace("∩", "#")
    all = all.replace("-", "#")
    all = all.replace("∪", "#")
    all = all.replace("'", "#")
    all = all.replace(")", "#")
    all = all.replace("(", "#")
    all = all.replace("-", "#")
    all = all + '#'
    print(all)

    candidiate_set_indexes = []
    candidiate_set_sizes = []
    candidiate_set_names = []
    candidiate_set_elements = []
    max_size = 0

    for set in single_set_names:
        for i, eqn in enumerate(equations):
            if set in eqn:
                size = None
                elements = None
                try:
                    if (type == util.type1):
                        size = int(eqn[eqn.find("=") + 1:len(eqn)])
                    else:
                        elements = extract_elements_from_eqn(eqn)
                        size = len(elements)
                except:
                    print("value error")
                if (size is not None):
                    if max_size < size:
                        max_size = size

    print("FINDING UNIVERSAL SET")
    # Find universal set based on given set names
    for set in single_set_names:
        print("SET : ",set)
        num_occurences = all.count(set.replace(' ', '#'))
        print("#Occur. : ", num_occurences)
        if (num_occurences == 1):
            for i, eqn in enumerate(equations):
                if set in eqn:
                    size = None
                    elements = None
                    try:
                        if (type == util.type1):
                            size = int(eqn[eqn.find("=") + 1:len(eqn)])
                        else:
                            elements = extract_elements_from_eqn(eqn)
                            # elements = elements_text.split(',')
                            size = len(elements)
                    except:
                        print("value error")
                    if (size is not None):
                        candidiate_set_indexes.append(i)
                        candidiate_set_sizes.append(size)
                        candidiate_set_names.append(set.strip())
                        candidiate_set_elements.append(elements)

    print(candidiate_set_names)
    print(candidiate_set_sizes)
    print(max_size)
    if len(candidiate_set_indexes) > 1:
        max_size = max(max(candidiate_set_sizes),max_size)
        uni_set_in_elems = True
        for i, size in enumerate(candidiate_set_sizes):
            if size == max_size:
                print("QQQ")
                if (type == util.type2):
                    print(candidiate_set_names[i])
                    for j, elems in enumerate(candidiate_set_elements):
                        print(elems, candidiate_set_elements[i])
                        if not contains(candidiate_set_elements[i], elems):
                            uni_set_in_elems = False
                if uni_set_in_elems:
                    equations[candidiate_set_indexes[i]] = equations[candidiate_set_indexes[i]].replace(
                        candidiate_set_names[i], 'ξ')
                else:
                    all_elements = []
                    for list in candidiate_set_elements:
                        for elem in list:
                            if elem not in all_elements:
                                all_elements.append(elem)
                    equations.append("ξ = {" + ','.join(all_elements) + "}")
                return equations
    else:
        if len(candidiate_set_indexes) > 0:
            if max_size <= candidiate_set_sizes[0]:
                equations[candidiate_set_indexes[0]] = equations[candidiate_set_indexes[0]].replace(
                    candidiate_set_names[0], 'ξ')

    return equations


def extract_main_set_names(main_set_eqns, type):
    names = []
    for expression in main_set_eqns:
        print(type)
        name = ''
        if type == util.type1:
            name = extract_name_from_sn(expression)
        if type == util.type2:
            name = extract_name_from_elem(expression)
        names.append(name.replace("\'", ''))
    return names


def extract_name_from_sn(expression):
    if '|' in expression:
        return expression[expression.find("|") + 1:expression.rfind("|")]
    else:
        return expression[expression.find("(") + 1:expression.rfind(")")]


def extract_name_from_elem(expression):
    return expression[0: expression.find("=")]


def contains(super_list, sub_list):
    if super_list is not None and sub_list is not None:
        for item in sub_list:
            if item not in super_list:
                return False
    else:
        return False
    return True


def extract_elements_from_eqn(equation):
    if "=" in equation:
        elements_text = equation[equation.find("="): len(equation)]
        if "{" in elements_text and "}" in elements_text:
            elements_text = elements_text[elements_text.find("{") + 1:elements_text.rfind("}")]
        if "(" in elements_text and ")" in elements_text:
            elements_text = elements_text[elements_text.find("(") + 1:elements_text.rfind(")")]
        if "[" in elements_text and "]" in elements_text:
            elements_text = elements_text[elements_text.find("[") + 1:elements_text.rfind("]")]
        # region.elements = elements_text.split(',')
        elements = elements_text.split(',')
        for i, element in enumerate(elements):
            # print(elements)
            element = element.lstrip()
            elements[i] = element.rstrip()
        return elements


def filter_expressions_elem(text, setDetails):
    capitals = re.compile(r'([A-Z])\w*')
    operators = re.compile(r'[ξ∪∩\-\'\(\)\[\]]')
    if (capitals.match(text) or operators.search(text)):
        existing_set = False
        for set in setDetails:
            if set.name in text:
                existing_set = True
                break
        if not existing_set:
            return False
        return True
    return False