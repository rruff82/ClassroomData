# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 18:46:14 2019

@author: ryan
"""

import os
import pandas
import numpy as np

import io
import re 


xpdftotext = os.path.expanduser('~/Documents/xpdf-tools/bin64/pdftotext.exe')

source_pdf = os.path.expanduser('~/Downloads/individualStudentReport (1).pdf')

dest_txt = os.path.expanduser('~/Documents/individualReport.txt')

cmd_txt = xpdftotext+' -table "'+source_pdf+'" "'+dest_txt+'"'

os.system(cmd_txt)

lines = list()

report_state = {"student":"",
                "course":"",
                "teacher":"",
                "mode":"new",
                }


    
expected_columns = {"Final Grade":["Rpt. Term","Grade","Percent","Absent", 
                                   "Tardy","Missing","Late","Incomplete"],
                    "Standard Final Grade":["Rpt. Term","Identifier",
                                            "Name","Grade"],
                    "Assignment Scores":["Date","Category","Assignment",
                                         "Score","Pts Poss","Flags","Comment"]
                    }


with open(dest_txt,"r") as f:
    lines = f.readlines()



def starts_with(line,txt):
    return line[0:len(txt)]==txt

def get_student_name(line):
    return str.strip(line[len("Individual Student Report"):])
def get_class_info(line):
    tail = line[7:]
    teacher_idx = tail.find("Teacher: ")
    
    course_name = str.strip(tail[:teacher_idx])           
    teacher_name = str.strip(tail[(teacher_idx+9):])
    return course_name,teacher_name


rpt_term_patt = re.compile(r'^[A-Z][0-9]\s')
no_patt = re.complile(r'^No\s')
date_patt = re.compile(r'[0-9][0-9]/[0-9][0-9]/[0-9][0-9]\s')

item_patt = {"Final Grade":rpt_term_patt,
             "Standard Final Grade":no_patt,
             "Assignment Scores":date_patt
             }


line_queue = list()  

def reduce_queue():
    line_queue = list()
    
def read_line(l):
    if (l[0] == '\x0c'):
        # page break marker
        if (len(line_queue)):
            reduce_queue()
        read_line(l[1:])
    elif starts_with(l,"Individual Student Report"):
        report_state["student"] = get_student_name(l)
        report_state["mode"] = "Individual Student Report"
    elif starts_with(l,"Class: "):
        report_state["course"],report_state["teacher"] = get_class_info(l)
    else:
        for m in expected_columns.keys():
            if (starts_with(l,m)):
                if (len(line_queue)):
                    reduce_queue()
                report_state["mode"] = m
            elif 

                

