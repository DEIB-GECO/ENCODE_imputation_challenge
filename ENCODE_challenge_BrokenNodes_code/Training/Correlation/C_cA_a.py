import pandas as pd
import numpy as np
import os
import pickle
import time

def getLabels(temp, k):
    copy = temp.copy()
    for i in range(len(temp)):
        if(k):
            copy[i] = copy[i][0:3]
        else:
            copy[i] = copy[i][3:6]
    copy = sorted(list(set(copy)))
    return copy

def getLabelList(dirs, label,k):
    temp = []
    for i in range(len(dirs)):
        copy = dirs.copy()
        if(k):
            if(copy[i][0:3]==label):
                temp.append(ordered_dir[i])
        else:
            if (copy[i][3:6] == label):
                temp.append(ordered_dir[i])
    return temp


def cellSimilarity(df, ordered_dir, labels,k):
    matrix = np.empty((len(labels), len(labels)))
    print(len(labels))
    for i in range(len(labels)):
        print(i)
        first_label = labels[i]
        first_list = getLabelList(ordered_dir,first_label,k)
        for j in range(len(labels)):
            if (labels[i] == labels[j]):
                matrix[i,j] = 1;
                continue
            second_label = labels[j]
            second_list = getLabelList(ordered_dir,second_label,k)
            new_df = df.loc[first_list, second_list]
            sum = new_df.values.sum()
            val = sum/(new_df.values.size)
            matrix[i,j] = val
    return matrix



with open ('signals', 'rb') as fp:
    ordered_dir = pickle.load(fp)
labels_cell = getLabels(ordered_dir, 1)
labels_assays = getLabels(ordered_dir, 0)
similarity = np.load("Similarity.npy")



df = pd.DataFrame(data = similarity, index = ordered_dir, columns= ordered_dir)
m_cells = cellSimilarity(df,ordered_dir,labels_cell,1)
m_assays = cellSimilarity(df,ordered_dir,labels_assays,0)

df_cells = pd.DataFrame(data = m_cells, index=labels_cell,columns=labels_cell)
df_assays = pd.DataFrame(data = m_assays, index=labels_assays, columns=labels_assays)
df_cells.to_csv('outCxC.csv')
df_assays.to_csv('outAxA.csv')
