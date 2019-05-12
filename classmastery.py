# -*- coding: utf-8 -*-
"""
A collection of utilities for analysing data from Power School Assessements
and Analytics.

This one reads a set of "Class Mastery" CSV files and prints some
summary data

Created on Mon May  6 14:34:35 2019

@author: ryan
"""
import os
import glob
import pandas
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans
input_src = os.path.expanduser('~/Documents/midtermmastery/*.csv')
output_graph = os.path.expanduser('~/Documents/midtermmastery/output_graph.pdf')

gradesheets = glob.glob(input_src)
numgroups = 6
threshold = .5

column_names = ["A","SOL","C","D","E","F","G","H","I","Name","Mastery","Pass","Score","N","Points","P","Possible","R","S","T","U","V","W","X","Y","Z","AA","AB","AC","AD","AE"]

dataframes = []
for i in gradesheets:
    d = pandas.read_csv(i,names=column_names)
    dataframes.append(d)




raw_df = pandas.concat(dataframes,ignore_index=True,sort=False)


names = raw_df["Name"].unique()
SOLs = raw_df["SOL"].unique()
new_cols = ["Name"]
new_cols.extend(SOLs)

sol_groups = dict()
for i in range(1,13):
    cat = "G."+str(i)
    children = []
    for sol in SOLs:
        if (sol.find("."+cat+".") > -1):
            children.append(sol)
        elif (sol.find("."+cat+" ") > -1):
            children.append(sol)
        elif (sol.find("."+cat+"\0") > -1):
            children.append(sol)
    if (len(children)>0):
        sol_groups[cat] = children

new_cols.extend(list(sol_groups.keys()))

new_cols.append("Overall")

records = []

for n in names:
    r = raw_df[raw_df["Name"]==n]
    record = [n]
    for sol in SOLs:
        record.append(r[r["SOL"]==sol]["Score"].sum())
    total_earned = r["Points"].sum()
    total_possible = r["Possible"].sum()
    
    for sol in SOLs:
        total_earned += r[r["SOL"]==sol]["Points"].sum()
        total_possible += r[r["SOL"]==sol]["Possible"].sum()
    
    for cat,catSOLs in sol_groups.items():
        points_earned = 0
        points_possible = 0
        for sol in catSOLs:
            points_earned += r[r["SOL"]==sol]["Points"].sum()
            points_possible += r[r["SOL"]==sol]["Possible"].sum()
        if (points_possible > 0):
            record.append(points_earned/points_possible)
        else:
            record.append(0)
    if (total_possible > 0):
        record.append(total_earned/total_possible)            
    else:
        record.append(0)
    records.append(record)
    
    
sol_data = pandas.DataFrame(records,columns=new_cols)    

summaries = list(sol_groups.keys())
summaries.append("Overall")
    
## Print an overall summary of student mastery by SOL 

for cat in summaries:
    print("***************************************")
    print(cat+" Summary")
    mastered = sol_data[sol_data[cat]>=.64]
    close = sol_data[sol_data[cat]>=.60]
    far = sol_data[sol_data[cat]>=.50]
    intervention = sol_data[sol_data[cat]<.50]
    far = far[far[cat]<.64]
    close = close[close[cat]<.6]
    print("---------------------------------------")
    print("Students Mastered 64 to 100:\t" + str(mastered.shape[0]) + "\n")
    print(list(mastered["Name"]))
    print("---------------------------------------")
    print("Students Close 60 to 64:\t" + str(close.shape[0]) + "\n")
    print(list(close["Name"]))
    print("---------------------------------------")
    print("Students Far 50 to 60:\t" + str(far.shape[0]) + "\n")
    print(list(far["Name"]))
    print("---------------------------------------")
    print("Students Needing Intervention 0 to 50:\t" 
          + str(intervention.shape[0]) + "\n")
    print(list(intervention["Name"]))
    print("***************************************") 
    
# Export polar graphs visualizing student strengths by SOLs
import numpy as np    
import matplotlib.pyplot as plt

def plot_performance_by_SOL(n):
    record = sol_data[sol_data["Name"]==n]
    scores = record[list(sol_groups.keys())].values
    num = len(sol_groups.keys())
    tau = 2*np.pi
    r = np.append(scores,scores[0][0])
    
    theta = np.mod(np.array(range(0,num+1)),num)/num*tau
    
       
    ax = plt.subplot(111, projection='polar')
    ax.plot(theta, r)
    ax.set_rmax(1)
    #ax.set_rticks([0.25, .50, .75, 1])  # Less radial ticks
    #ax.set_rlabel_position(-22.5)  # Move radial labels away from plotted line
    
    ax.set_rgrids([.25,.5,.75],labels=["","","",""],angle=360/num/2)
    
    ax.set_theta_direction = 1
    ax.set_theta_offset(tau/4)
    ax.set_thetagrids(theta[0:-1]/tau*360,labels=list(sol_groups.keys()))
    
    ax.grid(True)
    
    ax.set_title(n, va='bottom')
    
    plt.show()    

from matplotlib.backends.backend_pdf import PdfPages

pdf_pages = PdfPages(output_graph)
for n in names:
    fig = plt.figure(figsize=(8.27, 11.69), dpi=100)
    plot_performance_by_SOL(n)
    pdf_pages.savefig(fig)

pdf_pages.close()


#Find groups of students with similar profiles and group together

#Cluster the data into desired number of groups

df=sol_data[list(sol_groups.keys())]
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
sol_data["Group"]=groups
sortedData = sol_data.sort_values(['Group','Name'],ascending=[1, 1])




# Output analysis
print("**************************************")
print("Overall trends:")
meanOfMeans = np.mean(means)
std2 = np.std(means)
zMeta = (means-meanOfMeans)/std2
lowSOLs = []
highSOLs = []
for i in range(len(zMeta)):
    if (zMeta[i] < -threshold):
        lowSOLs.append(i+1)            
    elif (zMeta[i] > threshold):
        highSOLs.append(i+1)

print("Students did well on SOLs:")
print(highSOLs)
print("Students had a hard time on SOLs:")
print(lowSOLs)
print("SOL Vector:")
print(list(sol_groups.keys()))  

# Summarize groups


def profile_group(n):
    out = ""   
    for j in range(len(zScores[n])):
        if zScores[n][j] < -threshold:
            out = out + list(sol_groups.keys())[j] + ":Low,"     
        elif zScores[n][j] > threshold:
            out = out + list(sol_groups.keys())[j] + ":High," 
        else:
             out = out + list(sol_groups.keys())[j] + ":Avg,"
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
    print(groupDF["Name"])
    print("Group Profile:")
    print(profile_group(i))
    print("--------------------------------------")
