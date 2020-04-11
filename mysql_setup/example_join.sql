CREATE TABLE `example_join_left` (
                              `D1` INT(11) NOT NULL,
                              `D2` VARCHAR(50) NOT NULL,
                              `sales` INT(11) NOT NULL DEFAULT 0
);

INSERT INTO example_join_left VALUES (0, 'a', 4);
INSERT INTO example_join_left VALUES (0, 'c', 8);
INSERT INTO example_join_left VALUES (1, 'b', 6);
INSERT INTO example_join_left VALUES (1, 'c', 9);
INSERT INTO example_join_left VALUES (2, 'a', 12);
INSERT INTO example_join_left VALUES (2, 'd', 14);
INSERT INTO example_join_left VALUES (3, 'a', 8);
INSERT INTO example_join_left VALUES (3, 'b', 9);
INSERT INTO example_join_left VALUES (3, 'c', 7);

CREATE TABLE `example_join_right` (
                              `D1` INT(11) NOT NULL,
                              `sales` INT(11) NOT NULL DEFAULT 0
);


INSERT INTO example_join_right VALUES (1, 3);
INSERT INTO example_join_right VALUES (2, 2);