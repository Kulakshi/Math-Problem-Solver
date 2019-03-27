from .. import RegexPatterns
from ...Utils import util
import re
import math
import spacy
spacy_nlp = spacy.load('en_core_web_sm')

VERBS = ["find", "Find", "Solve", "solve", "Calculate", "calculate", ':', "List", "list", "elements", "element",
         "Elements", "members", "Members"]

def filter(text, type):
    # Filter from text
    text_copy = text
    output = []
    print(type, type == util.type1)
    if type == util.type1:
        equationsCard = extract_equations(text_copy, RegexPatterns.cardinality_regex)
        text_copy = removeFromText(text_copy, equationsCard)
        # print("text_copy:",  text_copy)
        subsets = extract_equations(text_copy, RegexPatterns.subset_regex)
        # print(subsets)
        text_copy = removeFromText(text_copy, subsets)
        equal_cardinalities = extract_equations(text, RegexPatterns.equal_cardinality_regex)
        text_copy = removeFromText(text_copy, equal_cardinalities)
        expressionsCard = extract_equations(text_copy, RegexPatterns.expression_regex)
        text_copy = removeFromText(text_copy, expressionsCard)
        # Further cleaning
        expressionsCard = filter_expressions_sn(expressionsCard)
        output = equationsCard + subsets + equal_cardinalities + expressionsCard
        # print(output)
    else:
        text_copy = text_copy.replace('[', '(')
        text_copy = text_copy.replace('[', '(')
        text_copy = text_copy.replace(']', ')')
        text_copy = text_copy.replace(']', ')')
        reg = re.compile(RegexPatterns.roman_numbers, re.IGNORECASE)
        results = reg.finditer(text_copy)
        if results is not None:
            for res in results:
                text_copy = text_copy.replace(res.group(), "# ")
        # print(text_copy)
        equations = extract_equations(text_copy, RegexPatterns.def_elem_regex)
        text_copy = removeFromText(text_copy, equations)
        # print(text_copy)
        # print(equations)

        for i, eqn in enumerate(equations):
            filtered_eqn = tag_based_filter_set_name_elem(eqn, RegexPatterns.def_elem_regex)
            if filtered_eqn is not None:
                equations[i] = filtered_eqn

        names = util.extract_main_set_names(equations, util.type2)

        sentences = re.split(r'[\n\r]+',text_copy)
        text_copy = remove_bullets(sentences, text_copy, names)
        # print(text_copy)
        sentences = re.split(r'[\t]+', text_copy)
        text_copy = remove_bullets(sentences, text_copy, names)

        # print(text_copy)
        expressions = extract_equations(text_copy, RegexPatterns.def_elem_exp_regex)
        # print("expressions", expressions)

        for i, expr in enumerate(expressions):
            filtered_eqn = tag_based_filter_set_name_elem(expr, RegexPatterns.def_elem_exp_regex)
            # print("FILTERD", filtered_eqn)
            if filtered_eqn is not None:
                expressions[i] = filtered_eqn
        output = equations + expressions
    return output

def removeFromText(text, equations):
    for eqn in equations:
        eqn = eqn.replace(' = ', '=')
        text = text.replace(eqn, '')
    return text

def extract_equations(text, regexstr):
    for verb in VERBS:
        if verb in text:
            text = text.replace(verb, '#')
            # text = text[text.rfind(verb)+len(verb):len(text)]
    replacement = re.compile(re.escape(' set '), re.IGNORECASE)
    text = replacement.sub(',', text)
    replacement = re.compile(re.escape(' and '), re.IGNORECASE)
    text = replacement.sub(',', text)
    replacement = re.compile(re.escape(' Venn diagram '), re.IGNORECASE)
    text = replacement.sub(',', text)
    replacement = re.compile(re.escape(' Venn '), re.IGNORECASE)
    text = replacement.sub(',', text)
    regex = re.compile(regexstr)
    text = text.replace('=', ' = ')
    output = []
    # add validations
    # print(text)
    if regexstr.startswith('(?'):
        results = regex.findall(text)
        for result in results:
            if type(result) == tuple:
                expr = result[0]
            else:
                expr = result
            expr = expr.lstrip()
            expr = expr.rstrip()
            if expr is not '':
                output.append(expr)
    else:
        results = regex.finditer(text)
        for result in results:
            expr = result.group()
            expr = expr.lstrip()
            expr = expr.rstrip()
            if expr is not '':
                output.append(expr)
    # print("RES", results)
    # print("RES", list(results))

    return output


def tag_based_filter_set_name_elem(text, regex):
    regex = re.compile(regex)
    # tokens = nltk.pos_tag(nltk.word_tokenize(text))
    spacy_tagged = spacy_nlp(text)
    tokens =[]
    for token in spacy_tagged:
        tokens.append((token.text, token.pos_))
    # print(tokens)

    if len(tokens) > 0:
        # rule1 = "NN" not in tokens[0][1] != 'NN' and tokens[0][1] != 'NNP' and tokens[0][0] != '(' and tokens[0][0] != '[' and tokens[0][0] != 'ξ'
        rule1 =  tokens[0][1] != 'NOUN' and tokens[0][0] != '(' and tokens[0][0] != '[' and tokens[0][0] != 'ξ'
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
            # print('tag_based_filter_set_name_elem',text)
            return None
        else:
            return text


def filter_expressions_sn(expressions):
    regex = re.compile(RegexPatterns.expression_regex)
    for i, expression in enumerate(expressions):
        count = 0
        have_brackets = False
        for j, letter in enumerate(expression):
            if letter == '(':
                count += 1
                have_brackets = True
            if letter == ')':
                count -= 1
            if have_brackets and count == 0:
                new_expr1 = expression[0:j + 1]
                new_expr2 = expression[j + 1:len(expression)]
                if regex.match(new_expr1):
                    expressions[i] = new_expr1
                    # print("NEW FILTERED EXPR", new_expr1)

                if len(new_expr2) < 1:
                    break
                expr = extract_equations(new_expr2, RegexPatterns.expression_regex)
                if len(expr) > 0:
                    expr = filter_expressions_sn(expr)
                    expressions = expressions + expr
                    # print("NEW EXPR LIST")
                    # print(expressions)
                    break
    return expressions


def remove_bullets(sentences, text, setNames):
    not_bullets = re.compile(r'[∩∪ξ\'\-\(]+')
    for sent in sentences:
        sent = sent.lstrip()
        # print(sent)
        candits = re.split(r'\)', sent)
        if len(candits) > 0:
            is_a_set = False
            for set in setNames:
                if set is not None:
                    # print(set, candits)
                    if set in candits[0]:
                        is_a_set = True
            if not is_a_set:
                text = text.replace(candits[0] + ')', ',')
                text = text.replace(candits[0] + '.', ',')

    return text


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
