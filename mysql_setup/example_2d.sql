CREATE TABLE `example_2d` (
                              `product` VARCHAR(50) NOT NULL,
                              `date` DATE NOT NULL,
                              `sales` INT(11) NOT NULL DEFAULT 0
);

INSERT INTO example_2d VALUES ('p1', '2020-3-4', 15);
INSERT INTO example_2d VALUES ('p3', '2020-3-4', 10);
INSERT INTO example_2d VALUES ('p1', '2020-2-3', 20);
INSERT INTO example_2d VALUES ('p2', '2020-2-3', 15);
INSERT INTO example_2d VALUES ('p3', '2020-2-3', 15);
INSERT INTO example_2d VALUES ('p4', '2020-2-3', 20);
INSERT INTO example_2d VALUES ('p2', '2020-2-2', 10);
INSERT INTO example_2d VALUES ('p3', '2020-2-2', 15);
INSERT INTO example_2d VALUES ('p1', '2020-1-1', 10);
INSERT INTO example_2d VALUES ('p3', '2020-1-1', 20);
INSERT INTO example_2d VALUES ('p4', '2020-1-1', 25);
