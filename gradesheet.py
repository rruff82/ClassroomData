# -*- coding: utf-8 -*-
"""
Statistical Analysis on Midterm Data

Exported Grade Sheet CSV files from aa.powerschool.com

Created on Thu Apr 18 17:54:28 2019

@author: ryan
"""

import csv
import os
import glob
import pandas
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans

# desired number of groups
numgroups = 4

# high/med/low threshhold, by +/- z score
threshold = .5


# the directory where the files are located
mypath = os.path.expanduser('~/Documents/midtermdata/')
# a file pattern describing which to use
filepattern = "*.csv"

# load all the files in the directory and join them together
gradesheets = glob.glob(mypath+filepattern)

dataframes = []
for i in gradesheets:
    d = pandas.read_csv(i)
    dataframes.append(d)

df = pandas.concat(dataframes)

# the headers produced by powerschool are insanely long. shorten them up to just Q#
colnames = list(df)
for i in range(len(colnames)):
    if (i > 1):
        colnames[i] = "Q" + str(i-1)
        
df.columns = colnames

# drop the score column
del df["Score"]

# drop class averages
df = df.drop(df["Students"]=="Class Totals")

# set student name as default index
df = df.set_index("Students")

# decifer PowerSchools gradesheet madness to a simple 1=correct 0=incorrect set
def to_binary_answer(s):
    if (s=="X"):
        return 0;
    elif (len(s)==1):
        return 1;
    else:
        return 0;
df = df.applymap(to_binary_answer)

#Cluster the data into desired number of groups
kmeans = KMeans(n_clusters=numgroups, random_state=0).fit(df)
labels = kmeans.labels_

centers = kmeans.cluster_centers_
groups = kmeans.predict(df)

#grab some stats
means = []
stdevs = []
for q in list(df):
   means.append(df[q].mean())
   stdevs.append(df[q].std())
zScores = []
for c in centers:
    z = []
    for i in range(len(c)):
        z.append((c[i]-means[i])/stdevs[i])
    zScores.append(z)
        
        

# Assign group to each student and sort
df["Group"]=groups
sortedData = df.sort_values(['Group','Students'],ascending=[1, 1])




# Output analysis
print("**************************************")
print("Overall trends:")
meanOfMeans = np.mean(means)
std2 = np.std(means)
zMeta = (means-meanOfMeans)/std2
lowQs = []
highQs = []
for i in range(len(zMeta)):
    if (zMeta[i] < -threshold):
        lowQs.append(i+1)            
    elif (zMeta[i] > threshold):
        highQs.append(i+1)

print("Students did well on questions:")
print(highQs)
print("Students had a hard time on questions:")
print(lowQs)
  

# Summarize groups


def profile_group(n):
    out = ""   
    for j in range(len(zScores[n])):
        if zScores[n][j] < -threshold:
            out = out + "Q" + str(j+1) + ":Low,"     
        elif zScores[n][j] > threshold:
            out = out + "Q" + str(j+1) + ":High,"     
    out = out + "]"
    return out

print("**************************************")        
print("Students clustered into " + str(numgroups) + " groups.")
for i in range(numgroups):
    groupDF = sortedData[sortedData["Group"]==i]
    print("--------------------------------------")
    print("Group #"+str(i+1)+":")
    print("Center:")
    print(np.round(centers[i]*100)/100)
    print("Member List:")
    print(groupDF.index.get_values())
    print("Group Profile:")
    print(profile_group(i))
    print("--------------------------------------")





