# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 14:03:39 2023

@author: aikan
"""
from neostruct import *

def get_price_from_param(param:Parameters) -> float :
    #Récupère le prix d'une option en construisant un arbre trinomial à partir
    #d'un objet Parameters.
    tree = Tree.make(param)
    tree.update()
    price = tree.option.price
    
    del tree
    return price

def delta(param1:Parameters, param2:Parameters) -> float :
    #Calcule le delta de l'option.
    price1 = get_price_from_param(param1)
    price2 = get_price_from_param(param2)
    
    return (price2-price1)/(param2.spot - param1.spot)
    
def gamma(param1:Parameters, param2:Parameters, param3:Parameters) -> float :
    #Calcule le gamma de l'arbre.
    delta1 = delta(param1, param2)
    delta2 = delta(param2, param3)
    
    return (delta2 - delta1) / (param3.spot - param2.spot)
    
def vega(param1:Parameters, param2:Parameters) -> float :
    #Calcule le vega de l'arbre.
    price1 = get_price_from_param(param1)
    price2 = get_price_from_param(param2)
    
    return (price2-price1)/((param2.volatility - param1.volatility)*100)
