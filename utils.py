# -*- coding: utf-8 -*-
"""
Created on Sat Dec 30 16:37:47 2023

@author: lbonn

Classe  qui :
    1) Gère le type de théorie par des variables d'instance
    2) Fournit les fonctions pour la sauvegarde
    3) Importe tous les modules nécessaire à toutes les classes
    
"""
import json
import numpy as np
import math as m
import matplotlib.pyplot as plt
# from sklearn.linear_model import LinearRegression
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib import cm
import os
from tkinter import filedialog
from tkinter.messagebox import showerror, showinfo

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

import copy
# import sympy
# from pandas import read_excel

from cmath import polar

# Imports pour tests_manu
import time as time



class Utils:    
    # Type théorie
    plaque = 0 #: Si 0 -> théorie des poutres, si 1 -> théorie des plaques
    def3_induite = 1 #: Si 1 -> déformations relatives à la normale 3 prises en compte
    
    # Type de simplification
    pagano = 1 # On utilise la simplification de Pagano pour accélerer les calculs
    polaire = 0 # On utilise la méthode polaire pour accélerer les calculs
    
    # Type de matériau
    # ame = 0 #: Si 0 -> matériau composite orthotrope, si 1 -> âme isotrope
    
    # Seuils
    seuil = 10**(-8) #: Les coefficients sous cette valeur cont considérés comme nuls
    offset_eps = 10**(-12) #: Seuils pour lesquels les déformations sont considérées nuls lorsque ces valeurs sont en dessous des seuils respectifs.
    offset_sig = 10**(-10) #: Seuils pour lesquels les contraintes sont considérées nuls lorsque ces valeurs sont en dessous des seuils respectifs.
    
    obj_to_save = dict({'vals_max' : dict({}),'props_mat' : dict({}),'rupture' : dict({}),'L_section' : dict({})}) #: Dictionnaire qui sauvegarde les résultats des exécutions successives tant que stockage_final n'est pas appelé
    nbr_obj = dict({'vals_max' : 0, 'props_mat' : 0, 'rupture' : 0, 'L_section' : 0}) #: Dictionnaire sauvegardant le nombre de fois qu'un certain tye d'objet a été généré lors d'exécutions successives
    
    def stockage(nom, objet_init):
        Utils.nbr_obj[nom] += 1 # Si un objet de cet type existe déjà, 
                                # on lui donne le même nom et on incrémente
                                # l'extension
        nom2 = nom + "_" + str(Utils.nbr_obj[nom])
        Utils.obj_to_save[nom][nom2] = objet_init
        
    def stockage_final():
        def transformateur_de_dict(dictio):
            # Fonction récursive qui permet de convertir des dictionnaires
            # à l'intérieur de dictionnaire dans un format pris en charge par
            # json
            for key in dictio:
                if isinstance(dictio[key], np.ndarray):
                    dictio[key] = dictio[key].tolist()
                elif isinstance(dictio[key], dict):
                    dictio[key] = transformateur_de_dict(dictio[key])
                else:
                    dictio[key] = str(dictio[key])

            return dictio
        
        for key in Utils.obj_to_save:
            for key2 in Utils.obj_to_save[key]:
                objet = copy.deepcopy(Utils.obj_to_save[key][key2])
                chemin = r"Ressources/donnees_json/" + key + "/" + key2 + ".json"
        
                if isinstance(objet, dict):
                    objet = transformateur_de_dict(objet)
                elif isinstance(objet, np.ndarray):
                    objet = objet.tolist()
                    
                with open(chemin, 'w') as f:
                    json.dump(objet, f, indent=4)
                    
    def vider_les_doss():
        # Fonction qui supprime définitivement toutes les données sauvegardées
        for key in ['L_section', 'props_mat','rupture', 'vals_max']:
            directory = r"Ressources/donnees_json/" + key
            # S. Drapier, 03/10/2024 -> simplification : suppression de tous les fichiers
            # for key2 in range(1, len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])+1):
            #     chemin = r"Ressources/donnees_json/" + key + "/" + key + "_" + str(key2) + ".json"
                # os.remove(chemin)
            for f in os.listdir(directory):
                chemin = r"Ressources/donnees_json/" + key + "/" + f
                os.remove(chemin)                
    
    def destockage(chemin_objet):
        # Fonction qui permet à l'objet de reprendre son type initial
        data = open(chemin_objet,'r') 
        objet_destocke = json.load(data)
        return objet_destocke

        