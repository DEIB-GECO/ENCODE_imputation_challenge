import os
import pickle
import pandas as pd
import numpy as np
import time
import argparse

def getLabels(temp, k):
    copy = temp.copy()
    for i in range(len(temp)):
        if(k):
            copy[i] = copy[i][0:3]
        else:
            copy[i] = copy[i][3:6]
    copy = sorted(list(set(copy)))
    return copy

def getLabelsToPredict(assay,dirs):
    f_dirs = dirs.copy()
    result = []
    for i in range(len(f_dirs)):
        if(assay == f_dirs[i][3:6]):
            result.append(dirs[i])
    return result


def getPredictions(list,current_cell,cc,basepath):
    f_list = list.copy()
    s1 = f_list[0][0:3]
    sim_sum = cc.loc[current_cell,s1]
    array = np.load(basepath+list[0])*(cc.loc[current_cell,s1])
    for i in range(len(list)):
        if(i == 0):
            continue
        s2 = f_list[i][0:3]
        temp = cc.loc[current_cell,s2]
        array = array + (np.load(basepath+list[i])*cc.loc[current_cell,s2])
        sim_sum = sim_sum + temp
    return array/sim_sum


def computePrediction(validation,cc,new_dirs,basepath,out):
    cell_validation = validation.copy()
    assay_validation = validation.copy()
    for i in range(len(validation)):
        start_time = time.time()
        current_cell = cell_validation[i][0:3]
        current_assay = assay_validation[i][3:6]
        list = getLabelsToPredict(current_assay,new_dirs) #newdirs per il test set

        np.save(os.path.join(out+"/", validation[i]),getPredictions(list,current_cell,cc, basepath))
        end_time = time.time() - start_time
        print(str(validation[i])+" predicted in "+str(end_time))




def parse_args():

    parser = argparse.ArgumentParser(
            prog='AssayPrediction.py')

    parser.add_argument('inputPATH',
                        help='the path of the input numpy data: necessary for the technique, downsampled at 25bp and transformed with the sinh^-1')
    parser.add_argument('outputPATH',
                        help='Insert the output PATH of the folder where you want to save the predictions')
    args = parser.parse_args()
    return args

def main():
    args_score = parse_args()
    args = args_score.__dict__
    basepath = args['inputPATH'] + "/"
    df = pd.read_csv('MetadataTable.csv')
    Test = df.groupby('Training(T),Validation(V),Blind-test(B)')
    Test = Test.get_group('B')
    Test_label = Test[["Cell_ID", "Mark_ID"]]
    Test_label_ord = []
    for index, row in Test_label.iterrows():
        Test_label_ord.append((str(row['Cell_ID']) + str(row['Mark_ID'])+'.npy'))

    with open('validation_labels', 'rb') as fp:
        val_labels = pickle.load(fp)

    with open('signals', 'rb') as fp:
        ordered_dir = pickle.load(fp)

    new_dirs = sorted(ordered_dir + val_labels+Test_label_ord)
    cells_simil = pd.read_csv('outCxC.csv', index_col=0)
    computePrediction(Test_label_ord, cells_simil,new_dirs,basepath,args['outputPATH'])


if __name__ == '__main__':
    main()

