# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 17:43:22 2023

@author: aikan
"""

from TreeWindow import *
from GreekWindow import *
from WindowBox import *
import sys

sys.setrecursionlimit(100000)
    
##########################################################################################################
################################################ MAIN ####################################################
##########################################################################################################

if __name__ == '__main__' :
    
    choice_list = make_window(Title = "Program Choice",
                              Question = "Choose what you want to compute:", 
                              ListChoice = ["Price", "Greeks"])
    
    if choice_list[0] :
        set_will_tree(True)
        TreeWindow()
        
    if choice_list[1] :
        set_will_greeks(True)
        GreekWindow()
    
    del choice_list