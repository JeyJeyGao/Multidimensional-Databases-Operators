from Backend import Backend
import mysql_setup.coronavirus as coronavirus
import mysql_setup.coronavirus_location as coronavirus_location
import datetime

if __name__ == "__main__":
    backend = Backend()
    backend.start_connection()
    # backend.update_coronavirus_data()
    cube = backend.get_cube(coronavirus.table_name,1)
    cube.show()
    location_cube = backend.get_cube(coronavirus_location.table_name,1)
    location_cube.show()
    # cube.push("date")
    joined = cube.join(location_cube)
    joined.show()
    # joined.show()
    # corona_joined = backend.get_cube("corona_joined")
    # corona_joined.show()
    # cube = cube.push("date")
    # cube.show()
    # cube = cube.push("country_region")
    # cube.show()
    # cube = cube.pull("date")
    # cube.show()
    # predicate_func = lambda x:x=="Washington"
    # cube = cube.restriction("province_state", predicate_func)
    # cube.show()
    # cube = cube.destroy("date")
    # cube.show()
    # cube = cube.destroy("province_state")
    # cube.show()
    # corona_test = backend.get_cube("corona_test")
    # corona_test = corona_test.restriction("date", lambda x: x == datetime.date(2020, 3, 28)).destroy("date")
    example_1d = backend.get_cube("example_1d", 2)
    example_2d = backend.get_cube("example_2d", 1)
    example_3d = backend.get_cube("example_3d", 1)
    # example join operator on the paper
    C = backend.get_cube("example_join_left",1)
    C.show()
    C1 = backend.get_cube("example_join_right",1)
    C1.show()
    dimension_name = ["D1"]
    f1 = [lambda x:x]
    f2 = [lambda x:x]
    felem = lambda e1_row, e2_row: [int(e1_row[0]) / int(e2_row[0])]
    joined_C = C.join(C1, felem, ["merged_val"], dimension_name, f1, f2)
    joined_C.show()