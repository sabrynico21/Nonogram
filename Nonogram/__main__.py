import csv
from .entities_ import Nonogram
import numpy as np
from.utils_ import tabu_search
if __name__ == "__main__":
    file_path = "C:/Users/sabry/OneDrive/Desktop/picross_10.csv"
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        first_row = next(reader)
        second_row = next(reader)
        matrix = Nonogram(rows= len(first_row), cols = len(second_row))
        matrix.set_rows_counts(first_row)
        matrix.set_cols_counts(second_row)
    print("expected row counts " ,matrix.row_counts)
    print("expected col counts " ,matrix.col_counts)

    tabu_search(matrix)
