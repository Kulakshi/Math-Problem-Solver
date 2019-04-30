import sympy
import math
from sympy import diff
import re
from . import utils
from .Utils import util
from . import dataCollections
import boolean

class Solver:

    def __init__(self):
        self.data = {}
        self.all_symbols = set()
        # self.qRegion_eqn_mapping = []
        self.result = {}
        self.answers = {}

    def clear(self):
        self.data.clear()
        self.all_symbols.clear()
        # self.qRegion_eqn_mapping.clear()
        self.result.clear()

    def solve(self, info, infoType):
        self.data = info.get_data();

        #find elements
        elements = []

        if(infoType == util.type2):
            elements = self.fill_elements(info)
        equations = self.generate_equations(self.data, info)
        symbols = ()
        final_answers = [elements]

        output = ''
        if len(info.q_min_regions) > 0:
            for index in info.q_min_regions:
                region = self.data[index]
                min = self.find_min_cardinality(index, self.data, equations)
                output += 'Minimum cardinality of '+region.name+" = "+str(min)+' \n'

        if len(info.q_max_regions) > 0:
            for index in info.q_max_regions:
                region = self.data[index]
                max = self.find_max_cardinality(index, self.data, equations)
                output += 'Maximum cardinality of '+region.name+" = "+str(max)+' \n'


        for symbol in self.all_symbols:
            symbols += (symbol,)
            self.result.update(sympy.solve(equations, symbols))


        if len(info.q_regions) > 0:
            for i in info.q_regions:
                region = self.data[i]
                expr = region.expr
                if(expr is not None):
                    if(expr in self.result):
                        ans =  self.result[expr]
                    else:
                        # ans = eqn.evalf(subs=self.result)
                        ans = expr.subs(self.result)
                    try:
                        if(int(ans) - float(ans) != 0):
                            raise Exception("Inconsistant data : Cardinality cannot be non integer")
                        ans = int(ans)
                        if ans< 0:
                            raise Exception("Inconsistant data : Cardinality cannot be negative")
                    except TypeError:
                        raise Exception('Not enough data to solve the problem')

                    output+= " n("+region.name+") = "+str(ans)
                    # if(self.data[i] is not None and ans is not None):
                    #     self.answers[self.data[i].label] = str(ans)
                    #     final_answers.append("n("+str(self.data[i].label) + ") = "+ str(ans))



        for name in self.answers:
            ordered_set = list(self.answers[name])
            ordered_set.sort()
            output += name + " = {" + str(', '.join(ordered_set)) + "}"
        self.clear()
        return output

    def generate_equations(self,data,info):
        equations = ()
        for i in info.get_filled_regions():
            v = self.data[i]
            # self.qRegion_eqn_mapping.append(None)
            if (v is not None):
                equal_expr = None
                if(v.equal_card_set is not None):
                    region_index = info.get_region_index(v.equal_card_set)
                    equal_expr = data[region_index].expr
                    equations += (sympy.simplify(equal_expr-v.expr),)
                if (v.size is not None or v.q_size is True):
                    eqn = v.expr
                    self.all_symbols.update(eqn.free_symbols)
                    if (v.size is not None):#size is not '?'):
                        if(v.q_size is True):
                            # self.qRegion_eqn_mapping[i] = eqn
                            self.result[eqn] = int(v.size)
                            if(equal_expr is not None):
                                self.result[equal_expr] = int(v.size)
                        if int(v.size) is 0:
                            symbols = eqn.free_symbols
                            for symbol in symbols:
                                equations += (symbol - 0,)
                        else:
                            eqn = eqn - int(v.size)
                            equations += (eqn,)
        #             if(v.size is None and v.q_size is True):
        #                 self.qRegion_eqn_mapping.append(eqn)
        return equations

    def find_min_cardinality(self, region_index, data, equations):
        sub_sets = utils.get_sub_sets(region_index, int(math.sqrt(len(data))))
        if len(sub_sets) > 1:
            max = 0
            for set in sub_sets:
                if data[set] is not None:
                    size = data[set].size
                    if size is not None:
                        if max < int(size):
                            max = int(size)
            return max
        else:
            symbols = ()
            eqn = data[region_index].expr - 0
            equations += (eqn,)
            result_copy = self.result.copy()
            for symbol in self.all_symbols:
                symbols += (symbol,)
                result_copy.update(sympy.solve(equations, symbols))
            for key,res in result_copy.items():
                if(res < 0):
                    return abs(res)
            return 0

    def find_max_cardinality(self,region_index,data, equations):
        super_sets = utils.get_super_sets(region_index, int(math.sqrt(len(data))))
        min = math.inf
        if len(super_sets) is 0:
            return None

        for set in super_sets:
            if data[set] is not None:
                size = data[set].size
                if size is not None:
                    if min > int(size):
                        min = int(size)

        symbols = ()
        eqn = data[region_index].expr - min
        equations += (eqn,)
        result_copy = self.result.copy()
        for symbol in self.all_symbols:
            symbols += (symbol,)
            result_copy.update(sympy.solve(equations, symbols))
        max_negative = 0
        for key, res in result_copy.items():
            if (res < max_negative):
                max_negative = res
                return min + max_negative
        return min

    def fill_elements(self,info):
        data = info.get_data()
        region_elements = []
        ans = ''
        for i, v in enumerate(data):
            if (v is not None):
                if(v.q_elements is True or v.q_size is True):
                    self.fill_region_elements(v.name, info)
                    if data[i].elements:
                        self.data[i].size = len(data[i].elements)
                    elements = ''
                    if v.elements:
                        elements = ', '.join(str(e) for e in v.elements)
                    if(v.q_elements):
                        if v.elements:
                            self.answers[v.label] = v.elements
                        else:
                            self.answers[v.label] = ''
                    ans += v.name + ' :'+ elements +' , '
        return ans



    def fill_region_elements(self,region_name,info):
        region_name = utils.convert_region_name_to_logical_exp(region_name)
        if region_name == 'ξ':
            if (self.data is not None and self.data[len(self.data) - 1] is not None and self.data[len(self.data) - 1].elements is not None):
                return self.data[len(self.data) - 1].elements
            else:
                print("ERROR")
        else:
            # if(region_name in info.main_set_names):
            #     if(self.data[info.get_main_name_index_map[region_name]].elements is not None):
            #         return self.data[info.get_main_name_index_map[region_name]].elements
            algebra = boolean.BooleanAlgebra()
            exp = str(algebra.parse(region_name).pretty())
            return utils.evaluate_logic_exp_tree(exp, info.get_num_sets(), info.get_main_name_index_map(), self.get_union,
                                                 self.get_intersection, self.get_complement)



    def get_complement(self, num_sets, index):
        result = None
        result_index = None
        if(self.data is not None and self.data[len(self.data)-1] is not None and self.data[len(self.data)-1].elements is not None):
            if(self.data[index] is not None and self.data[index].elements is not None):
                result_index = ''.join('1' if x == '0' else '0' for x in bin(index)[2:].zfill(pow(2, num_sets)))
                result = self.data[len(self.data)-1].elements - self.data[index].elements
                result_index = int(result_index, 2)
                if (self.data[result_index] is None):
                    self.data[result_index] = dataCollections.region(None,None,None,None)
                self.data[result_index].elements = set(result)
                self.data[result_index].size = len(result)
                return result_index
            else:
                print("ERROR")
        else:
            print("ERROR")

    def get_union(self,operands):
        result = None
        result_index = None
        for operand in operands:
            if(self.data[operand] is not None and self.data[operand].elements is not None):
                if (result is None):
                    result_index = operand
                    result = self.data[operand].elements
                else:
                    result_index = result_index | operand
                    result = result | self.data[operand].elements
                    if (self.data[result_index] is None):
                        self.data[result_index] = dataCollections.region(None, None, None, None)
                    self.data[result_index].elements = set(result)
            else:
                print("ERROR")
                return None
        return result_index


    def get_intersection(self,operands):
        result = None
        result_index = None
        for operand in operands:
            if(self.data[operand] is not None and self.data[operand].elements is not None):
                if (result is None):
                    result_index = operand
                    result = self.data[operand].elements
                else:
                    result_index = result_index & operand
                    result = result & self.data[operand].elements
                    if (self.data[result_index] is None):
                        self.data[result_index] = dataCollections.region(None, None, None, None)
                    self.data[result_index].elements = set(result)
            else:
                print("ERROR")
                return None
        return result_index
