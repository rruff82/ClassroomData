# -*- coding: utf-8 -*-

"""
A collection of utilities for analysing data from Power Teacher Pro 
scoresheet report.

This one reads a set of excel files and prints some
summary data.

My main goal with this was to compare two subsets of assignments to see which
was a better predictor of test success.

Created on Mon Mar 13 2019, 13:32:59

@author: ryan
"""

import numpy as np
import pandas

import os
import re

import matplotlib.pyplot as plt

input_src = os.path.expanduser('~/Documents/Scoresheet_May_14_2019.xlsx')

# my participation grades end with a date: MM/DD
mask_a = re.compile(r'.*[4-5]/[0-9]+$')
label_a = "Participation Score"
# my bookwork assignments start with a chapter and section X.Y
mask_b = re.compile(r'^[5-6].[0-9]+.*')
label_b = "Bookwook Score"
assessments = ["Chapter 5-6 Test"]
label_c = "Test Score"

# Note: requires xlrd package
scoresheet_raw = pandas.read_excel(input_src,sheet_name=None)

# sheets are named by class
classes = scoresheet_raw.keys()

df = pandas.concat(scoresheet_raw.values(),ignore_index=True)

new_cols = list(df.columns[:-1])
new_cols.append("Name")

df.columns = new_cols

#drop students who haven't taken assements[0]
df.drop(df[df[assessments[0]] == 0].index, inplace=True)

cols_a = []
cols_b = []
for col in new_cols:
    if (mask_a.match(col) is not None):
        cols_a.append(col)
    elif (mask_b.match(col) is not None):
        cols_b.append(col)




group_a_avg = np.array(df[cols_a].sum(axis=1))/len(cols_a)
group_b_avg = np.array(df[cols_b].sum(axis=1))/len(cols_b)
assessment_avg = np.array(df[assessments].sum(axis=1))/len(assessments)




plt.scatter(group_a_avg,assessment_avg)
plt.xlabel(label_a)
plt.ylabel(label_c)
plt.show()
print("Correlation between " + label_a + " and " + label_c)
print(np.corrcoef(group_a_avg, assessment_avg)[0][1])


plt.scatter(group_b_avg,assessment_avg)
plt.xlabel(label_b)
plt.ylabel(label_c)

plt.show()
print("Correlation between " + label_b + " and " + label_c)
print(np.corrcoef(group_b_avg, assessment_avg)[0][1])


plt.xlabel(label_a)
plt.ylabel(label_b)
plt.scatter(group_a_avg,group_b_avg,s=assessment_avg**2/10+5,alpha=.5)
plt.show()


print("Correlation between " + label_a + " and " + label_b)
print(np.corrcoef(group_a_avg, group_b_avg)[0][1])


