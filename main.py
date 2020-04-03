from Cube import Cube
from Backend import Backend
import mysql_setup.coronavirus as coronavirus
import mysql_setup.coronavirus_location as coronavirus_location

if __name__ == "__main__":
    backend = Backend()
    backend.start_connection()
    cube = backend.get_cube(coronavirus.table_name)
    cube.show()
    cube = cube.push("date")
    cube.show()
    cube = cube.push("country_state")
    cube.show()
    cube = cube.pull("date")
    cube.show()
    predicate_func = lambda x:x=="Washington"
    cube = cube.restriction("province_state", predicate_func)
    cube.show()
    cube = cube.destroy("date")
    cube.show()
    cube = cube.destroy("province_state")
    cube.show()
    