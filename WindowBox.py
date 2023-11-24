# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 23:30:42 2023

@author: aikan
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import datetime
import time
import configparser

##########################################################################################################
############################################### BUTTONS ##################################################
##########################################################################################################
global Choice

def button(Title:str, Question:str, on_click, off_click):
    #Crée une fenêtre avec des boutons "Oui", "Non" pour une question donnée.
    global Choice
    Choice = None

    def handle_on_click():
        on_click()
        fenetre.destroy()

    def handle_off_click():
        off_click()
        fenetre.destroy()

    fenetre = tk.Tk()
    fenetre.title(Title)

    message = tk.Label(fenetre, text=Question)
    message.grid(row=0, column=0, columnspan=2)

    bouton_oui = tk.Button(fenetre, text="Yes", command=handle_on_click)
    bouton_oui.grid(row=1, column=0)

    bouton_non = tk.Button(fenetre, text="No", command=handle_off_click)
    bouton_non.grid(row=1, column=1)

    fenetre.update_idletasks()
    screen_width = fenetre.winfo_screenwidth()
    screen_height = fenetre.winfo_screenheight()
    x = (screen_width - fenetre.winfo_width()) // 2
    y = (screen_height - fenetre.winfo_height()) // 2
    fenetre.geometry('+{}+{}'.format(x, y))

    fenetre.mainloop()

def on_click():
    #Change la valeur de la variable globale de choix en vrai (True)
    global Choice
    Choice = True

def off_click():
    #Change la valeur de la variable globale de choix en vrai (True)
    global Choice
    Choice = False
    
def get_choice() :
    #Récupère la valeur de la variable globale de choix
    global Choice
    return Choice

def resumetree(param, tree, duration:float, Choice:bool):
    # Crée une fenêtre Tkinter qui résume l'ensemble des informations essentielles
    # au pricing par arbre trinomial de notre option
    fenetre = tk.Tk()
    fenetre.title("Informations")

    # Crée des libellés pour afficher les informations
    label1 = tk.Label(fenetre, text=f"Number of Steps : {param.nb_steps}")
    label1.pack()
    
    if param.threshold > 0 :
        label1bis = tk.Label(fenetre, text=f"Pruning Threshold : {param.threshold}")
        label1bis.pack()

    label2 = tk.Label(fenetre, text=f"Option Price : {tree.option.price}")
    label2.pack()

    label3 = tk.Label(fenetre, text=f"Execution Time : {duration}")
    label3.pack()
    
    if Choice :
        label4 = tk.Label(fenetre, text="Search Performed")
        label4.pack()
        label5 = tk.Label(fenetre, text=f"List of Negative Probabilities : {tree.search_neg()} ")
        label5.pack()
    else :
        label4 = tk.Label(fenetre, text="Search Aborted")
        label4.pack()

    # Lance la boucle principale de la fenêtre Tkinter
    fenetre.mainloop()
    

def resumegreeks(ListParamSpot:list, ListParamVol:list, greek_choice:list, GREEKS:list, nb_steps:int, threshold:float):
    # Crée une fenêtre Tkinter qui résume les informations essentielles sur le calcul des greeks choisis
    fenetre = tk.Tk()
    fenetre.title("Informations")

    # Crée des libellés pour afficher les informations
    label1 = tk.Label(fenetre, text=f"Number of Steps : {nb_steps}")
    label1.pack()
    
    if threshold > 0 :
        label2 = tk.Label(fenetre, text=f"Pruning Threshold : {threshold}")
        label2.pack()
        
    if greek_choice[0] or greek_choice[1] :
        label3 = tk.Label(fenetre, text=f"Spot 1 : {ListParamSpot[0].spot}")
        label3.pack()
        label4 = tk.Label(fenetre, text=f"Spot 2 : {ListParamSpot[1].spot}")
        label4.pack()
        if greek_choice[1] :
            label5 = tk.Label(fenetre, text=f"Spot 3 : {ListParamSpot[2].spot}")
            label5.pack()
    
    if greek_choice[2] :
        label6 = tk.Label(fenetre, text=f"Volatility 1 : {ListParamVol[0].volatility}")
        label6.pack()
        label7 = tk.Label(fenetre, text=f"Volatility 2 : {ListParamVol[1].volatility}")
        label7.pack()
    
    if greek_choice[0] :
        label8 = tk.Label(fenetre, text=f"Delta : {GREEKS[0]}")
        label8.pack()
    
    if greek_choice[1] :
        label9 = tk.Label(fenetre, text=f"Gamma : {GREEKS[1]}")
        label9.pack()
        
    if greek_choice[2] :
        label10 = tk.Label(fenetre, text=f"Vega : {GREEKS[2]}")
        label10.pack()

    # Lance la boucle principale de la fenêtre Tkinter
    fenetre.mainloop()


def click_button(choice:bool, choice_list:list, boutons):
    #Crée un bouton sur lequel on peut cliquer.
    choice_list[choice] = not choice_list[choice]  # Inverse le choix (True -> False, False -> True)
    boutons[choice].config(relief=tk.SUNKEN if choice_list[choice] else tk.RAISED)

def make_window(Title:str, Question:str, ListChoice:list):
    #Crée une fenêtre permettant de faire un ensemble de choix.
    fenetre = tk.Tk()
    fenetre.title(Title)

    question_label = tk.Label(fenetre, text=Question)
    question_label.pack()

    choice_list = [False] * len(ListChoice)  # Initialise une liste de booléens à False

    boutons = []  # Pour stocker les boutons
    for i, choix in enumerate(ListChoice):
        bouton = tk.Button(fenetre, text=choix, command=lambda c=i: click_button(c, choice_list, boutons))
        bouton.pack()
        boutons.append(bouton)

    def check():
        fenetre.destroy()
    
    bouton_valider = tk.Button(fenetre, text="Validate", command=check)
    bouton_valider.pack()

    fenetre.mainloop()
    
    return choice_list

##########################################################################################################
############################################## FILES #####################################################
##########################################################################################################

def read_file(file_path='last_values.txt') -> list:
    #Extrait les données du fichier last_values.txt qui stocke les données historiques
    #renseignées et retourne la valeur de chaque ligne dans une liste
    parameters = []
    
    with open(file_path, 'r') as file:
        for line in file:
            colon_index = line.find(': ')
            semicolon_index = line.find(';')
            
            if colon_index != -1 and semicolon_index != -1:
                value = line[colon_index + 1:semicolon_index].strip()
                parameters.append(value)

    return parameters

def convert_parameters(parameters:list) -> list:
    #Convertit une liste de paramètres extraits d'un fichier texte en liste
    #avec les bons types correspondants.
    converted_parameters = []

    for i, value in enumerate(parameters):
        if i in (0, 1):
            converted_parameters.append(str(value))
        elif i in (9, 10, 11):
            date_parts = [int(part) for part in value.split('-')]
            date_value = datetime.date(year=date_parts[0], month=date_parts[1], day=date_parts[2])
            converted_parameters.append(date_value)
        else:
            try:
                float_value = float(value)
                converted_parameters.append(float_value)
            except ValueError:
                print(f"Unable to Convert to Float : {value}")

    return converted_parameters


def update_file(parameters:list, file_path='last_values.txt') -> list:
    #Réécris le fichier last_values.txt à partir des dernières valeurs renseignées
    #dans une liste parameters
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        colon_index = line.find(': ')
        semicolon_index = line.find(';')

        if colon_index != -1 and semicolon_index != -1:
            
            if parameters:
                new_value = parameters.pop(0)

                if i in (0, 1):
                    new_value = str(new_value)
                elif i in (9, 10, 11):
                    date_parts = [int(part) for part in str(new_value).split('-')]
                    new_value = datetime.date(year=date_parts[0], month=date_parts[1], day=date_parts[2])
                else:  # Tous les autres éléments sont des floats
                    try:
                        float_value = float(new_value)
                        new_value = float_value
                    except ValueError:
                        print(f"Unable to Convert to Float : {new_value}")

                lines[i] = line[:colon_index + 2] + str(new_value) + line[semicolon_index:]

    with open(file_path, 'w') as file:
        file.writelines(lines)

# =============================================================================================
# Classe CustomWindow
# Classe fille de tk.TK
# Construit une fenêtre permettant de saisir des valeurs et de les récupérer.
# =============================================================================================

class CustomWindow(tk.Tk):
    
    global parameters
    
    def __init__(self, Title:str, Question:str, ListNameVal:list):
        super().__init__()
        self.title(Title)
        self.labels = []
        self.entries = []
        self.Question = Question
        self.create_widgets(ListNameVal)

    def create_widgets(self, ListNameVal:list):
        #Crée un widgets avec un ensemble de cases pour saisir des valeurs correspondant 
        #à une liste de noms (ListVal)
        n = len(ListNameVal)
        question_label = tk.Label(self, text=self.Question)
        question_label.grid(row=0, column=0, columnspan=2)
        for i in range(n):
            label = tk.Label(self, text=ListNameVal[i] + " : ")
            label.grid(row=i+1, column=0)
            self.labels.append(label)

            entry = tk.Entry(self)
            entry.grid(row=i+1, column=1)
            self.entries.append(entry)

        button = tk.Button(self, text="Validate", command=self.validate)
        button.grid(row=n+1, column=0, columnspan=2)

    def validate(self):
        #Crée un bouton de validation des choix et des saisies.
        global parameters
        parameters = [entry.get() for entry in self.entries]
        self.destroy()
        
    def prefill_entry(self, i:int, value:float):
        #Pré-rempli les champs de notre fenêtre.
        self.entries[i].insert(0, value)
    
    @staticmethod
    def get_param() :
        global parameters
        return parameters


# =============================================================================================
# Classe CustomWindow
# Classe fille de tk.TK
# Construit une fenêtre permettant de saisir des dates et de les récupérer.
# =============================================================================================


class DateEntryWindow(tk.Tk):
    
    global date_parameters
    
    def __init__(self, Title:str, Question:str, ListNameDate:list):
        super().__init__()
        self.title(Title)
        self.labels = []
        self.entries = []
        self.date_list = []
        self.Question = Question
        self.create_widgets(ListNameDate)

    def create_widgets(self, ListNameDate:list):
        #Crée un widgets avec un ensemble de cases pour saisir des valeurs correspondant 
        #à des dates par année, mois, jour.
        n = len(ListNameDate)
        question_label = tk.Label(self, text=self.Question)
        question_label.grid(row=0, column=0, columnspan=4)
        for i in range(n):
            label = ttk.Label(self, text=ListNameDate[i] + " : ")
            label.grid(row=i+1, column=0)

            year_entry = ttk.Entry(self)
            year_entry.grid(row=i+1, column=1)
            month_entry = ttk.Entry(self)
            month_entry.grid(row=i+1, column=2)
            day_entry = ttk.Entry(self)
            day_entry.grid(row=i+1, column=3)

            self.labels.append(label)
            self.entries.extend([year_entry, month_entry, day_entry])

        validate_button = ttk.Button(self, text="Validate", command=self.validate)
        validate_button.grid(row=n+1, column=0, columnspan=4)

    def validate(self):
        #Crée un bouton de validation des choix et des saisies et récupérer l'information
        #au format datetime.
        global date_parameters
        date_parameters = []
        for i in range(0, len(self.entries), 3):
            year_str = self.entries[i].get()
            month_str = self.entries[i + 1].get()
            day_str = self.entries[i + 2].get()
            try:
                year = int(year_str)
                month = int(month_str)
                day = int(day_str)
                date_obj = datetime.date(year, month, day)
                date_parameters.append(date_obj)
            except (ValueError, TypeError) as e:
                print(f"Date Format Error : {year_str}-{month_str}-{day_str}")
                return

        self.destroy()
        
    @staticmethod
    def get_param() :
        global date_parameters
        return date_parameters