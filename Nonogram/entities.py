
import random
import numpy as np

class Cell:
    def __init__(self, value):
        self._value = value 
        self._group_row = None
        self._group_col = None
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = value
    
    @property
    def group_row(self):
        return self._group_row
    
    @group_row.setter
    def group_row(self, value):
        self._group_row = value
    
    @property
    def group_col(self):
        return self._group_col
    
    @group_col.setter
    def group_col(self, value):
        self._group_col = value


class MatrixOfCells:
    def __init__(self, rows=10, cols=10, row_counts=None, col_counts=None, actual_row_counts=None ,actual_col_counts=None, correct_col_groups_pct= None):
        self.rows = rows
        self.cols = cols
        self.matrix = [[Cell(0) for _ in range(cols)] for _ in range(rows)]
        self.row_counts = ([0] * rows if row_counts == None else row_counts) #expected row_counts
        self.col_counts = ([0] * cols if col_counts == None else col_counts)
        self.actual_row_counts = ([0] * rows if actual_row_counts == None else actual_row_counts)
        self.actual_col_counts = ([0] * cols if actual_col_counts == None else actual_col_counts)
        self.correct_row_groups = [0] * rows #can assume tre values: 0 - the groups don't match, 1 - the groups match but can be translated, 2 - the groups match and are positioned correctly
        self.correct_col_groups_pct = ([0] * cols if correct_col_groups_pct == None else correct_col_groups_pct)
    
    def __copy__(self):
        copy = MatrixOfCells(self.rows, self.cols, self.row_counts, self.col_counts, self.actual_row_counts,self.actual_col_counts, self.correct_col_groups_pct)
        for row in range(copy.rows):
            for col in range(copy.cols):
                copy.matrix[row][col].group_row = self.matrix[row][col].group_row
                copy.matrix[row][col].group_col = self.matrix[row][col].group_col
                copy.matrix[row][col].value = self.matrix[row][col].value
        return copy

    
    def set_value(self, row, col, value):
        self.matrix[row][col] = Cell(value)
    
    def get_value(self, row, col):
        return self.matrix[row][col].value
    
    def get_row_counts(self):
        return self.row_counts
    
    def get_col_counts(self):
        return self.col_counts
    
    def set_rows_counts(self, list_of_counts):
        for i, counts in enumerate(list_of_counts):
            integer_list = [int(num) for num in counts.split()]
            self.row_counts[i] = integer_list
    
    def set_cols_counts(self, list_of_counts):
        for i, counts in enumerate(list_of_counts):
            integer_list = [int(num) for num in counts.split()]
            self.col_counts[i] = integer_list

    def get_value_cells(self, index, type):
        if type == "row":
            return [element.value for element in self.matrix[index]]
        else: 
            return [row[index].value for row in self.matrix]
    
    # def get_group_cells(self, index, type):
    #     if type == "row":
    #         return [element.group for element in self.matrix[index]]
    #     else: 
    #         return [row[index].group for row in self.matrix]
    
    def modify_correct_row_groups(self, index): 
        #actual_counts = self.sequence_lengths(index,"row")
        self.sequence_lengths(index,"row")
        if self.row_counts[index] == self.actual_row_counts[index]:
            if sum(element for element in self.actual_row_counts[index]) + (len (self.actual_row_counts[index]) - 1) == self.rows:
                self.correct_row_groups[index] = 2 
            else:
                self.correct_row_groups[index] = 1
        else:
            self.correct_row_groups[index] = 0
    
    def modify_correct_col_groups_pct(self, index):
        percentage = 0
        #actual_counts = self.sequence_lengths(index,"col")
        self.sequence_lengths(index,"col")
        actual_len = len(self.actual_col_counts[index])
        expected_len = len(self.col_counts[index])
        
        for group in range (min( actual_len, expected_len)):
            percentage += self.actual_col_counts[index][group] / self.col_counts[index][group]
        difference = abs(actual_len - expected_len)
        for i in range(difference):
            percentage += 0
        self.correct_col_groups_pct[index] = percentage / max( actual_len, expected_len)

    def random_initialization(self):
        for i in range(self.rows):
            row_sum = sum( value for value in self.row_counts[i])
            cells = [index for index in range(self.cols)]
            columns = random.sample(cells, row_sum)  
            for j in columns:
                self.set_value(i, j, 1)

        for index in range(self.rows):
            self.modify_correct_row_groups(index)

    def initialize_cells_values(self):
        self.random_initialization()  
        correct_rows = np.flatnonzero(np.array(self.correct_row_groups))
        indices = np.setdiff1d(np.arange(self.rows), correct_rows)
        for row in indices: 
            while ( self.correct_row_groups[row] == 0):
                true_indices = np.flatnonzero(np.array(self.get_value_cells(row, "row")))
                false_indices = np.setdiff1d(np.arange(self.cols), true_indices)
                first_index = np.random.choice(true_indices)
                second_index = np.random.choice(false_indices)
                self.matrix[row][first_index].value = 0
                self.matrix[row][second_index].value = 1
                self.modify_correct_row_groups(row)

        for index in range(self.cols):
            self.modify_correct_col_groups_pct(index)
    
    def get_correct_row_groups(self):
        return self.correct_row_groups
    
    def get_correct_col_groups_pct(self):
        return self.correct_col_groups_pct
    
    def reset_groups(self, index, type):
        if type == "row":
            for element in self.matrix[index]:
                element.group_row = None
        else: 
            for row in self.matrix:
                row[index].group_col = None
    
    def sequence_lengths(self, index, type):
        array = self.get_value_cells(index, type)
        self.reset_groups(index, type)
        lengths = []
        count = 0
        positions = []
        group = 0 
        for i, num in enumerate(array):
            if num == 1:
                count += 1
                positions.append(i)
            elif count > 0:
                lengths.append(count)
                count = 0
                for pos in positions:
                    if type == "row":
                        self.matrix[index][pos].group_row = group
                    else:
                        self.matrix[pos][index].group_col = group
                group += 1
                positions = [ ]
        if count > 0:
            lengths.append(count)
            for pos in positions:
                if type == "row":
                    self.matrix[index][pos].group_row = group
                else:
                    self.matrix[pos][index].group_col = group
        if type == "row":
            self.actual_row_counts[index] = lengths
        else:
            self.actual_col_counts[index] = lengths


