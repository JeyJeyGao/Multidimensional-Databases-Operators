import pandas as pd 

class Cube:
    def __init__(self, table_df):
        self.original_data = table_df
        self.cube = table_df.copy()
        self.element = pd.DataFrame()
    
    def export_table(self, ):
        rows = self.dimention_value + self.elements
        return (dimentions_name, rows)

    def print():
        pass
        
    def pull():
        pass

    def push():
        pass

    def destroy():
        pass

    def restriction():
        pass
    
    