import cv2
import subprocess
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.scale
import itertools
import math
from scipy.interpolate import pchip

#returns list of all files (samples) without suffixes
def get_filelist():
    ls = []
    for file in os.scandir("converted/"):
        ls.append(file.name.removesuffix(".png"))
    return ls

def generate_paths():
    files = get_filelist()
    file = open("wsq_paths.txt", 'w')
    for f in files:
        file.write("gray/"+f+".wsq A\n")
    file.close()
    return 0

#compare the minuitae and write results to file
def all_to_all_comparisons(out_file):
    bozorth_comparisons = []

    #all to all comparisons
    for f in files:
        current_comparisons = []
        for f2 in files:
            a = str(subprocess.run(str("bozorth3 "+os.path.join(out_dir, f+".xyt")+" "+os.path.join(out_dir, f2+".xyt")), encoding='utf-8', capture_output=True).stdout).split("\n")[0]
            current_comparisons.append(int(a))
        bozorth_comparisons.append(current_comparisons)

    out = open(out_file, "w")
    out.write(str(bozorth_comparisons))
    out.close()

    return bozorth_comparisons

#returns array of nfiq estimates for all images
def get_nfiqs(filelist):
    nfiqs = []
    for file in filelist:
        n = str(subprocess.run(str("nfiq "+os.path.join("converted", file+".png")), encoding='utf-8', capture_output=True).stdout).split("\n")[0]
        nfiqs.append(int(n))
    return nfiqs

#bar plot: frequency/image quality
def plot_nfiqs(filelist):
    arr = get_nfiqs(filelist)
    values, counts = np.unique(arr, return_counts=True)
    plt.bar(values, counts)
    plt.xlabel("nfiq image quality values")
    plt.ylabel("frequency")
    plt.show()
    return 0

def plot_impostors():
    #read 2d array bozorth3 comparisons from the text file (so that they don't need to be computed every time)
    file = open("all_to_all.txt", "r")
    arr = eval(file.read())

    N = 200
    genuines = np.zeros(N)
    impostors = np.zeros(N)
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if math.floor(i/8) == math.floor(j/8):
                genuines[arr[i][j]] += 1
            else:
                impostors[arr[i][j]] += 1

    #bins for x-axis
    #M = 40
    #newGenuines = np.zeros(M)
    #newImpostors = np.zeros(M)
    #i = 0
    #for i in range(M):
    #    step = int(len(genuines)/M)
    #    newGenuines[i]=np.sum(genuines[i*step:i*step+step])
    #    newImpostors[i]=np.sum(impostors[i*step:i*step+step])

    #smoothen the curve for impostors (due to small sample size)
    #smp = np.array(range(len(genuines)))
    #x = np.linspace(smp.min(), smp.max(), 20)
    #plt.plot(x, pchip(smp, np.array(genuines))(x))
    #plt.plot(np.arange(M), newGenuines)
    #plt.plot(np.arange(M), newImpostors)

    plt.plot(np.arange(N), genuines[:N])
    plt.plot(np.arange(N), impostors[:N])
    plt.yscale('log')
    plt.xlabel("similarity")
    plt.ylabel("frequency")
    plt.legend(["genuines", "impostors"])
    plt.show()
    
    return 0

#heatmap
def plot_similarityMatrix():
    file = open("all_to_all.txt", "r")
    arr = eval(file.read())

    plt.imshow(arr)
    plt.colorbar()
    plt.title("Similarity matrix heatmap")
    plt.show()
    file.close()
    return 0

def threshold():
    return 19

def classification():
    ca = 0
    thr = threshold()

    file = open("all_to_all.txt", "r")
    arr = eval(file.read())

    pos = 0
    neg = 0
    correct = 0

    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i][j] > thr:
                pos+=1
                if math.floor(i/8) == math.floor(j/8):
                    correct += 1
            else:
                neg+=1
                if math.floor(i/8) != math.floor(j/8):
                    correct += 1

    ca = correct/(pos+neg)

    print("Classification accuracy: ", ca)

    return ca

#returns a dictionary in the form {subject_ID: fingerprint_type}
def get_types():
    types = {}
    files = get_filelist()

    with open("pcasys.out") as f:
        data = np.genfromtxt(itertools.islice(f, 0, len(files)), delimiter=';', dtype='str')

    for line in data:
        line = str(line)
        key = line.split(':')[0].strip('[\'').strip(".wsq")
        types[key] = line[line.find("hyp")+4]

    #print(types)
    return types

def get_id(index):
    file = get_filelist()[index]
    return file

def classification_by_type():
    types = get_types()

    ca = 0
    thr = threshold()

    file = open("all_to_all.txt", "r")
    arr = eval(file.read())

    pos = 0
    neg = 0
    correct = 0

    for i in range(len(arr)):
        id1 = get_id(i)
        for j in range(i+1, len(arr)):
            id2 = get_id(j)
            if types.get(id1) != types.get(id2): 
                continue
            if arr[i][j] > thr:
                pos+=1
                if math.floor(i/8) == math.floor(j/8):
                    correct += 1
            else:
                neg+=1
                if math.floor(i/8) != math.floor(j/8):
                    correct += 1

    ca = correct/(pos+neg)

    print("Classification accuracy (with grouping): ", ca)

    return ca


out_dir = "minutiae"
files = get_filelist()

plot_nfiqs(files)
plot_impostors()
plot_similarityMatrix()

#generate_paths()
#subprocess.run("pcasys pcasys.prs")

classification()
classification_by_type()
