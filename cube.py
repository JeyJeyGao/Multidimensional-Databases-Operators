class Cube:
    def __init__(self):
        self.original_data = None
        self.dimentions_name = None
        self.dimention_value = None
        self.elements = None
    
    def load_table(self, dimentions_name, rows):
        if len(dimentions_name) < 1:
            print("Error: the number of dimention is 0.")
            return
        self.original_data = rows
        self.dimentions_name = dimentions_name
        self.dimention_value = rows[:-1]
        self.elements = rows[-1]

    def export_table(self, ):
        rows = self.dimention_value + self.elements
        return (dimentions_name, rows)
        

    def pull():
        pass

    def push():
        pass

    def destroy():
        pass

    def restriction():
        pass
    
    