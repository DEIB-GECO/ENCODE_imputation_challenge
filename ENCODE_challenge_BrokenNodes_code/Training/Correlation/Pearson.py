import numpy as np
from numpy import empty
import os
import pickle
from scipy import stats
from multiprocessing import Pool
import time
import argparse


#Create a unique set of signals to work with for each process 
def createDirs(arrList, dirs,t):
    basevalue = int(len(dirs)/t)
    start = 0
    num = basevalue
    for i in range(t-1):
        arrList[i] = dirs[start:num]
        start = num
        num = num + basevalue
    arrList[t-1] = dirs[start:len(dirs)]
    return arrList

#Compute the Pearson correlation between two signals coming from the input path
def correlation(input, similarity, id, basepath, lenght,ordered_dir):
    print("process" +str(id)+" on")
    for i in range(len(input)):
        array = np.load(basepath + input[i])
        start_time = time.time()

        for j in range(lenght):
            second_array = np.load(basepath + ordered_dir[j])
            similarity[i, j], pvalue = stats.pearsonr(array, second_array)
        end_time = time.time() - start_time
        print("thread"+str(id)+": tempo riga"+ str(i)+ " = "+str(end_time))

    return similarity




def parse_args():

    parser = argparse.ArgumentParser(
            prog='Pearson.py')

    parser.add_argument('inputPATH',
                        help='the path of the input numpy data downsampled at 25bp and NOT transformed with the sinh^-1')
    args = parser.parse_args()
    return args

#Start three different process where each one performs a slice of the 267x267 similarity matrix
def main():
    args_score = parse_args()
    args = args_score.__dict__

    with open('signals', 'rb') as fp:
        dirs = pickle.load(fp)
    basepath = args['inputPATH']
    ordered_dir = sorted(dirs)
    lists = np.empty((3,), dtype=object)
    lists = createDirs(lists, ordered_dir, 3)
    ordered_dir1 = lists[0]
    ordered_dir2 = lists[1]
    ordered_dir3 = lists[2]
    lenght = len(dirs)
    similarity1 = empty((len(ordered_dir1), lenght))
    similarity2 = empty((len(ordered_dir2), lenght))
    similarity3 = empty((len(ordered_dir3), lenght))
    p = Pool()
    r = p.starmap(correlation, [(ordered_dir1,similarity1,"1",basepath,lenght,ordered_dir), (ordered_dir2,similarity2,"2",basepath,lenght,ordered_dir), (ordered_dir3,similarity3,"3",basepath,lenght,ordered_dir)])
    p.close()
    p.join()
    similarity = np.vstack((r[0], r[1], r[2]))
    np.save("Similarity.npy", similarity)

if __name__ == '__main__':
    main()
