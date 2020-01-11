import pandas as pd
import os
import numpy as np
import time
import pickle
import argparse

def getAssayList(a):
    new = []
    t_l = training_dirs.copy()
    for i in range(len(training_dirs)):
        if t_l[i][3:6] == a:
            new.append(t_l[i][0:3])
    return new

def getCellList(c):
    new = []
    t_l = training_dirs.copy()
    for i in range(len(training_dirs)):
        if t_l[i][0:3] == c:
            new.append(t_l[i][3:6])
    return new

def getParameter(a, c, a_s, c_s, ratio):
    assay_list = getAssayList(a)
    cell_list = getCellList(c)
    assay_values = c_s.loc[c, assay_list].values
    cell_values = a_s.loc[a, cell_list].values
    assay_values = -np.sort(-assay_values)
    cell_values = -np.sort(-cell_values)
    topk_assay = np.ceil(len(assay_values)*ratio)
    topk_cell = np.ceil(len(cell_values)*ratio)
    assay_value = assay_values[:int(topk_assay)].sum()
    cell_value = cell_values[:int(topk_cell)].sum()

    return assay_value/(assay_value+cell_value)



def computePrediction(d_a, a_s, d_c , c_s,basepath_assays,basepath_cells,out):
    dummy_cell = d_a.copy()
    dummy_assay = d_a.copy()
    for i in range(len(d_a)):
        start_time = time.time()
        cell_signal = np.load(basepath_cells + d_c[i])
        assay_signal = np.load(basepath_assays + d_a[i])
        current_cell = dummy_cell[i][0:3]
        current_assay = dummy_assay[i][3:6]
        ratio_val = 0.2
        alpha = getParameter(current_assay, current_cell, a_s, c_s, ratio_val)
        prediction = assay_signal*alpha + cell_signal*(1-alpha)
        np.save(os.path.join(out+"/", str(d_a[i])), prediction)
        end_time = time.time() - start_time
        print(str(d_a[i]) + " predicted in " + str(end_time))



with open('validation_labels', 'rb') as fp:
    val_labels = pickle.load(fp)

with open('signals', 'rb') as fp:
    ordered_dir = pickle.load(fp)

new_dirs = sorted(ordered_dir + val_labels)

training_dirs = new_dirs




def parse_args():

    parser = argparse.ArgumentParser(
            prog='MergeAssayCells.py')

    parser.add_argument('assayPATH',
                        help='the path of the assay based predictions')
    parser.add_argument('cellPATH',
                        help='the path of the cell based predictions')
    parser.add_argument('outputPATH',
                        help='Insert the output PATH of the folder where you want to save the predictions')
    args = parser.parse_args()
    return args

def main():
    args_score = parse_args()
    args = args_score.__dict__
    cells_simil = pd.read_csv('outCxC.csv', index_col=0)
    assays_simil = pd.read_csv('outAxA.csv', index_col=0)

    basepath_assays = args['assayPATH']+"/"
    dirs_assays = os.listdir(args['assayPATH'])

    basepath_cells = args['cellPATH'] + "/"
    dirs_cells = os.listdir(args['cellPATH'])
    dirs_assays = sorted(dirs_assays)
    dirs_cells = sorted(dirs_cells)

    computePrediction(dirs_assays, assays_simil, dirs_cells, cells_simil,basepath_assays,basepath_cells,args['outputPATH'])


if __name__ == '__main__':
    main()
