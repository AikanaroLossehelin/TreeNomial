# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 10:34:15 2023

@author: aikan
"""

from neostruct import *
from WindowBox import *
import datetime
import time

def set_will_tree(value:bool) :
    #Change la valeur de la variable de voeu d'exécution (Wanted).
    global Wanted
    Wanted = value

def exe_tree(param:Parameters) :
    #Calcule un arbre et le temps de construction et de pricing.
    tree = Tree.make(param)
    
    t0 = time.time()
    tree.update()
    tfin = time.time()
    
    duration = tfin - t0
    
    del t0, tfin
    
    return tree, duration
    

def TreeWindow() :  
    global Wanted
    
    while Wanted :
        #On récupère la liste des derniers paramètres utilisés
        last_values = convert_parameters(read_file())
        
        # Choix de la saisie manuelle
        button("Manual Entry", "Do you want to manually enter the pricing parameters?", on_click, off_click)
        Choice = get_choice()
    
        parameters = None
        date_parameters = None
        app = None
    
        if Choice :
            #Fenêtre de saisie des paramètres hors dates.
            app = CustomWindow(Title = "Parameter Entry", 
                               Question = "Enter the parameters",
                               ListNameVal = ["Option Type", "Catégory", "Number of Steps", "Spot", 
                                              "Strike", "Volatility", "Rate", "Dividend", "Scale"])
            
            for i in range(len(last_values[:9])) :
                app.prefill_entry(i,last_values[i])
            app.mainloop()
        
            parameters = CustomWindow.get_param()
            parameter = parameters[0:2] + [eval(parameters[i]) for i in range(2,len(parameters))]
        
            #fenêtre de saisie des dates.
            app = DateEntryWindow(Title = "Date Entry",
                                  Question = "Enter dates in the format YYYY-MM-DD:",
                                  ListNameDate = ["Pricing date", "Ex-div date", "Maturity"])
            
            app.mainloop()
        
            date_parameters = DateEntryWindow.get_param()
            last_values = parameter + date_parameters + last_values[12:]
            update_file(last_values)
        
        if not Choice :
        
            # On exécute avec les paramètres renseignés dans last_values.txt
            date_parameters = last_values[9:12]
            parameter = last_values[:9]
            
        #Choix de l'activation du pruning
        button("Pruning", "Do you want to activate pruning?", on_click, off_click)
        Choice = get_choice()
    
        parameters = None
        app = None
        threshold = 0
    
        if Choice :
            app = CustomWindow(Title = "Threshold Entry",
                               Question ="Enter the threshold",
                               ListNameVal = ["Threshold"])
            app.mainloop()
        
            parameters = CustomWindow.get_param()
            threshold = eval(parameters[0])
    
        param = Parameters(date_parameters, parameter, Choice, threshold)
    
        # Suppression des variables créées pour le paramétrage
        del parameter, parameters, date_parameters, app, Choice, threshold
    
        #Choix de la recherche dess probabilités négatives
        button("Negative Probabilities", "Do you want to search for negative probabilities?", on_click, off_click)
        Choice = get_choice()
        
        tree, duration = exe_tree(param)
        #fenêtre de synthèse de notre pricing
        resumetree(param, tree, duration, Choice)
        
        del Choice, duration, tree
        #fennêtre permettant d'arrêter le programme ou de le réexécuter
        button("New Entry", "Would you like to recalculate a tree?", on_click, off_click)
        Wanted = get_choice()

if __name__ == '__main__' :
    
    Wanted = True
    TreeWindow()