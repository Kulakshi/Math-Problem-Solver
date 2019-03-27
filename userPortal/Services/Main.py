import re
from . import dataCollections as dataCollector
from . import solvers
from . import Validator
from . import input_formatter

from .Derivations import Derivator
from .Mappers import Mapper
from .TextExtractions import RegexPatterns
from .TextExtractions.MLbasedExtractions import Filter_ML, parser
from .TextExtractions.RegexBasedExtractions import Filter_reg
from .Utils import util
from . import regex_based_solver

Patterns = RegexPatterns
def handle(text):
    info_type = text["info_type"]
    ques_type = text["ques_type"]

    text["info"] = input_formatter.change_alt_chars(text["info"])
    text["ques"] = input_formatter.change_alt_chars(text["ques"])

    infoOb = None
    '''
    Handle Information part of the problem
    '''
    if (text["info"] is not None or text['info'] is not ''):
        exps = []
        qexps = []
        exps = Filter_ML.filter(text["info"])
        qexps = Filter_ML.filter(text["ques"])

        for i,exp in enumerate(exps):
            isParseSuccess = parser.parseStr(exp)
            if not isParseSuccess:
                raise Exception("Error when parsing expression : ", exp)
        for i,exp in enumerate(qexps):
            isParseSuccess = parser.parseStr(exp)
            if not isParseSuccess:
                raise Exception("Error when parsing expression : ", exp)
        equations = exps
        print(equations)

        if(exps is not None):
            if info_type == util.type1:
                equations = Derivator.find_all_card_equations(equations, text["info"], info_type)
                setDetails = getSetDetails_type_sn(equations, '')
                infoOb = Mapper.info(setDetails)
            elif info_type == util.type2:
                global single_set_names
                single_set_names = []
                names = input_formatter.extract_main_set_names(equations, 'elem')
                for name in names:
                    name = clean_operators_and_outer_spaces(name, '#')
                    new_names = name.split('#')
                    for new_name in new_names:
                        if new_name not in single_set_names:
                                single_set_names.append(new_name)
                if 'ξ' not in text['info'] and len(equations)>1:
                    equations = input_formatter.find_universal_set_symbol(equations, qexps, info_type)
                setDetails = getSetDetails_type_elem(equations)
                infoOb = dataCollector.info(setDetails)

            else:
                raise Exception("ERROR : INVALID INFO TYPE : "+ info_type)
    else:
        raise Exception("ERROR : FILL REQUIRED FIELDS")


    '''
    Handle Question part of the problem
    '''
    if (text["info"] is not None or text['ques'] is not ''):
        expressions = qexps

        if (qexps is not None):
            if ques_type == util.type1:
                qSets = getSetDetails_type_sn(expressions, text["ques"])
            elif info_type == util.type2:
                for i,expr in enumerate(expressions):
                    filtered_eqn = input_formatter.tag_based_filter_set_name_elem(expr, str(Patterns.def_elem_exp_regex))
                    if filtered_eqn is not None:
                        expressions[i] = filtered_eqn

                items_to_remove = []
                for i, expr in enumerate(expressions):
                    print(expr)
                    if (input_formatter.filter_expressions_elem(expr, setDetails) is False):
                        items_to_remove.append(expr)

                for item in items_to_remove:
                    expressions.remove(item)

                qSets = getSetDetails_type_elem(expressions)
        else:
            raise Exception("ERROR : INVALID INFO TYPE")
    else:
        raise Exception("ERROR : FILL REQUIRED FIELDS")


    infoOb.update_data(qSets)


    output = ''
    for set in infoOb._regions:
        output += set.name + " : " + str(set.size) + ', ' + str(set.elements)

    print("output", output)
    Solver = solvers.Solver()
    final_answers = Solver.solve(infoOb, info_type)
    final_answers = '<br/>'.join(final_answers.split('\n'))

    return final_answers


VERBS = ["find", "Find", "Solve", "solve", "Calculate", "calculate", ':', "List", "list", "elements", "element","Elements", "members", "Members"]


def extract_equations(text, regex):
    output = []
    print(text),
    print(regex)
    regex = re.compile(regex)
    extracted_indexes = []
    for i,eqn in enumerate(text):
        results = regex.finditer(eqn)
        # add validations
        print("RES", eqn, results)
        for result in results:
            expr = result.group()
            print(expr)
            expr = expr.lstrip()
            expr = expr.rstrip()
            extracted_indexes.append(i)
            output.append(expr)
    for index in reversed(extracted_indexes):
        print(text)
        print(index)
        print(text[index])
        text = remove_at(index,text)
        # del text[index]
    return output

def remove_at(i, s):
    return s[:i] + s[i+1:]

max_keywords = [' max ', ' maximum ', ' greatest ', ' largest ', ' විශාලතම']
min_keywords = [' min ', ' minimum ', ' smallest ', ' least  ', ' කුඩාම']
def getSetDetails_type_sn(equations, text):
    sets = []
    EQUAL_CAR_SET = util.EQUAL_CAR_SET
    for equation in equations:
        region = dataCollector.region(None,None,None,None)
        name = input_formatter.extract_name_from_sn(equation)

        if "=" in equation:
            size = equation[equation.find("=") + 1:len(equation)]
            print(EQUAL_CAR_SET in size)
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
        if name and name!= '':
            region.name = trimmed_name
            region.label = name
            sets.append(region)
    return sets


def getSetDetails_type_elem(equations):
    sets = []
    for equation in equations:
        region = dataCollector.region(None,None,None,None)
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
    return sets



def clean_operators_and_outer_spaces(text, replacement):
    text = text.replace('(', replacement)
    text = text.replace(')', replacement)
    text = text.replace('\'', replacement)
    text = text.replace('∩', replacement)
    text = text.replace('∪', replacement)
    text = text.replace('-', replacement)
    text = text.lstrip()
    return text.rstrip()




