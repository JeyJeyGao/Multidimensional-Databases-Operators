import os


table_name = "corona_joined"
output_name = "corona_joined.sql"


def reformat(query):
    return query.format(table_name).replace("\n", "") + "\n"


def main():
    output = open(os.path.join("mysql_setup", output_name), "w")
    output.write(reformat("""CREATE TABLE `{}` (
                                   `country_region` VARCHAR(50) NOT NULL,
                                   `province_state` VARCHAR(50) NULL DEFAULT NULL,
                                   `date` DATE NULL DEFAULT NULL,
                                   `confirmed` INT(11) NULL DEFAULT NULL,
                                   `death` INT(11) NULL DEFAULT NULL,
                                   `latitude` FLOAT NOT NULL,
                                   `longitude` FLOAT NOT NULL
    );
    """))
    output.write(reformat("""INSERT INTO `{}` (country_region, province_state, date, confirmed, death, latitude, longitude)
    SELECT cases.country_region AS country_region, cases.province_state AS province_state, cases.date AS date, cases.confirmed AS confirmed, cases.death AS death, location.latitude, location.longitude
    FROM cases, location WHERE cases.country_region = location.country_region AND cases.province_state = location.province_state;
    """))
    output.write(reformat("""INSERT INTO `{}` (country_region, province_state, date, confirmed, death, latitude, longitude)
    SELECT cases.country_region AS country_region, cases.province_state AS province_state, cases.date AS date, cases.confirmed AS confirmed, cases.death AS death, location.latitude, location.longitude
    FROM cases, location WHERE cases.country_region = location.country_region AND ISNULL(cases.province_state) AND ISNULL(location.province_state) AND cases.country_region != 'US';
    """))
    output.close()
