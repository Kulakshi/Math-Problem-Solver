import re
from io import StringIO
import tokenize
import math
import sympy
import itertools


def convert_region_name_to_logical_exp(region_name):
    region_name = region_name.replace('∪', ' | ')
    region_name = region_name.replace('∩', ' & ')
    region_name = region_name.replace('ξ', 'ξ')
    region_name = region_name.replace('-', '& ~')
    region_name = region_name.replace('(', '( ')

    print("\n convert_region_name_to_logical_exp")
    print(region_name)

    regex = re.compile('\'')
    results = regex.finditer(region_name)
    indexes = []
    for result in results:
        tup = result.span()
        indexes.append(tup[0])

    for index in indexes:
        if index > 0:
            print(region_name[index-1])
            if (region_name[index - 1] is ')'):
                # print('index - 1 is )')
                count = 0
                span_index = -1
                for i in range(index - 1, -1, -1):
                    if (region_name[i] is ")"):
                        count = count + 1
                    if (region_name[i] is "("):
                        count = count - 1
                    if (count == 0):
                        span_index = i
                        break
                complemented_part = region_name[span_index: index + 1]
                region_name = region_name.replace(complemented_part,
                                                  '~' + complemented_part[0:len(complemented_part) - 1],1)
            else:
                span_index = -1
                for i in range(index - 1, 0, -1):
                    if (region_name[i] is " "):
                        span_index = i
                        break
                complemented_part = region_name[span_index + 1: index + 1]
                region_name = region_name.replace(complemented_part,
                                                  '~' + complemented_part[0:len(complemented_part) - 1],1)
    return region_name


def evaluate_logic_exp_tree(exp, num_sets, main_set_index_map, or_func, and_func, not_func):
    exp = exp.replace('\n', '')
    exp = exp.replace('Symbol(\'', '')
    exp = exp.replace(',', '')
    exp = exp.replace('\')', '')

    exp = [token[1] for token in tokenize.generate_tokens(StringIO(exp).readline) if str(token[1])]
    print(exp)
    stack = Stack()
    for i, literal in enumerate(exp):
        stack.push(literal)

    helperStack = Stack()
    while stack.size() > 0:
        literal = stack.pop()
        # print(" LITERAL : ", literal)
        if literal == 'OR' or literal == 'AND' or literal == 'NOT' and literal is not None:
            operands = []
            popbackliteral = helperStack.pop()
            # print("######1")
            # print(popbackliteral)
            while popbackliteral is not ')':
                if (not isinstance(popbackliteral, int)):
                    # print("######")
                    # print(popbackliteral)
                    operands.append(main_set_index_map[popbackliteral])
                else:
                    operands.append(popbackliteral)
                popbackliteral = helperStack.pop()
            if literal == 'OR':
                print(operands)
                stack.push(or_func(operands))
            if literal == 'AND':
                stack.push(and_func(operands))
            if literal == 'NOT' and len(operands) > 0:
                print(" trigerring NOT with.. : ", operands)
                stack.push(not_func(num_sets, operands[0]))
        else:
            if literal is not '(' and literal is not ' ' and literal is not None:
                # print(literal)
                if (literal in main_set_index_map):
                    helperStack.push(main_set_index_map[literal])
                else:
                    helperStack.push(literal)
                # print("=====================helperStack========================")
                # print(helperStack.items)
                # print("========================stack=====================")
                # print(stack.items)

    return helperStack.pop()


def generate_equations(index, v, len_data):

    print("EQUATIONS")
    # qRegion_eqn_mapping.append(None)
    if (v is not None):
        if (v.size is not None or v.q_size is True):
            eqn = get_expr_for_region(index, int(math.sqrt(len_data)))
            if (v.size is not None):  # size is not '?'):

                # if (v.q_size is True):
                    # self.qRegion_eqn_mapping[i] = eqn
                    # self.result[eqn] = int(v.size)
                eqn = eqn - int(v.size)
                print(eqn)
                # equations += (eqn,)
            if (v.size is None and v.q_size is True):
                print(eqn)
                # qRegion_eqn_mapping.append(eqn)
    # print(qRegion_eqn_mapping)
    return eqn

def get_symbols_for_region(key, num_symbols):
    a = ord('a')
    symbols = []
    key = bin(key)[2:].zfill(num_symbols)
    # print(key)
    for i, digit in enumerate(key):
        if (digit == '1'):
            symbols.append(sympy.Symbol(chr(a + i)))
    return symbols

def get_expr_for_region(key, num_symbols):
    a = ord('a')
    expr = 0
    key = bin(key)[2:].zfill(num_symbols)
    # print(key)
    for i, digit in enumerate(key):
        if (digit == '1'):
            expr += sympy.Symbol(chr(a + i))
    return expr

def get_super_sets(index, num_symbols):
    a = ord('a')
    symbols = []
    max_symbols = []
    key = bin(index)[2:].zfill(num_symbols)
    max_key = bin(pow(2,num_symbols)-1)[2:].zfill(num_symbols)

    for i, digit in enumerate(max_key):
        if (digit == '1'):
            max_symbols.append(chr(a + i))
        if(key[i] == '1'):
            symbols.append(chr(a + i))

    sym_set = set(symbols)
    max_sym_set = set(max_symbols)
    diff_set = max_sym_set - sym_set

    super_sets = []
    for i in range(len(diff_set)+1):
        diff_comb = itertools.combinations(sorted(diff_set), i)

        for combi in diff_comb:
            if len(combi) > 0 :
                new_set = set(symbols)
                for sym in combi:
                    new_set.add(sym)
                binary = ''
                for sym in max_symbols:
                    if sym in sorted(new_set):
                        binary = binary + '1'
                    else:
                        binary = binary + '0'
                super_sets.append(int(binary, 2))
    return super_sets

def get_sub_sets(index, num_symbols):
    a = ord('a')
    symbols = []
    max_symbols = []
    key = bin(index)[2:].zfill(num_symbols)
    max_key = bin(pow(2, num_symbols) - 1)[2:].zfill(num_symbols)

    for i, digit in enumerate(max_key):
        if (digit == '1'):
            max_symbols.append(chr(a + i))
        if(key[i] == '1'):
            symbols.append(chr(a + i))

    sub_sets = []
    for i in range(len(symbols)+1):
        diff_comb = itertools.combinations(sorted(symbols), i)
        for combi in diff_comb:
            if len(combi) > 0:
                binary = ''
                for sym in max_symbols:
                    if sym in sorted(combi):
                        binary = binary + '1'
                    else:
                        binary = binary + '0'
                sub_sets.append(int(binary, 2))
    return sub_sets


class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        # print("STACK PUSH : ", item)
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)
