import numpy as np

from tivars import TIRealList, TIMatrix


# Turn a list into a NumPy array
lst = TIRealList()
lst.open("../tests/data/var/RealList.8xl")

arr = np.asarray(lst.list(), dtype=float)
print(arr)


# Turn a matrix into a NumPy array
matrix = TIMatrix()
matrix.open("../tests/data/var/Matrix_3x3_standard.8xm")

arr = np.asarray(matrix.matrix(), dtype=float)
print(arr)
