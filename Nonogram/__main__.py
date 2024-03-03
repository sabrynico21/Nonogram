import csv
import numpy as np
import argparse
import os 
import matplotlib.pyplot as plt
from .entities import Nonogram
from.utils import tabu_search

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='')
    #parser.add_argument('--file', help='Specify the name file of the example')
    parser.add_argument('--dim', help='Specify the dimension of the grid')
    parser.add_argument('epochs', help='Specify the number of epochs')
    args = parser.parse_args() 

    dim = int(args.dim)
    
    path = f'./Nonogram/Examples/{dim}x{dim}'
    files = os.listdir(path)
    picross_loss_values = []
    difficult = []
    for file in files:
        count = int(args.epochs)
        file_path = os.path.join(path, file)
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            first_row = next(reader)
            second_row = next(reader)
        loss_values = []
        while( count != 0 ):
            
            matrix = Nonogram(rows= len(first_row), cols = len(second_row))
            matrix.set_rows_counts(first_row)
            matrix.set_cols_counts(second_row)
            #print("expected row counts " ,matrix.row_counts)
            #print("expected col counts " ,matrix.col_counts)
            loss = tabu_search(matrix)
            #print(loss)
            count -= 1
            loss_values.append(loss)
           
        # print(file)
        #print(matrix.get_difficult())
        #
        difficult.append(matrix.get_difficult())
        loss_values.sort()
        picross_loss_values.append(loss_values)
        print(loss_values)
        
    q2 = np.percentile(np.array(difficult), 50)
    #print(difficult)
    difficult.sort(reverse=True)
    first_group_indices = np.where(difficult <= q2)[0]
    second_group_indices = np.where(difficult > q2)[0]
    
    for indices in [first_group_indices,second_group_indices]:
        group_loss = np.array([picross_loss_values[idx] for idx in indices])
        loss_mean = np.mean(group_loss, axis=0)

        unique_values, counts = np.unique(loss_mean, return_counts=True)
        cumulative_counts = np.cumsum(counts)

        plt.figure(figsize=(8, 6))
        plt.plot(unique_values, cumulative_counts, marker='o', linestyle='-')

        plt.xlabel('Loss values')
        plt.ylabel('Count')
        plt.title('Occurrences of Loss values')

        plt.grid(True)
        #name = args.file.split(".")[0]
        plt.savefig(f'./Nonogram/Images/first.png')
        plt.show()

    # loss_values.sort()
    # unique_values, counts = np.unique(loss_values, return_counts=True)
    # cumulative_counts = np.cumsum(counts)

    # # Plot the data
    # plt.figure(figsize=(8, 6))
    # plt.plot(unique_values, cumulative_counts, marker='o', linestyle='-')

    # plt.xlabel('Loss values')
    # plt.ylabel('Count')
    # plt.title('Occurrences of Loss values')

    # # Optionally, you can add a grid
    # plt.grid(True)
    # name = args.file.split(".")[0]
    # plt.savefig(f'./Nonogram/Images/{name}.png')
    # plt.show()