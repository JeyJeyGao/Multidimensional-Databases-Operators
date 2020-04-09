from Backend import Backend
import mysql_setup.coronavirus as coronavirus
import mysql_setup.coronavirus_location as coronavirus_location
import datetime

if __name__ == "__main__":
    backend = Backend()
    backend.start_connection()
    # backend.update_coronavirus_data()
    cube = backend.get_cube(coronavirus.table_name)
    cube.show()
    location_cube = backend.get_cube(coronavirus_location.table_name)
    location_cube.show()
    joined = cube.join(location_cube)
    joined.show()
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
    