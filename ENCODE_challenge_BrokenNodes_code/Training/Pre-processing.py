import argparse
import os
import logging
import sys
import pyBigWig as pw
import numpy as np
from glob import glob

chroms = [248956422,242193529,198295559,190214555,181538259,170805979,159345973,145138636,138394717,133797422,135086622,
          133275309,114364328,107043718,101991189,90338345,83257441,80373285,58617616,64444167,46709983,50818468,156040895]

#Downsample the numpy signal at 25bp resolution
def undersample(v, window_size):
    n_samples = np.ceil(v.shape[0] / window_size).astype(int)
    v = np.resize(v, n_samples * window_size)
    v = v.reshape(-1, window_size)
    v = np.mean(v, axis=1)
    return v


#Load chromosomes name and lenght
def load_genome():
    genome = []
    with open(os.path.join(sys.path[0], "GRCh38_chrom_sizes.txt"), "r") as f:
        l = f.readline()
        while l:
            l = l.strip()
            ls = l.split("    ")
            genome.append((ls[0], int(ls[1])))
            l = f.readline()
    return genome

#Load the bigWig signal, convert it into numpy, then downsample at 25bp
# each chromosome with the undersample function
def load_bigwig(path, genome):
    bw = pw.open(path)
    vv = []
    for chrom, chrom_len in genome:
        vv.append(pw.values(chrom, 0, chrom_len, numpy=True))
    array = np.hstack(vv)
    start = 0
    stop = 0
    new_array = []
    array = np.nan_to_num(array)
    for j in range(len(chroms)):
        stop = stop + chroms[j]
        new_array = np.hstack((new_array, undersample(array[start:stop], 25)))
        start = stop
    return new_array


#Start converting each track then save the output signal in the output folder
def convert_files(training_path, output_training_path, output_sinh_path,genome):
    training_files = sorted(glob(os.path.join(training_path, "*.bigwig")))
    for tf in training_files:
        logging.info("Converting {}".format(os.path.basename(tf)))
        output_file = os.path.join(output_training_path,
                                   os.path.basename(tf).split(".")[0] + ".npy")
        output_sinh = os.path.join(output_sinh_path,
                                   os.path.basename(tf).split(".")[0] + ".npy")
        if not os.path.isfile(output_file):
            signal = load_bigwig(tf, genome)
            pw.save(output_file, signal)
        if not os.path.isfile(output_sinh):
            signal = load_bigwig(tf, genome)
            signal = np.arcsinh(signal)
            pw.save(output_sinh, signal)



def process():
    genome = load_genome()
    os.makedirs(outputPATH, exist_ok=True)
    os.makedirs(sinhPATH, exist_ok=True)
    convert_files(inputPATH, outputPATH, sinhPATH, genome)


def parse_args():

    parser = argparse.ArgumentParser(
            prog='Pre-processing.py')

    parser.add_argument('inputPATH',
                        help='Insert the input path ')
    parser.add_argument('outputPATH',
                        help='Insert the output PATH of the input signals in numpy format and downsampled at 25bp')
    parser.add_argument('sinhPATH',
                         help='Insert the output PATH of the input signals in numpy format, downsampled at 25bp and transformed with sinh^-1')
    args = parser.parse_args()
    return args

def main():
    args_score = parse_args()
    args = args_score.__dict__
    global inputPATH, outputPATH, sinhPATH
    inputPATH = args['inputPATH']
    outputPATH = args['outputPATH']
    sinhPATH = args['sinhPATH']
    process()

if __name__ == '__main__':
    main()