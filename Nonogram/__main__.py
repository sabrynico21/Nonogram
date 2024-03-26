import csv
import numpy as np
import argparse
import os 
import time
import matplotlib.pyplot as plt
from .entities import Nonogram
from.utils import tabu_search

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--mode', choices=['test', 'predict'], help='Specify the modality: test or predict')
    parser.add_argument('--file', help='Specify the file path in order to get the predition')
    parser.add_argument('--dim', type=int, help='Specify the dimension of the grid')
    parser.add_argument('epochs', nargs='?', default = 1, type=int, help='Specify the number of epochs')
    args = parser.parse_args() 
    
    if args.mode == 'test':
        dim = args.dim
        path = f'./Nonogram/Examples/{dim}x{dim}'
        files = os.listdir(path)         
    else:
        files = [args.file]
        
    epochs = args.epochs
    picross_loss_values = []
    picross_times = []
    difficult = []

    for f in files:
        count = epochs
        file_path = (os.path.join(path, f) if args.mode == 'test' else f)
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            first_row = next(reader)
            second_row = next(reader)
        loss_values = []
        execution_time = []
        while( count != 0 ):
            
            matrix = Nonogram(rows= len(first_row), cols = len(second_row))
            matrix.set_rows_counts(first_row)
            matrix.set_cols_counts(second_row)
            start_time = time.time()
            sol, loss = tabu_search(matrix)
            end_time = time.time()
            execution_time.append(end_time - start_time)
            loss_values.append(loss)  
            count -= 1
        
        difficult.append(matrix.get_difficult())
        loss_values.sort()
        picross_loss_values.append(loss_values)
        print("Loss: ",loss_values)
        print('Time:',execution_time)
        picross_times.append(execution_time)

    if (args.mode == 'test'):     
        q2 = np.percentile(np.array(sorted(difficult,reverse=True)), 50)
        
        first_group_indices = np.where(difficult > q2)[0]
        second_group_indices = np.where(difficult <= q2)[0]
        values = []
        cumulative_counts = []
        for indices in [first_group_indices,second_group_indices]:
            group_loss = np.array([picross_loss_values[idx] for idx in indices])
            loss_mean = np.mean(group_loss, axis=0)

            unique_values, counts = np.unique(loss_mean, return_counts=True)
            values.append(unique_values)
            cumulative_counts.append(np.cumsum(counts))

        plt.figure(figsize=(8, 6))
        
        plt.plot(values[0], cumulative_counts[0], marker='o', linestyle='-', label='Level 1')
        plt.plot(values[1], cumulative_counts[1], marker='s', linestyle='--', label='Level 2')

        plt.xlabel('Loss values')
        plt.ylabel('Count')
        plt.title('Occurrences of Loss values')
        plt.grid(True)
        plt.legend()
        plt.savefig(f'./Nonogram/Images/test_{dim}x{dim}.png')
        plt.show()
            
        picross_times = np.array(picross_times)
        #print(picross_times[first_group_indices].flatten())
        plt.figure(figsize=(8, 6))
        plt.boxplot([picross_times[first_group_indices].flatten(), picross_times[second_group_indices].flatten()], labels=['Level 1', 'Level 2'])

        # Adding labels and title
        plt.xlabel('Levels')
        plt.ylabel('Times (s)')
        plt.title('Game times')
        plt.grid(True)
        plt.savefig(f'./Nonogram/Images/times_{dim}x{dim}.png')
        plt.show()

    else:
        print("Solution: ")
        print(sol.game_table)
