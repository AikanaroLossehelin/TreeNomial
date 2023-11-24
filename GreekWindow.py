# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 10:37:17 2023

@author: aikan
"""

from compute_greeks import *
from neostruct import Parameters
from WindowBox import *
from copy import copy


def set_will_greeks(value:bool) :
    #Change la valeur de la variable de voeu d'exécution (Wanted).
    global Wanted
    Wanted = value
    
    
def make_param(param:list, i:int, List:list) -> list:
    #Crée une liste de Parameters à partir d'une liste de paramètres param qu'on va compléter
    #par différentes valeurs de la liste List afin de crée différents objets de classe Parameters
    global threshold
    global Choice
    global date_parameters
    
    param.insert(i, List[0])
    ListParam = [Parameters(date_parameters, param, Choice, threshold)]
    for k in range(1,len(List)) :
        param[i] = List[k]
        ListParam.append(Parameters(date_parameters, param, Choice, threshold))
    
    return ListParam


def input_param(Title:str, Question:str, ListNameVal:list, i:int, j:int, param:list, last_value:list) -> list :
    #Crée une fenêtre permettant la saisie d'un ensemble de valeurs (ListNameVal), qu'on stocke ensuite afin
    #de créer une liste de Parameters.
    app = CustomWindow(Title, Question, ListNameVal)
    
    loc = i
    if loc == 4 :
        loc+=1
    app.prefill_entry(0,last_value[loc])
    
    for k in range(1,len(ListNameVal)) :
        app.prefill_entry(k,"0")
    app.mainloop()

    parameters = CustomWindow.get_param()
    param.insert(i, eval(parameters[0])) 
    List = [eval(parameters[k]) for k in range(1,len(ListNameVal))]
    
    return make_param(param, j, List)


def auto_param(ListVal:list, i:int, j:int, param:list) -> list :
    #Crée une liste de Parameters à partir de paramètres déjà détenus dans une liste.
    param.insert(i, ListVal[0])
    return make_param(param, j, ListVal[1:len(ListVal)])
    
    
def GreekWindow() :
    global Wanted
    global threshold
    global Choice
    global date_parameters
    
    while Wanted :
        #On récupère la liste des derniers paramètres utilisés
        last_values = convert_parameters(read_file())
        
        # Choix de la saisie manuelle
        button("Manual Entry", "Do you want to manually enter the greeks' parameters?", on_click, off_click)
        Choice_glob = get_choice()
    
        parameters = None
        date_parameters = None
        app = None
        nb_steps = 100
    
        if Choice_glob :
            #Fenêtre de saisie des paramètres hors dates, volatilité et spot.
            app = CustomWindow(Title = "Parameter Entry", 
                               Question = "Enter the parameters",
                               ListNameVal = ["Option Type", "Catégory", "Number of Steps", 
                                              "Strike", "Rate", "Dividend", "Scale"])
            #Pré-remplissage des champs
            j = 0
            for i in (0, 1, 2, 4, 6, 7, 8) :
                app.prefill_entry(j,last_values[i])
                j+=1
            del j
            app.mainloop()
        
            parameters = CustomWindow.get_param()
            parameter = parameters[0:2] + [eval(parameters[i]) for i in range(2,len(parameters))]
            nb_steps = parameter[2]
            
            #fenêtre de saisie des dates.
            app = DateEntryWindow(Title = "Date Entry",
                                  Question = "Enter dates in the format YYYY-MM-DD:",
                                  ListNameDate = ["Pricing date", "Ex-div date", "Maturity"])
            app.mainloop()
        
            date_parameters = DateEntryWindow.get_param()
            #Pré-remplissage des champs
            j = 0
            for i in (0, 1, 2, 4, 6, 7, 8) :
                last_values[i] = parameter[j]
                j+=1
            del j
            
            for i in range(3):
                last_values[9+i] = date_parameters[i]
        
        if not Choice_glob :
        
            # On exécute avec les paramètres renseignés ici
            date_parameters = last_values[9:12]
            parameter = [last_values[i] for i in (0, 1, 2, 4, 6, 7, 8)]
            
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
            
        #Fenêtre de choix des greeks à calculer
        greek_choice = make_window(Title = "Greek Choice", 
                                   Question = "Which Greeks do you wish to calculate?", 
                                   ListChoice = ["Delta", "Gamma", "Vega"])
    
        ListParamSpot, ListParamVol = [], []
        DELTA, GAMMA, VEGA = 0, 0, 0
    
        paramvol, paramspot = copy(parameter), copy(parameter)
    
        if Choice_glob :
            #On calcule delta et/ou gamma
            if greek_choice[0] or greek_choice[1] :
                #Fenêtre de renseignement des paramètres nécessaires au calcul des greeks choisies
                ListParamSpot = input_param(Title = "Spot Entry",
                                            Question = "Enter the spots for the evaluation of the chosen Greeks (leave spot 3 empty if you have not selected gamma)",
                                            ListNameVal = ["Volatility", "Spot 1", "Spot 2", "Spot 3"], 
                                            i = 4, 
                                            j = 3,
                                            param = paramspot,
                                            last_value = last_values)
                
            
                if greek_choice[0] :
                    DELTA = delta(ListParamSpot[0], ListParamSpot[1])
                if greek_choice[1] :
                    GAMMA = gamma(ListParamSpot[0], ListParamSpot[1], ListParamSpot[2])
                
                for i in range(len(ListParamSpot)) :
                    last_values[12+i] = ListParamSpot[i].spot
                    
            #On calcule Vega
            if greek_choice[2] :
                #Fenêtre de renseignement des paramètres nécessaires au calcul des greeks choisies
                ListParamVol = input_param(Title = "Volatility Entry",
                                           Question = "Enter the volatilities for the evaluation of vega",
                                           ListNameVal = ["Spot", "Volatility 1", "Volatility 2"], 
                                           i = 3, 
                                           j = 5,
                                           param = paramvol,
                                           last_value = last_values)
            
                VEGA = vega(ListParamVol[0], ListParamVol[1])
                
                for i in range(len(ListParamVol)) :
                    last_values[15+i] = ListParamVol[i].volatility
            
        else :
            #On calcule delta et/ou gamma
            if greek_choice[0] or greek_choice[1] :
                
                list_val = [last_values[5]] + last_values[12:15]
                ListParamSpot = auto_param(ListVal = list_val, 
                                           i = 4, 
                                           j = 3,
                                           param = paramspot)
            
                if greek_choice[0] :
                    DELTA = delta(ListParamSpot[0], ListParamSpot[1])
                if greek_choice[1] :
                    GAMMA = gamma(ListParamSpot[0], ListParamSpot[1], ListParamSpot[2])
            #On calcule Vega
            if greek_choice[2] :
                
                list_val = [last_values[3]] + last_values[15:]
                ListParamVol = auto_param(ListVal = list_val, 
                                          i = 3, 
                                          j = 5,
                                          param = paramvol)
                
                VEGA = vega(ListParamVol[0], ListParamVol[1])
            
        GREEKS = [DELTA, GAMMA, VEGA]
        update_file(last_values)
        #fenêtre de synthèse de nos calculs et résultats.
        resumegreeks(ListParamSpot, ListParamVol, greek_choice, GREEKS, nb_steps, threshold)
        #fennêtre permettant d'arrêter le programme ou de le réexécuter
        button("New Entry", "Would you like to recalculate greeks?", on_click, off_click)
        Wanted = get_choice()

if __name__ == '__main__' :
    
    Wanted = True
    GreekWindow()