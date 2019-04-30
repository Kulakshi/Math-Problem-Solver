from scipy import sparse
import numpy
import math
# import latex2sympy as lax2sy
import re
import functools
# from latex2sympy import process_latex
import boolean
from io import StringIO
import tokenize
from . import utils


class region:
    def __init__(self, name, size, label, elements):
        self.name = name
        self.size = size
        self.label = label
        self.elements = elements
        self.q_size = False
        self.q_elements = False
        self.q_min_size = False
        self.q_max_size = False
        self.expr = None
        self.equal_card_set = None
        self.eqn = None


class info:
    def __init__(self, regions):
        self._regions = regions
        self.main_set_names = []
        self.num_sets = 0
        self.num_regions = 0
        self.main_name_index_map = {}
        self.q_regions = set()
        self.q_min_regions = set()
        self.q_max_regions = set()
        self.filled_regions = set()
        self.data = Finite_Array(0)  # sparse.dok_matrix((1, self.num_regions), dtype=object)
        self.add_init_data(regions)

    def add_init_data(self, regions):
        region_names = self.get_region_names(regions)

        self.main_set_names = self.find_main_set_names(region_names)

        self.num_sets = len(self.main_set_names)
        self.num_regions = pow(2, pow(2, self.num_sets))
        if ('ξ' in region_names):
            self.main_name_index_map = {'ξ': self.num_regions - 1}
        else:
            self.main_name_index_map = {}
        self.data = Finite_Array(self.num_regions)  # sparse.dok_matrix((1, self.num_regions), dtype=object)
        self.main_indices = self.calculate_main_set_indexes(self.num_sets)
        self.fill_data(self.num_sets, regions)

        # self.print_data_array();

    def update_data(self, regions):
        self.fill_data(self.num_sets, regions)
        # self.print_data_array();

    def get_num_sets(self):
        return self.num_sets

    def print_data_array(self):
        for i, data in enumerate(self.data.array):
            if (data is not None):
                print(i)
                print(data.name)
                print(data.size)
                print(data.elements)
                print(data.q_size)
                print(data.q_elements)
                print(data.expr)
                print(data.equal_card_set)
                print("===")

    def get_region_names(self, regions):
        region_names = []
        for region in regions:
            region_names.append(region.name)
        return region_names

    def get_data(self):
        return self.data.array

    def get_filled_regions(self):
        return self.filled_regions

    def get_main_name_index_map(self):
        return self.main_name_index_map

    def find_main_set_names(self, region_names):
        _names = set()
        for name in region_names:
            candi_names = re.sub(r'(\(|\)|∩|∪|ξ|\-|\'|\’|\|)', '#', name)
            candi_names = candi_names.split('#')

            for candi_name in candi_names:
                if candi_name is not '':
                    _names.add(candi_name)
        return _names;

    def calculate_main_set_indexes(self, num_sets):
        num_bits = pow(2, num_sets)
        bit_mat = []
        for i in range(num_bits):
            bit_mat.append([x for x in list(format(i, '0' + str(num_sets) + 'b'))])
        bit_mat = numpy.array(bit_mat)
        bit_mat = bit_mat.transpose()

        main_indexes = []
        for row in bit_mat:
            main_indexes.append(int(''.join(row), 2))
        return main_indexes

    def fill_data(self, num_sets, regions):
        self.fill_main_sets(num_sets, regions)
        for region in regions:
            name = region.name
            if (name not in self.main_set_names):
                index = self.get_region_index(name)
                self.check_and_store(index, region)

    def check_and_store(self, index, region):
        remaining_region = self.data.get(index)
        if remaining_region is not None:
            if region.size is None:
                region.size = remaining_region.size
            if region.elements is None:
                region.elements = remaining_region.elements
            if region.equal_card_set is None:
                region.equal_card_set = remaining_region.equal_card_set
        if region.size is not None:
            self.validate_size(index, region.size)

        region.expr = utils.get_expr_for_region(index, pow(2, self.num_sets))
        if(region.size is not None):
            self.eqn = region.expr - int(region.size)

        if region.q_max_size: self.q_max_regions.add(index)
        if region.q_min_size: self.q_min_regions.add(index)
        if region.q_size is True: self.q_regions.add(index)
        self.filled_regions.add(index)
        self.data.put(index, region)

    def validate_size(self, region_index, size):
        super_sets = utils.get_super_sets(region_index, pow(2, self.num_sets))
        if size is not None:
            for index in super_sets:
                region = self.data.get(index)
                if region is not None:
                    if region.size is not None:
                        if int(region.size) < int(size):
                            raise Exception("Inconsistent Data : Cardinality of super set is less than sub set")

            sub_sets = utils.get_sub_sets(region_index, pow(2, self.num_sets))
            for index in sub_sets:
                region = self.data.get(index)
                if region is not None:
                    if region.size is not None:
                        if int(region.size) > int(size):
                            raise Exception("Inconsistent Data : Cardinality of sub set is larger than super set")

    def fill_main_sets(self, num_sets, regions):
        # main_indexes = self.calculate_main_set_indexes(num_sets)
        main_sets = self.get_main_set_regions(regions)
        # add main set regions to data

        if (len(self.main_indices) == num_sets & len(main_sets) == num_sets):
            for i, main_index in enumerate(self.main_indices):
                self.check_and_store(main_index, main_sets[i])
                self.main_name_index_map[main_sets[i].name] = main_index
        else:
            print("ERROR : fill_main_sets")

    def get_main_set_regions(self, regions):
        main_sets = []
        # create regions
        for name in self.main_set_names:
            size = None
            new_region = region(name, None, None, None)
            for reg in regions:
                if name == reg.name:
                    new_region = reg
            main_sets.append(new_region)
        # print(main_sets)
        return main_sets;

    def get_region_index(self, region_name):
        region_name = utils.convert_region_name_to_logical_exp(region_name)
        if region_name == 'ξ':
            return self.num_regions - 1
        elif region_name in self.main_set_names:
            return  self.main_name_index_map[region_name]
        else:
            algebra = boolean.BooleanAlgebra()

            exp = str(algebra.parse(region_name).pretty())
            return utils.evaluate_logic_exp_tree(exp, self.num_sets, self.main_name_index_map, self.get_union_index,
                                                 self.get_intersection_index, self.get_complement_index)

    def get_complement_index(self, num_sets, index):
        # comp_bin = ''.join('1' if x == '0' else '0' for x in format(index, '0' + str(num_sets) + 'b'))
        comp_bin = ''.join('1' if x == '0' else '0' for x in bin(index)[2:].zfill(pow(2, num_sets)))
        return int(comp_bin, 2)

    def get_union_index(self, operands):
        result = None
        for operand in operands:
            if (result is None):
                result = operand
            else:
                result = result | operand
        return result

    def get_intersection_index(self, operands):
        result = None
        for operand in operands:
            if (result is None):
                result = operand
            else:
                result = result & operand
        return result


class Finite_Array:
    def __init__(self, max_size):
        self.size = 0
        self.max_size = max_size
        self.array = []
        for i in range(max_size):
            self.array.append(None)

    def put(self, index, object):
        if self.isIndexValid(index):
            self.array[index] = object
            self.size = self.size + 1

    def get(self, index):
        if self.isIndexValid(index):
            if self.array[index] is not None:
                return self.array[index]
            else:
                a = 10
                # print("ERROR : ACCESSING NULL VALUE")
        else:
            print("ERROR : INVALID INDEX")

    def isIndexValid(self, index):
        return index <= self.max_size - 1

    def isEmpty(self):
        return self.size < 1

    # a = numpy.empty(16, dtype=object)

    # mtx = sparse.dok_matrix((5,5), dtype=region)
    # S = sparse.dok_matrix((1, 4), dtype=object)
    # for i in range(1):
    #     for j in range(2):
    #         S[i, j] = region("A", 12, "A")  # Update element
    # print(S[0, 3])
    # for k, v in self.data.items():
    #     if (v is not None):
    #         print(k + "  " + v.name + " " + str(v.size))

    # print(algebra.parse('(apple or banana and (orange or pineapple and (lemon or cherry)))').get_symbols())

    # def parse_bool(self, tokens,index):
    #     if(index > len(tokens)):
    #         if(tokens[index] is )
