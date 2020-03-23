DROP DATABASE cubeTest;
CREATE DATABASE cubeTest;
USE cubeTest;
CREATE TABLE Product(
   ID   INT              NOT NULL,
   NAME VARCHAR (20)     NOT NULL,
   PRICE   INT           NOT NULL,
   PROVIDER  CHAR (25)   NOT NULL
);
INSERT INTO Product (ID, NAME, PRICE, PROVIDER)
VALUES (1, 'iPhone', 999, 'Apple');
INSERT INTO Product (ID, NAME, PRICE, PROVIDER)
VALUES (2, 'Galaxy', 799, 'Samsung');
