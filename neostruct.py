# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 18:15:13 2023

@author: aikan
"""

import math as mp
import xlwings as xw
import datetime
import time
from scipy.stats import norm


# =============================================================================================
# Parameters Class
# This class is used to store the parameters necessary for constructing and using the 
# financial options tree. It includes key dates, general tree parameters, 
# a pruning indicator, and a threshold for this pruning.
# =============================================================================================


class Parameters :
    
    def __init__(self, date_param, param, pruning, threshold) :
        self.pricing_date = date_param[0]
        self.date_ex_div = date_param[1]
        self.maturity = date_param[2]
        self.Type = param[0]
        self.Category = param[1]
        self.nb_steps = param[2]
        self.spot = param[3]
        self.strike = param[4]
        self.volatility = param[5]
        self.rate = param[6]
        self.dividend = param[7]
        self.scale = param[8]
        self.threshold = pruning * threshold
        self.delta_t = ((self.maturity-self.pricing_date).days)/(self.scale*self.nb_steps)
        self.alpha = mp.exp(self.volatility * mp.sqrt(3 * self.delta_t))
        
        

# =============================================================================================
# Option Class
# Represents a financial option. Stores the main characteristics of an option 
# such as its type (Call or Put), category (European or American), maturity date 
# and strike price. It also allows for the calculation of the option's payoff.
# =============================================================================================


class Option :
    
    def __init__(self, Type, Category, maturity, strike) :
        self.Type = Type
        self.Category = Category
        self.maturity = maturity
        self.strike = strike
        self.price = 0


    def payoff(self, spot:float) -> float :
        # Méthode qui calcule le payoff de l'option en fonction du prix actuel du sous-jacent (spot).
        Type = self.Type 
        strike = self.strike 
        
        if Type == "Call" :
            return max(spot - strike, 0)
        
        elif Type == "Put" :
            return max(strike - spot, 0)
        
        else :
            print("Le type n'est pas renseigné. On procède comme pour un call")
            return  max(spot - strike, 0)

# =============================================================================================
# Market Class
# Models a financial market by defining key parameters such as volatility, 
# interest rates, the current spot price, and dividends, as well as the dividend payout date.
# =============================================================================================


class Market :
    
    def __init__(self, volatility, rate, spot, dividend, date_ex_div) :
        self.volatility = volatility
        self.rate = rate
        self.spot = spot
        self.dividend = dividend
        self.date_ex_div = date_ex_div

# =============================================================================================
# Model Class
# Configures the modeling parameters of the options tree, such as the pricing date, 
# the number of steps, the maturity date, time scale, and pruning threshold.
# =============================================================================================


class Model :
    
    def __init__(self, pricing_date, nb_steps, maturity, scale, threshold) :
        self.pricing_date = pricing_date
        self.nb_steps = nb_steps
        self.delta_t = ((maturity-pricing_date).days)/(scale*nb_steps)
        self.scale = scale
        self.threshold = threshold


# =============================================================================================
# Node Class
# Represents a node in the options tree. Each node holds information about 
# the spot price, its neighbors, its transition probabilities, as well as methods for 
# calculating these probabilities and establishing links with neighboring nodes.
# =============================================================================================


class Node :
    
    def __init__(self, spot) :
        self.spot = spot
        self.neighbour_down = None
        self.neighbour_up = None
        self.next_down = None
        self.next_mid = None
        self.next_up = None
        self.Pdown = 0
        self.Pmid = 0
        self.Pup = 0
        self.Ptot = 0
        self.price = None
        self.Pneg = []

###################################### Méthode de calcul forward ##############################################


    def forward(self, alpha:float, market:Market, model:Model, tokken:bool) -> float:
        #Calcule la valeur forward d'un nœud dans l'arbre d'options financières.
        #La valeur forward est calculée en fonction de la raison de l'arbre (alpha),
        #un objet représentant le marché (market), un objet représentant le modèle 
        #financier (model), un tokken qui, lorsqu'il est vrai (True), soustrait 
        #les dividendes du calcul de la valeur forward. Cela reflète le paiement 
        #des dividendes à la date ex-dividende.
        
        delta_t = model.delta_t
        r = market.rate
        return self.spot * mp.exp(delta_t * r) - tokken * market.dividend
    

################################## Méthodes calcul probabilités ##############################################

    def compute_pdown(self, forward:float, rate:float, delta_t:float, volatility:float, alpha:float):
        #Calcule la probabilité d'accéder au prochain noeud inférieur grâce à la 
        #valeur forward du noeud, le taux du marché (rate), le pas de temps 
        #(delta_t), la volatilité du marché et la raison de l'arbre (alpha).
        
        S2 = self.next_mid.spot
        V = self.spot**2 * mp.exp(2 * rate * delta_t) * (mp.exp(volatility**2 * delta_t) - 1)
        self.Pdown = (1 / S2**2 * (V + forward**2) - 1 - (alpha + 1) * (1 / S2 * forward - 1)) / ((1 - alpha) * (1 / alpha**2 - 1))
           
        
    def compute_pup(self, forward:float, alpha:float):
        #Calcule la probabilité d'accéder au prochain noeud supérieur à partir 
        #de la valeur du forward du noeud et de la raison de l'arbre (alpha) 
        #après calcul de la probabilité Pdown.
 
        S2 = self.next_mid.spot
        self.Pup = (forward /S2 - 1 - self.Pdown * (1/alpha - 1)) / (alpha - 1)
    
    
    def compute_pmid(self):
        #Calcule la probabilité d'accéder au prochain noeud milieu à partir de Pup et Pdown.
        self.Pmid = 1 - self.Pup - self.Pdown
    
    
    def compute_ptot(self):
        #Calcule la proabilité d'accéder au noeuds suivants depuis la racine.
        self.next_mid.Ptot += self.Ptot * self.Pmid
        self.next_down.Ptot += self.Ptot * self.Pdown
        self.next_up.Ptot += self.Ptot * self.Pup
    
    
    def compute_proba(self, forward:float, rate:float, delta_t:float, volatility:float, alpha:float) :
        #Effectue le calcul de toutes les probabilités stockées dans le noeud.
        self.compute_pdown(forward, rate, delta_t, volatility, alpha) 
        self.compute_pup(forward, alpha)
        self.compute_pmid()
        self.compute_ptot()
        

######################################### Méthodes diverses ################################################

    
    def isClose(self, forward:float, alpha:float) -> bool :
        #Détermine si un noeud est proche d'un autre par moyennage arithmétique.
        return (forward <= self.spot*(1+alpha)/2) and (forward >= self.spot*(1+1/alpha)/2)
    
    
    def set_neighup(self, node) :
        #Enregistre un noeud (node) comme le voisin supérieur du noeud visité.
        self.neighbour_up = node
    
    
    def set_neighdown(self, node) :
        #Enregistre un noeud (node) comme le voisin inférieur du noeud visité.
        self.neighbour_down = node
    
    
    def move_up(self, alpha:float) :
        #Construit le noeud supérieur au noeud visité s'il n'existe pas.
        if self.neighbour_up == None :
            node = Node(self.spot * alpha)
            self.set_neighup(node)
            node.set_neighdown(self)
            return node
        else :
            return self.neighbour_up
    

    def move_down(self, alpha:float) :
        #Construit le noeud inférieur au noeud visité s'il n'existe pas.
        if self.neighbour_down == None :
            node = Node(self.spot / alpha)
            self.set_neighdown(node)
            node.set_neighup(self)
            return node
        else :
            return self.neighbour_down
    
    
    def breadth(self) -> int:
        #Calcule la profondeur de l'arbre en parcourant la branche composé de tous les 
        #noeuds du milieu. Cette fonction permet le contrôle de la profondeur au moment de la construction de l'abre.
        if self.next_mid == None :
            return 1
        else :
            return self.next_mid.breadth() + 1
    
    
    @staticmethod
    def search_neg(node, nb_steps: int, L: list) -> list:
        #Renvoie la liste des probabilités négatives présentes à chaque noeud en partant d'un noeud (node)
        #et en récupérant la liste locale des probabilités négatives contenue dans Pneg.
        
        i = 0  
        node_current = node  
        start_node = node
        next_column = node_current.next_down
        
        while i < nb_steps and not start_node is None:
            
            if node_current is not None:
                if node_current.Pneg != []:
                    L.append(node_current.Pneg)
                node_current = node_current.neighbour_up
            else:
                if next_column is None:
                    next_column = start_node.next_mid
                    if next_column is None:
                        next_column = start_node.next_up
                        if next_column is None:
                            start_node = start_node.neighbour_up
                            next_column = start_node.next_down
                else:
                    node_current = next_column
                    start_node = next_column
                    i += 1  
        return L



######################################### Méthodes d'update #################################################

    
    def update_down(self, alpha:float):
        #Met à jour les liaisons avec le voisin inférieur du noeud visité.
        next_down = self.next_mid.move_down(alpha)
        self.next_down = self.next_mid.neighbour_down = next_down
        self.next_down.neighbour_up = self.next_mid
  
    
    def update_up(self, alpha:float):
        #Met à jour les liaisons avec le voisin supérieur du noeud visité.
        next_up = self.next_mid.move_up(alpha)
        self.next_up = self.next_mid.neighbour_up = next_up
        self.next_up.neighbour_down = self.next_mid    
   
    
    def build(self, node, alpha:float, market:Market, model:Model, tokken:bool) :
        #Construit les noeuds fils du noeud visité en construisant son noeud fils milieu au niveau du
        #noeud fils dont la valeur du forward est la plus proche. L'emploie de la méthode isClose permet de 
        #diriger l'ascension ou la descente du noeud pour sa construction. Une fois que le noeud fils milieu
        #est construit, on met à jour le noeud visité en créant ses noeuds fils inférieur et supérieur. Enfin,
        #on calcule l'ensemble des probabilités d'accès aux différents noeuds fils et on stocke les probabilités
        #négatives dans Pneg.
        #NB : Si un noeud possède un voisin dont les enfants sont aussi des enfants de notre noeud, on s'y greffe
        #plutôt que de les recréer.
        
        forward = self.forward(alpha, market, model, tokken)
        
        if node is None:
            node_comp = Node(forward)
        else:
            node_comp = node

        if forward >= 0:
    
            while not node_comp.isClose(forward, alpha):
        
                if forward > node_comp.spot:
                    node_comp = node_comp.move_up(alpha)
                else:
                    node_comp = node_comp.move_down(alpha)
    
            self.next_mid = node_comp
            
            self.update_up(alpha)
            self.update_down(alpha)
            
            self.compute_proba(forward, market.rate, model.delta_t, market.volatility, alpha)
            
            if self.Pdown < 0:
                self.Pneg.append(self.Pdown)
            if self.Pmid < 0:
                self.Pneg.append(self.Pmid)
            if self.Pup < 0:
                self.Pneg.append(self.Pup)
        
    
    def update_column(self, i:int, alpha:float, market:Market, model:Model, ded:float):
        #On met à jour l'ensemble des noeuds d'une colonne en partant de la branche du milieu et
        #en parcourant chacun des noeuds grâce à leurs liaisons vers le haut ou le bas avec leurs voisins puis
        #en appliquant la méthode build afin de créer leurs noeuds fils. En outre, on détermine en début de fonction si on constate un dividende
        #à la période des noeuds fils.
        
        tokken = (i * model.delta_t < ded <= (i+1) * model.delta_t)
        next_mid = Node(self.forward(alpha, market, model, tokken))
        self.build(next_mid, alpha, market, model, tokken)
        node_up = self.neighbour_up
        node_down = self.neighbour_down
        
        while node_up is not None and node_down is not None:
            
            if node_up is not None:
                if node_up.Ptot > model.threshold:
                    node_up.build(node_up.neighbour_down.next_up, alpha, market, model, tokken)
                node_up = node_up.neighbour_up
                
            if node_down is not None:
                if node_down.Ptot > model.threshold:
                    node_down.build(node_down.neighbour_up.next_down, alpha, market, model, tokken)
                node_down = node_down.neighbour_down
                
    
    def update_node(self, alpha:float, market:Market, model:Model) :
        #Cette fonction parcoure un arbre en créant à chaque étape une colonne de noeuds à 
        #partir d'une autre antérieure à l'aide de la fonction update_column. Afin de créer le nombre de
        #colonnes correspondant au nombre de pas qu'on veut effectuer dans le temps jusqu'à notre maturité, 
        #on crée un incrément (i) qui est mis à jour après chaque nouvelle colonne créée. Cet incrément
        #permet également de stopper la construction de l'arbre.
        
        i = 0
        node_current = self
        ded = (market.date_ex_div - model.pricing_date).days/model.scale
        while i < model.nb_steps :
            node_current.update_column(i, alpha, market, model, ded)
            node_current = node_current.next_mid
            i += 1
    
    
    def update_price(self, option:Option, rate:float, delta_t:float) -> float :
        #Calcule le prix de l'option au niveau du noeud visité et selon le type 
        #d'option (Call ou Put et Européenne ou Américaine). Le calcul est fait récursivement
        #mais en ne parcourant qu'une fois chaque noeud - ce qui est déterminé par l'attribut 
        #"price" du noeud.
        
        if self.next_mid == None :
                
            self.price = option.payoff(self.spot)        
        
        elif self.price is None :
            
            payoff_mid = self.next_mid.update_price(option, rate, delta_t)
            payoff_down = self.next_down.update_price(option, rate, delta_t)
            payoff_up = self.next_up.update_price(option, rate, delta_t)
            
            Pdown = self.Pdown
            Pup = self.Pup
            Pmid = self.Pmid
            
            self.price = (Pmid*payoff_mid + Pup*payoff_up + Pdown*payoff_down) * mp.exp(- rate * delta_t)
            
            if option.Category == "American" :
                
                self.price = max(self.price, option.payoff(self.spot))
                
        return self.price


# =============================================================================================
# Tree Class
# Constructs and manages the options tree using the aforementioned classes and methods. 
# It connects the market, options, model, and nodes to form a complete structure.
# =============================================================================================


class Tree :
    
    def __init__(self, node, option, model, market):
        self.alpha = mp.exp(market.volatility * mp.sqrt(3 * model.delta_t))
        self.node = node
        self.option = option
        self.model = model
        self.market = market
    
    
    @staticmethod
    def make(param:Parameters) :
        #Méthode statique qui initialise un arbre à partir d'un dictionnaire de paramètres de la
        #classe Parameters.
        
        option = Option(param.Type, param.Category, param.maturity, param.strike)
        market = Market(param.volatility, param.rate, param.spot, param.dividend, param.date_ex_div)
        model = Model(param.pricing_date, param.nb_steps, param.maturity, param.scale, param.threshold)
        
        node = Node(market.spot)
        node.Ptot = 1
        tree = Tree(node, option, model, market)
        
        return tree
    

    def search_neg(self) -> list:
        #Cherche la liste des probabilités négatives présentes dans l'arbre par appel de la méthode
        #search_neg définie pour la classe Node.
        L = []
        return Node.search_neg(self.node, self.model.delta_t, L)
    
    
######################################### Méthode d'update ##############################################
    
    
    def update(self):
        #Crée l'ensemble de l'arborescence à partir du noeud racine de l'arbre puis calcule le prix de
        #l'option représentée.
        self.node.update_node(self.alpha, self.market, self.model)
        self.option.price = self.node.update_price(self.option, self.market.rate, self.model.delta_t)
    
    
if __name__ == '__main__' :
    
    pricing_date = datetime.date(year = 2023 , month = 9, day = 1)
    date_ex_div = datetime.date(year = 2024 , month = 3, day = 1)
    maturity = datetime.date(year = 2024, month = 7, day = 1)
    date_parameters = [pricing_date, date_ex_div, maturity]
    parameter = ["Call", "European", 200, 101, 101, 0.25, 0.02, 3, 365]
    threshold = 0 
    
    param = Parameters(date_parameters, parameter, True, threshold)
    tree = Tree.make(param)
    t0 = time.time()
    tree.update()
    tfin = time.time()
    
    duration = tfin - t0
    price = tree.option.price
    breadth = tree.node.breadth()
    
    print("price : ", price)
    print("duration : ", duration)
    print("breadth : ", breadth)