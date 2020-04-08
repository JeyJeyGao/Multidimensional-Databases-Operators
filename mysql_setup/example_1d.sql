CREATE TABLE `example_1d` (
                              `product` VARCHAR(50) NOT NULL,
                              `sales` INT(11) NOT NULL DEFAULT 0,
                              `d` VARCHAR(50) NOT NULL
);

INSERT INTO example_1d VALUES ('p1', 15, 'd1');
INSERT INTO example_1d VALUES ('p2', 20, 'd3');
INSERT INTO example_1d VALUES ('p3', 10, 'd4');
