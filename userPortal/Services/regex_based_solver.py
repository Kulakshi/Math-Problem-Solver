import re
from . import dataCollections as dataCollector
from . import solvers
from . import Validator
from . import input_formatter
from .Utils import util

cardinality_regex = r'[Nn]{0,1}[ ]*(\(([A-Za-z∩∪ξ\-\(\)\'\ ]+)\))[ ]*=[ ]*[-]{0,1}[ ]*\d+|\|([A-Za-z∩∪ξ\-\(\)\'\ ]+)\|[ ]*=[ ]*[-]{0,1}\d+'
cardinality_regex_relaxed = r'[Nn]{1}[ ]*([\(\[\|]([A-Za-z∩∪ξ\-\(\)\'\ ]+?)[\)\]\}\|]?)[ ]*=?[ ]*[-]{0,1}[ ]*\d+|\|([A-Za-z∩∪ξ\-\(\)\'\ ]+)\|[ ]*=?[ ]*[-]{0,1}\d+'
expression_regex = r'[Nn][ ]*([\(\[]([A-Za-z∩∪ξ\-\(\)\'\ ]+)[\)\]])|\|([A-Za-z∩∪ξ\-\(\)\'\ ]+)\|'
def_elem_regex = r'(ξ|[A-Za-z∩∪\-\(\)\'\ ]+) *= *[\{\(\[][\w,. ]*[\)\}\]]'
def_elem_exp_regex = r'([A-Za-z∩∪ξ\-\(\)\'\ ]+) *'
left_subset_regex = r'[A-Za-z∩∪\']+ *[⸦⊃] *[A-Za-z∩∪ξ]+'
equal_cardinality_regex = r'[Nn][ ]*(\(([A-Za-z∩∪ξ\-\(\)\'\ ]+)\))[ ]*=[ ]*[Nn][ ]*(\(([A-Za-z∩∪ξ\-\(\)\'\ ]+)\))|\|[ ]*(([A-Za-z∩∪ξ\-\(\)\'\ ]+))\|([ ]*=[ ]*\|[ ]*(([A-Za-z∩∪ξ\-\(\)\'\ ]+))\|)*'
roman_numbers = r'\((?=[MDCLXVI])M*(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})\)'

EQUAL_CAR_SET = '<EQL>'


def handle(text):
    info_type = text["info_type"]
    ques_type = text["ques_type"]

    text["info"] = input_formatter.change_alt_chars(text["info"])
    text["ques"] = input_formatter.change_alt_chars(text["ques"])

    if info_type == util.type2 :
        text["info"] = text["info"].replace('[', '(')
        text["ques"] = text["ques"].replace('[', '(')
        text["info"] = text["info"].replace(']', ')')
        text["ques"] = text["ques"].replace(']', ')')


    if ques_type == util.type2:
        reg = re.compile(roman_numbers, re.IGNORECASE)
        results = reg.finditer(text["ques"])
        if results is not None:
            for res in results:
                text["ques"] = text["ques"].replace(res.group(), "# ")

    if (text["info"] is not None or text['info'] is not ''):
        if info_type == util.type1:
            equations = extract_equations(text["info"], cardinality_regex)

            subsets = extract_equations(text["info"], left_subset_regex)
            equal_cardinalities = extract_equations(text["info"], equal_cardinality_regex)

            equations = equations + getEqualCardinalitySetData_sn(equal_cardinalities)
            equations = equations + getSubsetData_sn(subsets)

            if 'ξ' not in text['info'] and len(equations) > 1:
                equations = input_formatter.find_universal_set_symbol(equations, text["ques"], info_type)

            setDetails = getSetDetails_type_sn(equations, '')
            # for set in setDetails:
            #     print(set.name)
            #     print(set.size)



        elif info_type == util.type2:
            equations = extract_equations(text["info"], def_elem_regex)

            for i, eqn in enumerate(equations):
                filtered_eqn = input_formatter.tag_based_filter_set_name_elem(eqn, def_elem_regex)
                if filtered_eqn is not None:
                    equations[i] = filtered_eqn
                equations[i] = input_formatter.fill_elem_sequences(equations[i])

            e1 = equations.copy()
            global single_set_names
            single_set_names = []
            names = input_formatter.extract_main_set_names(equations, util.type2)

            for name in names:
                name = clean_operators_and_outer_apaces(name, '#')
                new_names = name.split('#')
                for new_name in new_names:
                    if new_name not in single_set_names:
                        single_set_names.append(new_name)

            if 'ξ' not in text['info'] and len(equations) > 1:
                equations = input_formatter.find_universal_set_symbol(equations, text["ques"], info_type)


            setDetails = getSetDetails_type_elem(equations)

        else:
            print("ERROR : INVALID INFO TYPE")
            return "ERROR : INVALID INFO TYPE"
    else:
        return "ERROR : FILL REQUIRED FIELDS"

    infoOb = dataCollector.info(setDetails)

    if (text["info"] is not None or text['ques'] is not ''):
        if ques_type == util.type1:
            expressions = extract_equations(text["ques"], expression_regex)
            expressions = filter_expressions_sn(expressions)
            qSets = getSetDetails_type_sn(expressions, text["ques"])
        elif info_type == util.type2:

            # handle bullets
            sentences = re.split(r'[\n\r]+', text['ques'])
            text['ques'] = remove_bullets(sentences, text['ques'], setDetails)
            sentences = re.split(r'[\t]+', text['ques'])
            text['ques'] = remove_bullets(sentences, text['ques'], setDetails)

            expressions = extract_equations(text["ques"], def_elem_exp_regex)

            for i, expr in enumerate(expressions):
                filtered_eqn = input_formatter.tag_based_filter_set_name_elem(expr, def_elem_exp_regex)
                if filtered_eqn is not None:
                    expressions[i] = filtered_eqn

            items_to_remove = []
            for i, expr in enumerate(expressions):
                # print(expr)
                if (filter_expressions_elem(expr, setDetails) is False):
                    items_to_remove.append(expr)

            for item in items_to_remove:
                expressions.remove(item)

            qSets = getSetDetails_type_elem(expressions)

        else:
            print("ERROR : INVALID INFO TYPE")
            return "ERROR : INVALID INFO TYPE"
    else:
        return "ERROR : FILL REQUIRED FIELDS"

    infoOb.update_data(qSets)

    output = ''
    for set in infoOb._regions:
        output += set.name + " : " + str(set.size) + ', ' + str(set.elements)
    Solver = solvers.Solver()
    final_answers = Solver.solve(infoOb, info_type)
    final_answers = '<br/>'.join(final_answers.split('\n'))
    return final_answers


VERBS = ["find", "Find", "Solve", "solve", "Calculate", "calculate", ':', "List", "list", "elements", "element",
         "Elements", "members", "Members"]


def extract_equations(text, regex):
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

    regex = re.compile(regex)
    results = regex.finditer(text)
    output = []
    # add validations
    for i, result in enumerate(results):
        expr = result.group()
        expr = expr.lstrip()
        expr = expr.rstrip()
        output.append(expr)
    return output


max_keywords = [' max ', ' maximum ', ' greatest ', ' largest ', ' විශාලතම']
min_keywords = [' min ', ' minimum ', ' smallest ', ' least  ', ' කුඩාම']


def getSetDetails_type_sn(equations, text):
    sets = []
    for equation in equations:
        region = dataCollector.region(None, None, None, None)
        name = input_formatter.extract_name_from_sn(equation)

        if "=" in equation:
            size = equation[equation.find("=") + 1:len(equation)]
            if (EQUAL_CAR_SET not in size):
                if not Validator.is_a_positive_int(size):
                    raise Exception("negative cardinality")
                region.size = size
            else:
                region.equal_card_set = size[size.find(EQUAL_CAR_SET + "_") + len(EQUAL_CAR_SET + "_"):len(size)]
        else:
            find_min_max = False
            if text != '':
                for keyword in max_keywords:
                    if keyword in text:
                        region.q_max_size = True
                        find_min_max = True
                for keyword in min_keywords:
                    if keyword in text:
                        region.q_min_size = True
                        find_min_max = True
            if not find_min_max:
                region.q_size = True
        # add validations
        trimmed_name = name.replace(" ", "")
        region.name = trimmed_name
        region.label = name
        sets.append(region)
    return sets


def getSubsetData_sn(subsets):
    equations = []
    for subset in subsets:
        candits = re.split(r'[⸦⊃]', subset)
        left = candits[0]
        right = candits[1]
        if ('⸦' in subset):
            equations.append('n(' + right + '\'∩' + left + ')=0')
        if ('⊃' in subset):
            equations.append('n(' + left + '\'∩' + right + ')=0')
    return equations


def getEqualCardinalitySetData_sn(equal_sets):
    equations = []
    for equation in equal_sets:
        sets = equation.split('=')
        for i, set in enumerate(sets):
            if i > 0:
                exp1 = sets[i - 1]
                exp2 = set
                equations.append(exp1 + "=" + EQUAL_CAR_SET + "_" + input_formatter.extract_name_from_sn(exp2))
    return equations


def getSetDetails_type_elem(equations):
    sets = []
    for equation in equations:
        region = dataCollector.region(None, None, None, None)
        if "=" in equation:
            name = equation[0: equation.find("=")]
        elements = input_formatter.extract_elements_from_eqn(equation)
        if elements is not None:
            region.elements = set(elements)
            region.size = len(region.elements)

        else:
            name = equation
            region.q_elements = True
        region.name = name
        region.name = region.name.replace(" ", "")
        region.label = name
        sets.append(region)
        # sets.append(dataCollector.region(trimmed_name,len(elements),name, elements))
    return sets


def filter_expressions_sn(expressions):
    regex = re.compile(expression_regex)
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

                if len(new_expr2) < 1:
                    break
                expr = extract_equations(new_expr2, expression_regex)
                if len(expr) > 0:
                    expr = filter_expressions_sn(expr)
                    expressions = expressions + expr
                    break
    return expressions


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


def remove_bullets(sentences, text, setDetails):
    not_bullets = re.compile(r'[∩∪ξ\'\-\(]+')
    for sent in sentences:
        sent = sent.lstrip()
        candits = re.split(r'\)', sent)
        if len(candits) > 0:
            is_a_set = False
            for set in setDetails:
                if set.name is not None:
                    if set.name in candits[0]:
                        is_a_set = True
            if not is_a_set:
                text = text.replace(candits[0] + ')', ',')

    return text


def is_paras_balanced(text, para):
    count = 0
    for index, letter in enumerate(text):
        if letter == '(':
            count += 1
        if letter == ')':
            count -= 1
        if count < 0:
            return -1 * index
    if count > 0:
        return index
    return count


def clean_operators_and_outer_apaces(text, replacement):
    text = text.replace('(', replacement)
    text = text.replace(')', replacement)
    text = text.replace('\'', replacement)
    text = text.replace('∩', replacement)
    text = text.replace('∪', replacement)
    text = text.replace('-', replacement)
    text = text.lstrip()
    return text.rstrip()