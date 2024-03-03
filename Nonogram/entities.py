import numpy as np
import random
import math
random.seed(42)
class Nonogram:
    def __init__(self, rows=10, cols=10, row_counts=None, col_counts=None, actual_row_counts=None ,actual_col_counts=None, correct_row_groups=None, correct_col_groups= None):
        self.num_rows = rows
        self.num_cols = cols
        self.game_table = np.zeros((self.num_rows, self.num_cols), dtype=int)
        self.group_mask_row = np.zeros((self.num_rows, self.num_cols), dtype=int)
        self.group_mask_col = np.zeros((self.num_rows, self.num_cols), dtype=int)

        self.row_counts = ([0] * rows if row_counts == None else row_counts) #expected row_counts
        self.col_counts = ([0] * cols if col_counts == None else col_counts)

        self.actual_row_counts = ([0] * rows if actual_row_counts == None else actual_row_counts)
        self.actual_col_counts = ([0] * cols if actual_col_counts == None else actual_col_counts)

        self.correct_row_groups = ([0] * rows if correct_row_groups == None else correct_row_groups) #can assume tre values: 0 - the groups don't match, 1 - the groups match but can be translated, 2 - the groups match and are positioned correctly
        self.correct_col_groups = ([0] * cols if correct_col_groups == None else correct_col_groups) 

    def __copy__(self):
        copy = Nonogram(self.num_rows, self.num_cols, self.row_counts, self.col_counts, self.actual_row_counts,self.actual_col_counts,None, self.correct_col_groups)
        for row in range(copy.num_rows):
            for col in range(copy.num_cols):
                copy.group_mask_row[row][col] = self.group_mask_row[row][col]
                copy.group_mask_col[row][col] = self.group_mask_col[row][col]
                copy.game_table[row][col] = self.game_table[row][col]
        return copy
    
    def set_value(self, row, col, value):
        self.game_table[row][col] = value
    
    def get_value(self, row, col):
        return self.game_table[row][col]
    
    def get_row_counts(self):
        return self.row_counts
    
    def get_col_counts(self):
        return self.col_counts
    
    def get_actual_col_counts(self):
        return self.actual_col_counts
    
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
            return [element for element in self.game_table[index]]
        else: 
            return [row[index] for row in self.game_table]
        
    def modify_correct_row_groups(self, index): 
        #self.modify_group_mask(index,"row") 
        if self.row_counts[index] == self.actual_row_counts[index]:
            if sum(element for element in self.actual_row_counts[index]) + (len (self.actual_row_counts[index]) - 1) == self.num_rows:
                self.correct_row_groups[index] = 2 
            else:
                self.correct_row_groups[index] = 1
        else:
            self.correct_row_groups[index] = 0

    # def modify_correct_col_groups_pct(self, index): #contare quante violazioni ci sono nei gruppi
    #     percentage = []
    #     #self.modify_group_mask(index,"col")  
    #     actual_len = len(self.actual_col_counts[index])
    #     expected_len = len(self.col_counts[index])

    #     if ( self.col_counts[index] == [0]):
    #         if (self.actual_col_counts[index] == [0]):
    #             self.correct_col_groups_pct[index] = 1.0
    #         else:
    #             self.correct_col_groups_pct[index] = 0.0
    #         return

    #     if (actual_len == expected_len): 
    #         for group in range (actual_len):      
    #             percentage.append(self.actual_col_counts[index][group] / self.col_counts[index][group])
    #         if sum(percentage) == float(actual_len):
    #             if percentage.count(1.0) != actual_len:
    #                 self.correct_col_groups_pct[index] = 0
    #                 return
    #         self.correct_col_groups_pct[index] = sum(percentage) / actual_len 
    #     else:
    #         self.correct_col_groups_pct[index] = 0
            # difference = actual_len - expected_len
            # mean_percentage = 0
            # if difference > 0: 
            #     for d in range(0, difference):
            #         percentage = 0
            #         for group in range (expected_len):
            #             percentage += self.actual_col_counts[index][group + d] / self.col_counts[index][group]
            #         mean_percentage += percentage / expected_len
            #     self.correct_col_groups_pct[index] = mean_percentage / (difference + 1 )
            # else:
            #     difference = - difference 
            #     for d in range(0, difference):
            #         percentage = 0
            #         for group in range (actual_len):
            #             percentage += self.actual_col_counts[index][group] / self.col_counts[index][group + d]
            #         mean_percentage += (percentage / actual_len if actual_len !=0 else 0)
            #     self.correct_col_groups_pct[index] = mean_percentage / (difference + 1 )
    
    def modify_correct_col_groups(self, index): #contare quante violazioni ci sono nei gruppi
        percentage = [] 
        actual_len = len(self.actual_col_counts[index])
        expected_len = len(self.col_counts[index])

        if ( self.col_counts[index] == [0]):
            if (self.actual_col_counts[index] == [0]):
                self.correct_col_groups[index] = [0]
            else:
                self.correct_col_groups[index] = [1]
            return
        
        num_groups = expected_len

        if (actual_len != expected_len): 
            num_groups = min(actual_len, expected_len)
        
        for group in range (num_groups):      
            if self.actual_col_counts[index][group] / self.col_counts[index][group] == 1.0:
                percentage.append(0)
            else:
                percentage.append(1)

        if (expected_len - actual_len > 0):
            for _ in range(actual_len - expected_len):
                percentage.append(1)

        self.correct_col_groups[index] = percentage

    def random_initialization(self):
        for i in range(self.num_rows):
            row_sum = sum( value for value in self.row_counts[i])
            cells = [index for index in range(self.num_cols)]
            columns = random.sample(cells, row_sum)  
            for j in columns:
                self.set_value(i, j, 1)

        for index in range(self.num_rows):
            self.modify_group_mask(index, "row")
            self.modify_correct_row_groups(index)
        for index in range(self.num_cols):
            self.modify_group_mask(index, "col")
            self.modify_correct_col_groups(index)
    
    def initialize_cells_values(self):
        self.random_initialization()  
        correct_rows = np.flatnonzero(np.array(self.correct_row_groups))
        indices = np.setdiff1d(np.arange(self.num_rows), correct_rows)
        for row in indices: 
            while ( self.correct_row_groups[row] == 0):
                true_indices = np.flatnonzero(np.array(self.get_value_cells(row, "row")))
                false_indices = np.setdiff1d(np.arange(self.num_cols), true_indices)
                first_index = np.random.choice(true_indices)
                second_index = np.random.choice(false_indices)
                self.set_value(row, first_index, 0)
                self.set_value(row, second_index, 1)
                self.modify_group_mask(row, "row")
                self.modify_correct_row_groups(row)

        for index in range(self.num_cols):
            self.modify_group_mask(index, "col")
            self.modify_correct_col_groups(index)
        
        # print(" Table inizialization ", self.game_table)
        # print("\n")
        # print(self.get_correct_col_groups_pct())
        #print(objective_function(self))

    def get_correct_row_groups(self):
        return self.correct_row_groups
    
    def get_correct_col_groups(self):
        return self.correct_col_groups
    
    def reset_groups(self, index, type):
        if type == "row":
            for col in range(self.num_cols):
                self.group_mask_row[index][col] = -1
        else: 
            for row in range(self.num_rows):
                self.group_mask_col[row][index] = -1
    
    def modify_group_mask(self, index, type):
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
                        self.group_mask_row[index][pos] = group
                    else:
                        self.group_mask_col[pos][index] = group
                group += 1
                positions = [ ]
        if count > 0:
            lengths.append(count)
            for pos in positions:
                if type == "row":
                    self.group_mask_row[index][pos] = group
                else:
                    self.group_mask_col[pos][index] = group

        if lengths == []:
            lengths.append(0)

        self.modify_actual_counts(index, type, lengths)
    
    def modify_actual_counts(self, index, type, lengths):
        if type == "row":
            self.actual_row_counts[index] = lengths
        else:
            self.actual_col_counts[index] = lengths
    
    def get_difficult(self):
        complexity = 0
        num_groups = 0
        for row in range(self.num_rows):
            complexity += sum(self.row_counts[row])
            num_groups += len(self.row_counts[row])
        return complexity / num_groups

class Memory:
    def __init__(self, max_size):
        self.max_size = max_size
        self.tabu_list = []

    def add(self, item):
        if len(self.tabu_list) >= self.max_size:
            self.tabu_list.pop(0)
        self.tabu_list.append(item)

    def get_memory(self):
        return self.tabu_list

    def clear_memory(self):
        self.tabu_list = self.tabu_list[ math.ceil(self.get_size() / 2)  : ] #int(self.get_size() / 2) + 1
        #self.memory = []

    def get_size(self):
        return len(self.tabu_list)

    def reset_memory(self):
        self.tabu_list = []
    
    def get_size(self):
        return len(self.tabu_list)