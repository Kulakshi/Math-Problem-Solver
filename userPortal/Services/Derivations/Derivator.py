import re
from ..Utils import util
from ..TextExtractions import RegexPatterns
Patterns = RegexPatterns

def find_all_card_equations(expressions, text, info_type):
    subsets = find_subsets(expressions)
    equal_cardinalities = find_equal_sets(expressions)
    expressions = expressions + equalCardSetsToCard(equal_cardinalities, expressions)
    expressions = expressions + subsetsToCard(subsets)
    if 'ξ' not in text and len(expressions) > 1:
        expressions = find_universal_set_symbol(expressions, info_type)
    return expressions

def find_all_elem_equations(expressions, text, info_type):
    subsets = find_subsets(expressions)
    equal_cardinalities = find_equal_sets(expressions)
    expressions = expressions + equalCardSetsToCard(equal_cardinalities, expressions)
    expressions = expressions + subsetsToCard(subsets)
    if 'ξ' not in text and len(expressions) > 1:
        expressions = find_universal_set_symbol(expressions, info_type)
    return expressions


def find_universal_set_symbol(equations, type):
    single_sets_eqns = equations
    single_set_names = extract_main_set_names(single_sets_eqns, type)
    names = []

    for eqn in equations:
        if (type == util.type1):
            names.append(util.extract_name_from_sn(eqn))
        if (type == util.type2):
            names.append(util.extract_name_from_elem(eqn))
    all = '#'.join(names)
    all = all.replace(' ', '#')
    all = all.replace("∩", "#")
    all = all.replace("-", "#")
    all = all.replace("∪", "#")
    all = all.replace("'", "#")
    all = all + '#'
    print(all)

    candidiate_set_indexes = []
    candidiate_set_sizes = []
    candidiate_set_names = []
    candidiate_set_elements = []

    print("FINDING UNIVERSAL SET")
    # Find universal set based on given set names
    for set in single_set_names:
        print("SET : ",set)
        num_occurences = all.count(set.replace(' ', '#') + "#")
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
                        candidiate_set_names.append(set)
                        candidiate_set_elements.append(elements)

    should_check_size = True
    # Find universal set based on set sizes
    if should_check_size:
        if len(candidiate_set_indexes) > 1:
            max_size = max(candidiate_set_sizes)
            uni_set_in_elems = True
            for i, size in enumerate(candidiate_set_sizes):
                if size == max_size:
                    if (type == util.type2):
                        print(candidiate_set_names[i])
                        for j, elems in enumerate(candidiate_set_elements):
                            print(elems, candidiate_set_elements[i])
                            if not contains(candidiate_set_elements[i],elems):
                                uni_set_in_elems = False
                    if uni_set_in_elems:
                        equations[candidiate_set_indexes[i]] = equations[candidiate_set_indexes[i]].replace(
                            candidiate_set_names[i], 'ξ')
                    else:
                        all_elements =  []
                        for list in candidiate_set_elements:
                            for elem in list:
                                if elem not in all_elements:
                                    all_elements.append(elem)
                        equations.append("ξ = {"+','.join(all_elements)+"}")
                    return equations
        else:
            if len(candidiate_set_indexes) > 0:
                equations[candidiate_set_indexes[0]] = equations[candidiate_set_indexes[0]].replace(
                    candidiate_set_names[0], 'ξ')

    return equations


def find_subsets(text):
    output = []
    regex = re.compile(str(Patterns.subset_regex))
    extracted_indexes = []
    for i,eqn in enumerate(text):
        results = regex.findall(eqn)
        if len(results) > 0 : extracted_indexes.append(i)
        for result in results:
            expr = result
            expr = expr.lstrip()
            expr = expr.rstrip()
            output.append(expr)
    for index in reversed(extracted_indexes):
        del text[index]
    return output

def find_equal_sets(text):
    output = []
    regex = re.compile(str(Patterns.equal_cardinality_regex))
    extracted_indexes = []
    for i,eqn in enumerate(text):
        results = regex.findall(eqn)
        if len(results) > 0 : extracted_indexes.append(i)
        for result in results:
            expr = result[0]
            expr = expr.lstrip()
            expr = expr.rstrip()
            output.append(expr)
    for index in reversed(extracted_indexes):
        del text[index]
    return output

#getEqualCardinalitySetData_sn
def equalCardSetsToCard(equal_sets, cardEquations):
    equations = []
    cardLefts = []
    cardRights = []
    for cardEqn in cardEquations:
        if '=' in cardEqn:
            cardSets = cardEqn.split('=')
            cardLefts.append(cardSets[0].replace(' ', ''))
            cardRights.append(cardSets[1].replace(' ', ''))


    for equation in equal_sets:
        sets = equation.split('=')
        for i,set in enumerate(sets):
            set = set.replace(' ', '')
            print("SET ", set)

            if i > 0:
                exp1 = sets[i-1]
                exp2 = set
                if exp1 in cardLefts:
                    cardRight = cardRights[cardLefts.index(exp1)]
                    if cardRight.isdigit():
                        equations.append(exp2 + '='+ cardRight)
                elif exp1 in cardRights:
                    cardLeft = cardLefts[cardRights.index(exp1)]
                    if cardLeft.isdigit():
                        equations.append(exp2 + '='+ cardLeft)
                elif exp2 in cardLefts:
                    cardRight = cardRights[cardLefts.index(exp2)]
                    if cardRight.isdigit():
                        equations.append(exp1 + '='+ cardRight)
                elif exp2 in cardRights:
                    cardLeft = cardLefts[cardRights.index(exp2)]
                    if cardLeft.isdigit():
                        equations.append(exp1 + '='+ cardLeft)
                else:
                    equations.append(exp1 + "=" + util.EQUAL_CAR_SET + "_" + util.extract_name_from_sn(exp2))



    return equations

#getSubsetData_sn
def subsetsToCard(subsets):
    derive_new_subsets(subsets, '⸦')
    derive_new_subsets(subsets, '⊃')
    derive_new_subsets(subsets, '⊇')
    derive_new_subsets(subsets, '⊆')
    print("with derived subsets ", subsets)
    equations = []
    for subset in subsets:
        candits = re.split(r'[⸦⊃⊆⊇]', subset)
        left = candits[0]
        right = candits[1]
        if( '⸦' in subset ):
            equations.append('n(' + right + '\'∩' + left + ')=0')
        if( '⊆' in subset ):
            equations.append('n(' + right + '\'∩' + left + ')=0')
            equations.append('n(' + right + ') = n(' + left + ')')
        if( '⊃' in subset ):
            equations.append('n(' + left + '\'∩' + right + ')=0')
        if( '⊇' in subset ):
            equations.append('n(' + left + '\'∩' + right + ')=0')
            equations.append('n(' + left + ') = n(' + right + ')=0')
    return equations



#private
def derive_new_subsets(subsets, subsetOp):
    all_subsets = []
    for subset in subsets:
        candits = re.split(r'['+subsetOp+']', subset)
        if(len(candits) < 2 ): return
        right = candits[1].lstrip().rstrip()
        left = candits[0].lstrip().rstrip()
        all_subsets.append((left, right))
    for subset in all_subsets:
        left = subset[0]
        right = subset[1]
        candits = [t[1] for t in all_subsets if t[0] is right]
        for candit in candits:
            print(left,candit)
            print((left,candit) not in all_subsets)
            if (left,candit) not in all_subsets:
                all_subsets.append((left,candit))
                subsets.append(left + subsetOp + candit)
    print(all_subsets)
    print(subsets)

def extract_main_set_names(main_set_eqns, type):
    names = []
    for expression in main_set_eqns:
        if type == util.type1:
            name = util.extract_name_from_sn(expression)
        if type == util.type2:
            name = util.extract_name_from_elem(expression)
        names.append(name.replace("\'", ''))
    return names



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


def contains(super_list, sub_list):
    if super_list is not None and sub_list is not None:
        for item in sub_list:
            if item not in super_list:
                return False
    else:
        return False
    return True

