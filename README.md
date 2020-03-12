# Multidimensional-Databases-Operators
This project implements the multidimensional databases operators for Rakesh Agrawal's paper. Rakesh Agrawal, Ashish Gupta, and Sunita Sarawagi. 1997. Modeling Multidimensional Databases. In Proceedings of the Thirteenth International Conference on Data Engineering (ICDE ’97). IEEE Computer Society, USA, 232–243.

## Plan to support operators:

- Pull
- Push
- Distory dimension
- Restriction
- Join
- Associate
- Merge

## Usage:

**Before start**

1. Edit config.json to connect to MySql backend
2. Start cube.py in interactive mode

**Example**

| Date   | Supplier | Product | Sales |
| ------ | -------- | ------- | ----- |
| Jan 1  | S1       | p1      | 5     |
| Sept 1 | S2       | P2      | 9     |

###### Import a cube from backend

c1 = Cube(t1)

###### save to backend

c1.save(t1)

###### Visualize a cube

c1.visualize()

###### Use operators

c = c1.push("product")  #push "product" dimension into elements

c = c1.join(c2,[f1...k, f'1...k], [f_elem], [dimensions...])

## Software Architecture Design

**Cube Store** 

**Backend Connection**

**Visulization Controller**

