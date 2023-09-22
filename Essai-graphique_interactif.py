#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 16:57:36 2023

@author: drapier
"""
import tkinter as tk

def on_button_click():
    label.config(text="Hello, " + entry.get())

root = tk.Tk()
root.title("Exemple d'interaction graphique")

label = tk.Label(root, text="Entrez votre nom :")
label.pack()

entry = tk.Entry(root)
entry.pack()

button = tk.Button(root, text="Valider", command=on_button_click)
button.pack()

root.mainloop()
