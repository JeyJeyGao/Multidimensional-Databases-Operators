import pandas as pd 
import numpy as np
import copy
from visualization import Visualization

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
        
    def pull(self, dimensions_name, new_name=None):
        if dimensions_name not in self.element.columns:
            print("Error: {} is not a column name in the element tuple of the cube".format(dimensions_name))
            return self
        if new_name is None:
            new_name = dimensions_name
        new_cube = copy.deepcopy(self)
        new_cube.cube[new_name] = self.element[dimensions_name]
        new_cube.element = self.element.drop(columns=[dimensions_name])
        return new_cube

    def push(self, dimensions_name, new_name=None):
        if dimensions_name not in self.cube.columns:
            print("Error: {} is not a dimension of this cube".format(dimensions_name))
            return self
        if new_name is None:
            new_name = dimensions_name
        new_cube = copy.deepcopy(self)
        new_cube.element[new_name] = self.cube[dimensions_name]
        return new_cube

    def destroy(self, dimensions_name):
        if dimensions_name not in self.cube.columns:
            print("Error: {} is not a dimension of this cube".format(dimensions_name))
            return self
        dimensions_values = self.cube[dimensions_name]
        if len(dimensions_values) > 0:
            only_value = dimensions_values[dimensions_values.index[0]]
            for v in dimensions_values:
                if not v == only_value:
                    print("Error: Cannot destroy dimension, because more than one value in this dimension")
                    return self
        new_cube = copy.deepcopy(self)
        new_cube.cube = new_cube.cube.drop(columns=[dimensions_name])
        return new_cube

    # predicate_func receive the value of a row of this dimension, return true or false
    def restriction(self, dimensions_name, predicate_func):
        if dimensions_name not in self.cube.columns:
            print("Error: {} is not a dimension of this cube".format(dimensions_name))
            return self
        new_cube = copy.deepcopy(self)
        idx = new_cube.cube[dimensions_name].apply(predicate_func)
        new_cube.cube = new_cube.cube.loc[idx]
        new_cube.element = new_cube.element.loc[idx]
        return new_cube
    
    def __dimension_transform(self, cube, dimensions_names, f):
        if len(dimensions_names) == 0:
            return cube
        input_dim_names, output_dim_names = self.__parse_dimension_names(dimensions_names)
        if len(input_dim_names) != len(output_dim_names):
            print("Error: input_dim_names should have the same length as output_dim_names")
            return None
        elif len(input_dim_names) != len(f):
            print("Error: dimension_names should have the same length as function list f")
            return None
        cube = self.__dim_elem_merge(cube)
        res_cube = copy.deepcopy(cube)
        for i, name in enumerate(input_dim_names):
            for index, row in cube.cube.iterrows():
                if name not in cube.cube.columns:
                    print("Error: {} is not a dimension of this cube".format(name))
                    return cube
                func = f[i]
                maped_vals = func(row[name])
                if type(maped_vals) != list:
                    print("Error: function f should return a list of values")
                    return None
                # if mapping function f only return 1 value, then change it in the original place
                # else if return multiple value -> add new row
                res_cube.cube.at[index, name] = maped_vals[0]
                if len(maped_vals) > 1:
                    for value in maped_vals[1:]:
                        row[name] = value
                        res_cube.cube = res_cube.cube.append(row)
            res_cube.cube = res_cube.cube.reset_index(drop=True)
            cube.cube = copy.deepcopy(res_cube.cube)
        res_cube.cube = res_cube.cube.rename(columns={input_dim_names[i]: output_dim_names[i] for i in range(len(input_dim_names))})
        res_cube = self.__dim_elem_separate(res_cube)
        return res_cube
    
    # dimension_names: [[input dimension names],[output dimension names]]
    #   if no [output dimension names], that is means keep the original names
    def merge(self, felem, dimension_names, f):
        if felem == None or dimension_names == None or f == None:
            print("Error: parameters cannnot be None")
            return self
        elif len(dimension_names) != len(f):
            print("Error: function f list should have the same length as dimension_names")
            return self
        c = copy.deepcopy(self)
        c = self.__dimension_transform(c, dimension_names, f)
        dim_names = list(c.cube.columns)
        c = self.__dim_elem_merge(c)
        print(c.cube)
        c.cube = c.cube.groupby(dim_names).agg(
            felem
        ).reset_index()
        c = self.__dim_elem_separate(c)
        return c

    def associate(self, cube2, felem=None, felem_names=[], dimensions_names=[], f=[], dimensions_names2=[], f2=[]):
        # check: each dimension of C1 be joined with some dimension of C.
        c1_dim_names = list(self.cube.columns)
        c2_dim_names = list(cube2.cube.columns)
        for i, name in enumerate(dimensions_names):
            if name in dimensions_names:
                c1_dim_names[i] = dimensions_names[name]
        for i, name in enumerate(dimensions_names2):
            if name in dimensions_names2:
                c2_dim_names[i] = dimensions_names2[name]
        for name in c1_dim_names:
            if name not in c2_dim_names:
                print("Error: each dimension of C1 be joined with some dimension of C.")
                return self
        return self.join(cube2, felem, felem_names, dimensions_names, f, dimensions_names2, f2)
            

    # cube2 is the other cube to be joined
    # dimensions_names = [...] is a list of dimensions' names that cube and cube2 shared
    # f = [f...]; f2 = [f...]; are the funcitons that will apply for each dimension of cube and cube 2
    # felem(elem, elem2)->merged_elem is the function that will apply when the element of cube and the element of cube2 are going to be merged
    # defalue values:
    #   felem: c1.elem and c2.elem, input is (row in c1.elem, row in c2.elem)
    #   felem_names: the column names after merge the element
    #   dimensions_names: the comment dimension of each data cube
    #   f & f2: y = x
    def join(self, cube2, felem=None, felem_names=[], dimensions_names=[], f=[], dimensions_names2=[], f2=[]):
        # copy data
        c1 = self.__dimension_transform(self, dimensions_names, f)
        c2 = self.__dimension_transform(cube2, dimensions_names2, f2)
        c1_element_names = c1.element.columns
        c2_element_names = c2.element.columns
        # Merge phase
        #   find shared dimension
        shared_dim_names = list(set(list(c1.cube.columns)) & set(list(c2.cube.columns)))
        c1_m = self.__dim_elem_merge(c1)
        c2_m = self.__dim_elem_merge(c2)
        c1.cube = pd.merge(c1_m.cube, c2_m.cube,  how='inner', left_on=shared_dim_names, right_on = shared_dim_names)
        c1 = self.__dim_elem_separate(c1)
        merged_c1_elem = pd.DataFrame()
        merged_c2_elem = pd.DataFrame()
        for name in c1_element_names:
            if name not in c2_element_names:
                merged_c1_elem[name] = c1.element[name]
            else:
                merged_c1_elem[name] = c1.element[name + "_x"]
        for name in c2_element_names:
            if name not in c1_element_names:
                merged_c2_elem[name] = c1.element[name]
            else:
                merged_c2_elem[name] = c1.element[name + "_y"]
        if felem == None:
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
        return c1

    # dimension_names: [[input dimension names],[output dimension names]]
    #   if no [output dimension names], that is means keep the original names
    def __parse_dimension_names(self, dimension_names):
        if type(dimension_names) == dict:
            input_dim_names = []
            output_dim_names = []
            for in_name, out_name in dimension_names.items():
                input_dim_names.append(in_name)
                output_dim_names.append(out_name)
        elif type(dimension_names) == list:
            input_dim_names = dimension_names
            output_dim_names = dimension_names
        else:
            print("Error: dimension_names is ilegal.")
        return [input_dim_names, output_dim_names]
    
        # return a cube: dimension and element are merged    
    def __dim_elem_merge(self, cube):
        c = copy.deepcopy(cube)
        elem_names = c.element.columns
        for name in elem_names:
            c = c.pull(name, "element_" + name)
        return c
    
    def __dim_elem_separate(self, cube):
        c = copy.deepcopy(cube)
        dim_names = c.cube.columns
        c.element = pd.DataFrame()
        for name in dim_names:
            if "element_" in name:
                c = c.push(name, name[8:])
                c.cube = c.cube.drop(columns=[name]) 
        return c
