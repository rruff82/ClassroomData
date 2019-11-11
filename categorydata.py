# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 11:58:38 2019

@author: ryan
"""

import numpy as np
import pandas

import os
import re

import matplotlib.pyplot as plt
input_src = os.path.expanduser('~/Documents/category-grades-fa19.csv')

cat_data = pandas.read_csv(input_src)



participation_cats = ["HOMEWORK","CLASSWORK"]
accuracy_cats = ["QUIZ","TEST"]
exam_cats = ["EXAM"]
all_cats = participation_cats+accuracy_cats+exam_cats

def grade_to_float(st):
    return float(st.split()[1][:-1])

for cat in all_cats:
    cat_data.drop(cat_data[cat_data[cat] == "--"].index, inplace=True)
    cat_data[cat] = cat_data[cat].apply(grade_to_float)



participation_avg = np.array(cat_data[participation_cats].sum(axis=1))/len(participation_cats)
accuracy_avg = np.array(cat_data[accuracy_cats].sum(axis=1))/len(accuracy_cats)
exam_avg = np.array(cat_data[exam_cats].sum(axis=1))/len(exam_cats)

label_a = "CW/HW"
label_b = "Quiz/Test"
label_c = "Exam"

def print_hist(scores,label):
    plt.hist(scores)
    plt.xlabel(label)
    plt.ylabel("#")
    plt.show()
    print(label+" mean:"+str(scores.mean()))
    print(label+" stdev:"+str(scores.std()))

for cat in all_cats:
    print_hist(cat_data[cat],cat)


print_hist(participation_avg,label_a)
print_hist(accuracy_avg,label_b)



def print_corr(s_a,l_a,s_b,l_b):
    plt.scatter(s_a,s_b)
    plt.xlabel(l_a)
    plt.ylabel(l_b)
    plt.plot(np.unique(s_a), np.poly1d(np.polyfit(s_a, s_a, 1))(np.unique(s_a)))
    plt.show()
    print("Correlation between " + l_a + " and " + l_b)
    print(np.corrcoef(s_a, s_b)[0][1])
    
print_corr(participation_avg,label_a,exam_avg,label_c)
print_corr(accuracy_avg,label_b,exam_avg,label_c)



plt.xlabel(label_a)
plt.ylabel(label_b)
plt.scatter(participation_avg,accuracy_avg,s=exam_avg**2/10+5,alpha=.5)
plt.plot(np.unique(participation_avg), np.poly1d(np.polyfit(participation_avg, accuracy_avg, 1))(np.unique(participation_avg)))

plt.show()


print("Correlation between " + label_a + " and " + label_b)
print(np.corrcoef(participation_avg, accuracy_avg)[0][1])

