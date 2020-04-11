import pandas as pd 
import numpy as np
import copy
from visualization import Visualization
import gc

class Cube:
    def __init__(self, table_df):
        self.original_data = table_df
        self.cube = table_df.copy()
        self.element = pd.DataFrame()
    
    def show(self, ):
        temp_cube = self.cube.copy()
        element_tuple = self.element.values.tolist()
        # if element is empty, set to be 1
        if len(element_tuple) == 0:
            temp_cube["element"] = np.ones((len(temp_cube),1), dtype=int)
        else:
            # if one of the row is empty, set to be 1
            for i in range(len(element_tuple)):
                if len(element_tuple[i]) == 0:
                    element_tuple[i] = 1
            temp_cube["element"] = element_tuple
        print(temp_cube)

    def get_dimension_names(self):
        return list(self.cube.columns)

    def get_num_dimensions(self):
        return len(self.cube.columns)

    def visualize(self, type=None):
        if not type:
            if self.get_num_dimensions() <= 3:
                Visualization(self.cube, self.element).show_cube()
            else:
                Visualization(self.cube, self.element).show_table()
        elif type == "table":
            Visualization(self.cube, self.element).show_table()
        elif type == "map":
            Visualization(self.cube, self.element).show_map()
        
    def pull(self, dimentions_name):
        if dimentions_name not in self.element.columns:
            print("Error: {} is not a column name in the element tuple of the cube".format(dimentions_name))
            return self
        new_cube = copy.deepcopy(self)
        new_cube.cube[dimentions_name] = self.element[dimentions_name]
        new_cube.element = self.element.drop(columns=[dimentions_name])
        return new_cube

    def push(self, dimentions_name):
        if dimentions_name not in self.cube.columns:
            print("Error: {} is not a dimention of this cube".format(dimentions_name))
            return self
        new_cube = copy.deepcopy(self)
        new_cube.element[dimentions_name] = self.cube[dimentions_name]
        return new_cube

    def destroy(self, dimentions_name):
        if dimentions_name not in self.cube.columns:
            print("Error: {} is not a dimention of this cube".format(dimentions_name))
            return self
        dimentions_values = self.cube[dimentions_name]
        if len(dimentions_values) > 0:
            only_value = dimentions_values[dimentions_values.index[0]]
            for v in dimentions_values:
                if not v == only_value:
                    print("Error: Cannot destroy dimention, because more than one value in this dimention")
                    return self
        new_cube = copy.deepcopy(self)
        new_cube.cube = new_cube.cube.drop(columns=[dimentions_name])
        return new_cube

    # predicate_func receive the value of a row of this dimention, return true or false
    def restriction(self, dimentions_name, predicate_func):
        if dimentions_name not in self.cube.columns:
            print("Error: {} is not a dimention of this cube".format(dimentions_name))
            return self
        new_cube = copy.deepcopy(self)
        idx = new_cube.cube[dimentions_name].apply(predicate_func)
        new_cube.cube = new_cube.cube.loc[idx]
        new_cube.element = new_cube.element.loc[idx]
        return new_cube
    
    # this is not an operator
    def dimention_transform(self, cube, dimentions_name, func):
        if dimentions_name not in cube.cube.columns:
            print("Error: {} is not a dimention of this cube".format(dimentions_name))
            return cube
        data_list = list(cube.cube[dimentions_name])
        try:
            for i in range(len(data_list)):
                data_list[i] = func(data_list[i])
        except:
            print("Cannot apply func to the data in column {}".format(dimentions_name))
            return None
        cube.cube[dimentions_name] = data_list
        return cube
    
    # Haven't tested!!!
    # cube2 is the other cube to be joined
    # dimentions_names = [...] is a list of dimentions' names that cube and cube2 shared
    # f = [f...]; f2 = [f...]; are the funcitons that will apply for each dimention of cube and cube 2
    # felem(elem, elem2)->merged_elem is the function that will apply when the element of cube and the element of cube2 are going to be merged
    # defalue values:
    #   felem: c1.elem and c2.elem, input is (row in c1.elem, row in c2.elem)
    #   felem_names: the column names after merge the element
    #   dimentions_names: the comment dimention of each data cube
    #   f & f2: y = x
    def join(self, cube2, felem=None, felem_names=[], dimentions_names=[], f=[], f2=[]):
        # validation phase
        #   make sure f and f2 have the same length as the shared dimentions_names
        if len(f) != len(dimentions_names) or len(f2) != len(dimentions_names):
            print("Error: f or f2 funcitons list doesn't have the same length as share dimentions_names")
            return self
        #   make sure dimentions_names are inclued in both cube and cube2
        if len(dimentions_names) == 0:
            dimentions_names = list(set(self.cube.columns) & set(cube2.cube.columns))
        for dim_name in dimentions_names:
            if dim_name not in self.cube.columns:
                print("Error: {} is not a dimention of this cube".format(dim_name))
                return self 
            elif dim_name not in cube2.cube.columns:
                print("Error: {} is not a dimention of this cube2".format(dim_name))
                return self 
        # copy data
        c1 = copy.deepcopy(self)
        c2 = copy.deepcopy(cube2)
        # Dimmentions transform phase
        #   apply f to cube and f2 to cube2
        for i, dim_name in enumerate(dimentions_names):
            if len(f) != 0:
                c1 = self.dimention_transform(c1, dim_name, f[i])
            if len(f2) != 0:
                c2 = self.dimention_transform(c2, dim_name, f2[i])
            if c1 == None or c2 == None:
                return self
        # Merge phase
        c1_elem_names = c1.element.columns
        c1_dim_names = c1.cube.columns
        c2_elem_names = c2.element.columns
        c2_dim_names = c2.cube.columns
        merged_c1_elem = pd.DataFrame()
        merged_c2_elem = pd.DataFrame()
        for name in c1_elem_names:
            c1 = c1.pull(name)
        for name in c2_elem_names:
            c2 = c2.pull(name)
        c1.cube = pd.merge(c1.cube, c2.cube,  how='inner', left_on=dimentions_names, right_on = dimentions_names)
        for name in c1_elem_names:
            if name not in c2_elem_names:
                merged_c1_elem[name] = c1.cube[name]
            else:
                merged_c1_elem[name] = c1.cube[name + "_x"]

        for name in c2_elem_names:
            if name not in c1_elem_names:
                merged_c2_elem[name] = c1.cube[name]
            else:
                merged_c2_elem[name] = c1.cube[name + "_y"]

        if felem is None:
            # if felem is not defined, keep both of the element
            c1.element = pd.concat([merged_c1_elem, merged_c2_elem], axis=1)
        else:
            elem1_list = merged_c1_elem.values.tolist()
            elem2_list = merged_c2_elem.values.tolist()
            merged_elem = []
            for i in range(0, len(elem1_list)):
                merged_elem.append(felem(elem1_list[i], elem2_list[i]))
            if len(felem_names) == len(merged_elem[0]):
                merged_elem = np.array([felem_names] + merged_elem)
            else:
                merged_elem = np.array(["dim" + str(i) for i in range(len(merged_elem[0]))] + merged_elem)
            c1.element = table_df = pd.DataFrame(data=merged_elem[1:,0:], columns=merged_elem[0,0:])
        # delete dimension that was not exist
        for name in c1.cube.columns:
            if name not in c1_dim_names and name not in c2_dim_names:
                c1.cube = c1.cube.drop(columns=[name])
        return c1