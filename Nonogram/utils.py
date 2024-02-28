import numpy as np
import random
import math
from .entities import Memory
random.seed(42)

def normalize_array(arr):
    np_arr = np.array(arr)
    min_val = np.min(np_arr)
    max_val = np.max(np_arr)
    if min_val == max_val:
        return arr
    normalized_arr = (np_arr - min_val) / (max_val - min_val)
    return normalized_arr.tolist() 

def calculate_exceeding_groups(solution): 
    exceeding_penalty = 0
    for i in range(solution.num_cols):
        len_actual = len(solution.actual_col_counts[i])
        len_expected = len(solution.col_counts[i])
        if len_actual != len_expected:
            exceeding_penalty += abs(len_expected - len_actual)

    return exceeding_penalty

def calculate_exceeding_len(solution): 
    exceeding_penalty = 0
    for i in range(solution.num_cols):
        expected_col_sum = sum (count for count in solution.col_counts[i])
        actual_col_sum = solution.get_value_cells(i,"col").count(1)
        if actual_col_sum != expected_col_sum:
            exceeding_penalty += abs(actual_col_sum - expected_col_sum)
    return exceeding_penalty

def calculate_completeness(solution):
    [solution.modify_group_mask(index, "col") for index in range(solution.num_cols)]
    [solution.modify_correct_col_groups_pct(index) for index in range(solution.num_cols)]
    completeness = sum(normalize_array(solution.get_correct_col_groups_pct())) / solution.num_cols
    return 1 - completeness

def objective_function(solution, completeness_weight=0.40, groups_penalty_weight=0.30, len_penalty_weight= 0.30):
    completeness = calculate_completeness(solution)
    exceeding_groups = calculate_exceeding_groups(solution)
    exceeding_len = calculate_exceeding_len(solution)
    objective_score = completeness_weight * completeness + groups_penalty_weight * exceeding_groups + len_penalty_weight * exceeding_len
    return objective_score

def roll_group(group_indices, offset, row):
    for index in group_indices:
        row[index] = 0
    group_indices = group_indices + offset
    for index in group_indices:
        row[index] = 1
    return row

def check_history(cache, solution, row_index, offset_value, group_indices): 
    row_to_check = solution.game_table[row_index].copy()
    row_to_check = roll_group(group_indices, offset_value, row_to_check)  
    items = cache.get_memory()
    for item in items:
        if (item[0] == row_index):
            if ( np.array_equal(row_to_check, item[1])) :
                return False
    return True 

def get_admissible_range(cache, solution, group_indices, group_list, group_value, row_index, count, descrease_count):
    first_group_index = group_indices[0]    
    last_group_index = group_indices[-1]
    last_pred_index = np.where(group_list == (group_value - 1))[0]
    first_next_index = np.where(group_list == (group_value + 1))[0]
    prob = random.choice(np.arange(math.ceil(solution.num_cols / 2)))
    if prob == 0 :
        max_value = solution.num_cols - last_group_index - 1   
        if len(first_next_index) != 0: 
            distance = first_next_index[0] - last_group_index
            max_value = min(max_value, distance -2) 
        min_value = - first_group_index   
        if len(last_pred_index) != 0 and group_value -1 != -1: 
            distance = last_pred_index[-1] - first_group_index
            min_value = max( min_value, distance + 2 )
        range = np.arange(min_value,max_value)
        #range = range[range != 0]
        range = range[~np.isin(range, [0, 1, -1])]
        values_to_remove = []
        for value in range:
            if not check_history(cache, solution, row_index, value, group_indices):
                values_to_remove.append(value)
        mask = np.isin(range, values_to_remove, invert=True)
        range = range[mask]
        return range
    else:
        adm_range = []
        # Check for a preceding group
        if group_value - 1 != -1:
            last_pred_index = last_pred_index[-1]
            if first_group_index - last_pred_index >= 3 and check_history(cache, solution, row_index, -1, group_indices):
                adm_range.append(-1)
        else:
            if (first_group_index != 0) and check_history(cache, solution, row_index, -1, group_indices):
                adm_range.append(-1)

        # Check for a succeeding group
        if len(first_next_index) > 0:
            first_next_index = first_next_index[0]
            if first_next_index - last_group_index >= 3 and check_history(cache, solution, row_index, 1, group_indices):
                adm_range.append(1)
        else:
            if (last_group_index != solution.num_cols -1) and check_history(cache, solution, row_index, 1, group_indices):
                adm_range.append(1)

    return adm_range

def neighb(cache, solution, indices, count, descrease_count):
    neighbors = []
    for row_index in indices:
        group_list = solution.group_mask_row[row_index]
        unique_groups = list(set(group_list[group_list != -1]))
        for group_value in unique_groups:
            offset_values = [] 
            group_indices = np.where(group_list == group_value)[0]
            offset_values = get_admissible_range(cache, solution.__copy__(), group_indices, group_list, group_value, row_index, count, descrease_count)
            if len(offset_values) == 0:
                continue
            neig = solution.__copy__()
            #for offset in offset_values:
            offset =random.choice(offset_values)
            for group_index in group_indices:
                neig.set_value(row_index, group_index, 0)

            new_group_indices = group_indices + offset
            for group_index in new_group_indices:
                neig.set_value(row_index, group_index, 1)
            
            for row in range(neig.num_rows):
                neig.modify_group_mask(row, "row")
            for col in range(neig.num_cols):
                neig.modify_group_mask(col, "col")
                neig.modify_correct_col_groups_pct(col)

            neighbors.append([neig, objective_function(neig)])
            cache.add((row_index,neig.game_table[row_index]))
    return neighbors

def tabu_search(solution):
    solution.initialize_cells_values() 
    print(print(objective_function(solution)))
    indices = np.array(solution.get_correct_row_groups())
    indices = np.where(indices != 2)[0] # ectract the index of rows in wich the groups don't are located correctly
    count = 0
    current_min = objective_function(solution)
    descrease_count = 0
    cache = Memory(solution.correct_row_groups.count(1) * 3)
    while (objective_function(solution) != 0 and count < 3000):
        count+= 1
        neighbors = neighb(cache, solution.__copy__(), indices, count, descrease_count)
        if (len(neighbors)== 0):
            cache.clear_memory()
            continue
        objective_function_values = [element[1] for element in neighbors]
        min_value = min(objective_function_values)
        min_index = objective_function_values.index(min_value)
        if (min_value < current_min or (count - descrease_count) > 1):
            solution = neighbors[min_index][0]
            current_min = min_value
            print(" current min value ", current_min)
            descrease_count = count
    print(" last iteration: ", count)
    print("\n")
    print(" Solution table:")
    print(solution.game_table)
    print("\n")
    print(" Solution col counts: ")
    print(solution.get_actual_col_counts())
    print("\n")
    print(" Percent of correct column group: ")
    print(solution.get_correct_col_groups_pct())
    print("\n")
    print(" Objective function: ")
    print(objective_function(solution))
    