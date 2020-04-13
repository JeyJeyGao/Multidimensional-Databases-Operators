from Backend import Backend
import mysql_setup.coronavirus as coronavirus
import mysql_setup.coronavirus_location as coronavirus_location
import datetime

if __name__ == "__main__":
    backend = Backend()
    backend.start_connection()
    # backend.update_coronavirus_data()
    # cube = backend.get_cube(coronavirus.table_name,1)
    # cube.show()
    # location_cube = backend.get_cube(coronavirus_location.table_name,1)
    # location_cube.show()
    # cube.push("date")
    # joined = cube.join(location_cube)
    # joined.show()
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
    # example_1d = backend.get_cube("example_1d", 2)
    example_2d = backend.get_cube("example_2d", 1)
     # example_3d = backend.get_cube("example_3d", 1)

    # example join operator on the paper
    C = backend.get_cube("example_join_left",1)
    C.show()
    C1 = backend.get_cube("example_join_right",1)
    C1.show()
    dimension_name = {"D1":"D1"}
    f1 = [lambda x:[int(x)]]
    f2 = [lambda x:[int(x)]]
    felem = lambda e1_row, e2_row: [int(e1_row[0]) / int(e2_row[0])]
    joined_C = C.join(C1, felem, ["merged_val"], dimension_name, f1, dimension_name, f2)
    # joined_C = C.join(C1)
    joined_C.show()

    # example merge operator on the paper
    dimension_name = {"date":"month", "product":"category"}
    f = [
        lambda x: [x.replace(day = 1)],
        lambda x: ["cat1" if x=="p1" or x=="p2" else "cat2"]
    ]
    felem = lambda x : x.sum()
    merged_2d = example_2d.merge(felem, dimension_name, f)
    merged_2d.show()

    #example associate
    c = merged_2d.restriction("month", lambda x:x == datetime.date(2020,2,1) or x == datetime.date(2020,1,1))
    c.show()

    dimension_name = {"month":"date", "category":"product"}
    dimension_name2 = {"date":"date", "product":"product"}
    f = [
        lambda x: [x.replace(day = i) for i in range(1,5)],
        lambda x: ["p1","p2"] if x=="cat1" else ["p3","p4"]
    ]
    f2 = [
        lambda x: [x],
        lambda x: [x]
    ]
    felem = lambda x, y: [float(y[0]) / float(x[0])]
    felem_names = ["merged_val"]
    associated_cube = c.associate(example_2d, felem, felem_names, dimension_name, f, dimension_name2, f2)
    associated_cube.show()