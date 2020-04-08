CREATE TABLE `example_3d` (
                              `supplier` VARCHAR(50) NOT NULL,
                              `product` VARCHAR(50) NOT NULL,
                              `date` DATE NOT NULL,
                              `sales` INT(11) NOT NULL DEFAULT 0
);

INSERT INTO example_3d VALUES ('s2', 'p1', '2020-3-4', 15);
INSERT INTO example_3d VALUES ('s1', 'p3', '2020-3-4', 10);
INSERT INTO example_3d VALUES ('s3', 'p1', '2020-2-3', 20);
INSERT INTO example_3d VALUES ('s3', 'p2', '2020-2-3', 15);
INSERT INTO example_3d VALUES ('s2', 'p3', '2020-2-3', 15);
INSERT INTO example_3d VALUES ('s1', 'p4', '2020-2-3', 20);
INSERT INTO example_3d VALUES ('s4', 'p2', '2020-2-2', 10);
INSERT INTO example_3d VALUES ('s3', 'p3', '2020-2-2', 15);
INSERT INTO example_3d VALUES ('s4', 'p1', '2020-1-1', 10);
INSERT INTO example_3d VALUES ('s4', 'p3', '2020-1-1', 20);
INSERT INTO example_3d VALUES ('s3', 'p4', '2020-1-1', 25);
