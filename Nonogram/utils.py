import numpy as np
import random
from queue import LifoQueue
stack = LifoQueue(maxsize=)
def calculate_exceeding_penalty(solution):

    exceeding_penalty = 0
    for i in range(solution.cols):
        expected_col_sum = sum (count for count in solution.col_counts[i])
        actual_col_sum = solution.get_value_cells(i,"col").count(1)
        if actual_col_sum != expected_col_sum:
            exceeding_penalty += abs(expected_col_sum - actual_col_sum)
    
    return exceeding_penalty

# def sequence_lengths(array):
#     lengths = []
#     count = 0
#     for num in array:
#         if num == 1:
#             count += 1
#         elif count > 0:
#             lengths.append(count)
#             count = 0
#     if count > 0:
#         lengths.append(count)
#     return lengths

def calculate_completeness(solution):
    completeness = sum(solution.get_correct_col_groups_pct()) / solution.cols
    return 1 - completeness

def objective_function(solution, completeness_weight=0.5, penalty_weight=0.5):
    completeness = calculate_completeness(solution)
    exceeding_penalty = calculate_exceeding_penalty(solution)
    objective_score = completeness_weight * completeness + penalty_weight * exceeding_penalty
    return objective_score

def get_admissible_range(solution, group_indices, group_list, group_value):
    first_group_index = group_indices[0]    
    last_group_index = group_indices[-1]
    last_pred_index = np.where(group_list == (group_value -1))[0]
    first_next_index = np.where(group_list == (group_value +1))[0]
    value = 0 
    adm_range = []
    if len(last_pred_index) != 0: #c'è un gruppo precedente 
        last_pred_index = last_pred_index[-1]
        if (last_pred_index != first_group_index -2):
            value = -1
    else:
        if (first_group_index != 0):
            value = -1
    if value!= 0:    
        adm_range.append(value)
    value = 0
    if len(first_next_index) != 0: #c'è un gruppo successivo
        first_next_index = first_next_index[0]
        if (first_next_index != last_group_index + 2):
            value = 1
    else:
        if (last_group_index != solution.cols -1):
            value = 1
    if value!= 0:    
        adm_range.append(value)
    
    #max_value = solution.cols - (first_group_index + solution.actual_row_counts[row_index][group_value] - 1 )
    #first_other_index = np.where(group_list == (group_value + 1))[0]
    # if len(first_other_index) != 0: # Find the index of the first occurrence of another number
    #     distance = first_other_index[0] - last_group_index
    #     max_value = min(max_value, distance -2) #distanza tra corrente e successivo gruppo
    # min_value = - first_group_index
    # last_other_index = np.where(group_list == group_value-1)[0]
    # if len(last_other_index) != 0: 
    #     distance = last_other_index[-1] - first_group_index
    #     min_value = max(min_value, distance +2 )
    # range = np.arange(min_value,max_value)
    print(adm_range, "adm")
    return adm_range

def neighb(solution, indices):
    row_index = random.choice(indices)  #scelgo riga
    print("row: ", row_index)
    group_list = np.array([cell.group_row for cell in solution.matrix[row_index]])   
    #print(group_list)                      #scelgo gruppo da spostare
    unique_groups= set(value for value in group_list if value is not None)
    offset_values = []
    while (len(offset_values) == 0):
        print("ciao")
        group_value = random.choice(list(unique_groups)) #scelgo valore gruppo da spostare 
        print("group value: ", group_value)
        group_indices = np.where(group_list == group_value)[0]
        offset_values = get_admissible_range(solution, group_indices, group_list, group_value)
        print("off:", offset_values)
    #print(range)
    offset = random.choice(offset_values)
    print(group_indices, "antes")
    for group_index in group_indices:
        solution.matrix[row_index][group_index].value = 0
        #solution.modify_correct_col_groups_pct(group_index)
    
    group_indices = group_indices + offset
    print(group_indices, "despues")
    for group_index in group_indices:
        solution.matrix[row_index][group_index].value = 1
        solution.modify_correct_col_groups_pct(group_index)

    return solution
     
def function(solution, k):
    indices = np.array(solution.get_correct_row_groups())
    indices = np.where(indices != 2)[0] # ectract the index of rows in wich the groups don't are located correctly
    neighbors = []
    count = 0
    while (objective_function(solution) != 0 and count < 300):
        count+= 1
        #for _ in range(k):
        while (len(neighbors)!= k):
            neighbor = neighb(solution.__copy__(), indices)
            if neighbor != None:
                neighbors.append([neighbor, objective_function(neighbor)])
        objective_function_values = [element[1] for element in neighbors]
        min_value = min(objective_function_values)
        min_index = objective_function_values.index(min_value)
        if (min_value < objective_function(solution)):
            solution = neighbors[min_index][0]
            print("True")
            for row in solution.matrix:
                print([cell.value for cell in row])
            print(min_value)
            #memorizzare posizioni precedenti
            queue = [] # array di code 
            q = append di una tupla (gruppo, direzione) aggiungo in testa 
    return solution



