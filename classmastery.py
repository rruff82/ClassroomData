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

mypath = os.path.expanduser('~/Documents/midtermmastery/*.csv')
gradesheets = glob.glob(mypath)

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
    if (len(children)>0):
        sol_groups[cat] = children

new_cols.extend(list(sol_groups.keys()))

new_cols.append("Overall")

records = []

for n in names:
    r = raw_df[raw_df["Name"]==n]
    record = [n]
    for sol in SOLs:
        record.append(float(r[r["SOL"]==sol]["Score"]))
    total_earned = r["Points"].sum()
    total_possible = r["Possible"].sum()
    
    for sol in SOLs:
        total_earned += float(r[r["SOL"]==sol]["Points"])
        total_possible += float(r[r["SOL"]==sol]["Possible"])
    
    for cat,catSOLs in sol_groups.items():
        points_earned = 0
        points_possible = 0
        for sol in catSOLs:
            points_earned += float(r[r["SOL"]==sol]["Points"])
            points_possible += float(r[r["SOL"]==sol]["Possible"])        
        record.append(points_earned/points_possible)
    record.append(total_earned/total_possible)            
    records.append(record)
    
    
sol_data = pandas.DataFrame(records,columns=new_cols)    

summaries = list(sol_groups.keys())
summaries.append("Overall")
    


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

pdf_pages = PdfPages('masteries.pdf')
for n in names:
    fig = plt.figure(figsize=(8.27, 11.69), dpi=100)
    plot_performance_by_SOL(n)
    pdf_pages.savefig(fig)

pdf_pages.close()
