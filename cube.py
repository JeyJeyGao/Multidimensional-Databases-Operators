import pandas as pd 
import numpy as np
import copy

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
            only_value = dimentions_values[0]
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