#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 17:03:12 2023

@author: drapier
"""

"""
        Calculs des propriétés au sens de l'ingénieur à l'échelle du pli
        
        Essais de POO vs dictionnaires 
"""


# %% Plis vesion POO

'''
    1.1/ Calcul des rigidités au sens de l'ingénieur à partir des propriétés de ses constituants

'''

# Version POO
class Data:
    # def __init__(self, Vf=0., Em=0., num=0., Ef=0., nuf=0., Gflt=0., ep=0.):
    def __init__(self, Vf, Em, num, Ef, nuf, Gflt, ep):        
        self.Vf = Vf
        self.Em = Em
        self.num = num
        self.Ef = Ef
        self.nuf = nuf
        self.Gflt = Gflt
        self.ep = ep

    def __str__(self):
        return f"Vf={self.Vf}, Em={self.Em}, num={self.num}, Ef={self.Ef}, nuf={self.nuf}, Gflt={self.Gflt}, ep={self.ep}"

class Rigidite_Inge:
    # def __init__(self, Vf=0., Em=0., num=0., Ef=0., nuf=0., Gflt=0., ep=0., EL=0., ET=0., nuLT=0., GTTp=0., KL=0.):
    def __init__(self, Vf, Em, num, Ef, nuf, Gflt, ep, EL=0., ET=0., nuLT=0., GTTp=0., KL=0.):
        self.data = Data(Vf, Em, num, Ef, nuf, Gflt, ep)
        Gm = self.data.Em / (2 * (1 + self.data.num))
        Gf = self.data.Ef / (2 * (1 + self.data.nuf))
        kf = self.data.Ef / (3 * (1 - 2 * self.data.nuf))
        km = self.data.Em / (3 * (1 - 2 * self.data.num))
        Km = km + Gm / 3.
  
        self.KL = Km + self.data.Vf / (1 / (kf - km + (Gf - Gm) / 3) + (1 - self.data.Vf) / (km + 4 * Gm / 3))
        self.EL = self.data.Vf * self.data.Ef + (1. - self.data.Vf) * self.data.Em
        self.nuLT = self.data.Vf * self.data.nuf + (1 - self.data.Vf) * self.data.num
        self.ET = 1 / (1 / self.data.Ef + 1 / self.data.Em)
        self.GTTp = 1 / (2 * (1 / self.ET - 1 / (2 * self.KL) - 2 * (self.nuLT**2 / self.EL)))
   
    def __str__(self):
        return (
            f"EL={self.EL}, ET={self.ET}, nuLT={self.nuLT}, GTTp={self.GTTp}, KL={self.KL}, data=[{str(self.data)}]"
        )

# Instances
T300_914 = Data(0.6, 3.5, 0.3, 260., 0.33, 97.7, 125.E-3)

Pli_T300_914 = Rigidite_Inge(
    T300_914.Vf, T300_914.Em, T300_914.num, T300_914.Ef, T300_914.nuf, T300_914.Gflt, T300_914.ep
)

# %% Version POO ET dictionnaires

# proprietes = ('Vf','Em', 'num', 'Ef', 'nuf', 'Gflt') 
# rigidites_ing = ('KL', 'EL', 'nuLT', 'GTTp', 'ET', 'GLT', 'nuTTp')

class Rigidite_Inge:
    def __init__(self, data, rig_inge):
        self.data = data
        self.rig_inge = rig_inge  # Ajout d'une affectation pour self.rig_inge

        Gm = self.data["Em"] / (2 * (1 + self.data["num"]))
        Gf = self.data["Ef"] / (2 * (1 + self.data["nuf"]))
        kf = self.data["Ef"] / (3 * (1 - 2 * self.data["nuf"]))
        km = self.data["Em"] / (3 * (1 - 2 * self.data["num"]))
        Km = km + Gm / 3.

        self.rig_inge["KL"] = Km + self.data["Vf"] / (1 / (kf - km + (Gf - Gm) / 3) + (1 - self.data["Vf"]) / (km + 4 * Gm / 3))
        self.rig_inge["EL"] = self.data["Vf"] * self.data["Ef"] + (1. - self.data["Vf"]) * self.data["Em"]
        self.rig_inge["nuLT"] = self.data["Vf"] * self.data["nuf"] + (1 - self.data["Vf"]) * self.data["num"]
        self.rig_inge["ET"] = 1 / (1 / self.data["Ef"] + 1 / self.data["Em"])
        self.rig_inge["GTTp"] = 1 / (2 * (1 / self.rig_inge["ET"] - 1 / 
                                          (2 * self.rig_inge["KL"]) - 2 * (self.rig_inge["nuLT"] ** 2 / self.rig_inge["EL"])))

        # Ajout des calculs pour mat
        self.rig_inge["GLT"] = Gm * (self.data["Gflt"] * (1 + self.data["Vf"]) + 
                                     Gm * (1 - self.data["Vf"])) / (self.data["Gflt"] * (1 - self.data["Vf"]) + Gm * (1 + self.data["Vf"]))
        self.rig_inge["nuTTp"] = self.rig_inge["ET"] / (2 * self.rig_inge["GTTp"]) - 1

    def __str__(self):
        return (
            f"EL={self.rig_inge['EL']}, ET={self.rig_inge['ET']}, nuLT={self.rig_inge['nuLT']}, GTTp={self.rig_inge['GTTp']}, KL={self.rig_inge['KL']}, data=[{str(self.data)}]"
        )

# Données et rigidités
T300_914 = {
    "Vf": 0.6,
    "Em": 3.5,
    "num": 0.3,
    "Ef": 260.,
    "nuf": 0.33,
    "Gflt": 97.7,
    "ep": 125.E-3
}

rigidites_ing = {
    "KL": 0.0,
    "EL": 0.0,
    "nuLT": 0.0,
    "ET": 0.0,
    "GTTp": 0.0,
    "GLT": 0.0,
    "nuTTp": 0.0
}

# Création de l'instance de Rigidite_Inge
Pli_T300_914 = Rigidite_Inge(T300_914, rigidites_ing)

# Affichage de l'instance
print(Pli_T300_914)


# class Data:
#     # def __init__(self, Vf=0., Em=0., num=0., Ef=0., nuf=0., Gflt=0., ep=0.):
#     def __init__(self, props):        
#         self.Vf = props["Vf"]
#         self.Em = props["Em"]
#         self.num = props["num"]
#         self.Ef = props["Ef"]
#         self.nuf = props["nuf"]
#         self.Gflt = props["Gflt"]
#         self.ep = props["ep"]
        
#     def __str__(self):
#         return f"Vf={self.Vf}, Em={self.Em}, num={self.num}, Ef={self.Ef}, nuf={self.nuf}, Gflt={self.Gflt}, ep={self.ep}"


# T300_914 = Data(0.6, 3.5, 0.3, 260., 0.33, 97.7, 125.E-3)

# Pli_T300_914 = Rigidite_Inge(
#     T300_914.Vf, T300_914.Em, T300_914.num, T300_914.Ef, T300_914.nuf, T300_914.Gflt, T300_914.ep
# )

# %%
# Version dictionnaire
'''
    0/ Structure de données de base : pli=dict{angle,{data},{props},[L],[Lp],ep,hmin}
'''

proprietes = ('Vf','Em', 'num', 'Ef', 'nuf', 'Gflt') 
rigidites_ing = ('KL', 'EL', 'nuLT', 'GTTp', 'ET', 'GLT', 'nuTTp')
data = dict.fromkeys(proprietes,0.0)
props = dict.fromkeys(rigidites_ing,0.0)

pli = {}
pli["angle"] = 0.0
pli["data"] = data
pli["props"] = props
pli["L"] = np.zeros((6,6))
pli["Lcp"] = np.zeros(4)
pli["ep"] = 0.0
pli["hmin"] = 0.0 


'''
    1.1/ Calcul des rigidités du pli au sens de l'ingénieur
       
    Entrée = dictionnaire de propriétés matériaux mat = Vf, Em, num, Ef, nuf, Gflt 
    Sortie = dictionnaire Rigidites_Ingenieur = KL, EL, ...
'''

def Rigidite_Inge(constituants):
    Vf = constituants["Vf"]
    Em = constituants["Em"]
    num = constituants["num"]
    Ef = constituants["Ef"]
    nuf = constituants["nuf"]
    Gflt =constituants["Gflt"]
    
    Gm = Em/(2*(1+num))
    Gf = Ef/(2*(1+nuf))
    kf = Ef/(3*(1-2*nuf))
    km = Em/(3*(1-2*num))
    Km = km + Gm/3
    
    mat = {}
    KL = mat["KL"] = Km+Vf/(1/(kf-km+(Gf-Gm)/3)+(1-Vf)/(km+4*Gm/3))
    EL = mat["EL"] = Vf*Ef+(1-Vf)*Em
    nuLT = mat["nuLT"] =Vf*nuf+(1-Vf)*num
    GTTp = mat["GTTp"] =Gm*((1+Vf/(Gm/(Gf-Gm)+(km+7*Gm/3)/(2*km+8*Gm/3)*(1-Vf))))
    ET = mat["ET"] =2/(1/(2*KL)+1/(2*GTTp)+2*(nuLT**2/EL))
    # autre possibilité GLT = 1/2*1/(2/ET-1/(2*KL)-2*(nuLT**2/EL))
    mat["GLT"] =Gm*(Gflt*(1+Vf)+Gm*(1-Vf))/(Gflt*(1-Vf)+Gm*(1+Vf))
    mat["nuTTp"] =ET/(2*GTTp)-1
    
    return mat

T300_914_dict = data.copy()
T300_914_dict["Vf"] = 0.6
T300_914_dict["Em"] = 3.5
T300_914_dict["num"] = 0.3
T300_914_dict["Ef"] = 260.
T300_914_dict["nuf"] = 0.33
T300_914_dict["Gflt"] = 97.7
T300_914_dict["ep"] = 125.E-3

# %%
pli = {}
pli["angle"] = 0.0
pli["data"] = data
pli["props"] = props
pli["L"] = np.zeros((6,6))
pli["Lcp"] = np.zeros(4)
pli["ep"] = 0.0
pli["hmin"] = 0.0 

class Pli:
    def __init__(self, angle, data, props, L, Lcp, ep, hmin):
        self.angle = angle
        self.data = data
        self.props = props
        self.L = L

    def __str__(self):
        return f"{self.angle} {self.data}, {self.props}, {self.L}"    

#

# %% initialisations par défaut

# Créer un objet à partir d'un dictionnaire
person_dict = {
    'nom': 'Doe',
    'prénom': 'John',
    'âge': 30,
    'ville': 'New York'
}

class Person:
    def __init__(self, nom, prénom, âge, ville):
        self.nom = nom
        self.prénom = prénom
        self.âge = âge
        self.ville = ville

    def __str__(self):
        return f"{self.prénom} {self.nom}, {self.âge} ans, de {self.ville}"

# Créez une instance de la classe Person à partir du dictionnaire
person_instance = Person(**person_dict)


 # Vous pouvez maintenant accéder aux attributs de l'objet comme suit :
print(person_instance.nom)  # Affiche "Doe"
print(person_instance.prénom)  # Affiche "John"
print(person_instance.âge)  # Affiche 30
print(person_instance.ville)  # Affiche "New York"

# Vous pouvez également utiliser la méthode __str__ pour afficher les informations de la personne
print(person_instance)  # Affiche "John Doe, 30 ans, de New York"

class Personne:
    def __init__(self, nom="Doe", prénom="John", âge=30):
        self.nom = nom
        self.prénom = prénom
        self.âge = âge

# Créez une instance de la classe Personne sans spécifier les valeurs
personne_par_défaut = Personne()

# Créez une instance de la classe Personne en spécifiant des valeurs
personne_personnalisée = Personne(nom="Smith", âge=25)

print(personne_par_défaut.nom, personne_par_défaut.prénom, personne_par_défaut.âge)  # Affiche "Doe John 30"
print(personne_personnalisée.nom, personne_personnalisée.prénom, personne_personnalisée.âge)  # Affiche "Smith John 25"

# %%
# accesseurs et mutateurs
class MaClasse:
    def __init__(self, attribut1, attribut2):
        self.attribut1 = attribut1
        self.attribut2 = attribut2

    # Méthode d'accès pour attribut1
    def get_attribut1(self):
        return self.attribut1

    # Méthode de mutation pour attribut1
    def set_attribut1(self, nouvelle_valeur):
        self.attribut1 = nouvelle_valeur

    # Méthode d'accès pour attribut2
    def get_attribut2(self):
        return self.attribut2

    # Méthode de mutation pour attribut2
    def set_attribut2(self, nouvelle_valeur):
        self.attribut2 = nouvelle_valeur


# Créez une instance de la classe
objet = MaClasse("valeur1", "valeur2")

# Accédez à la valeur de l'attribut1 en utilisant la méthode d'accès
valeur_attribut1 = objet.get_attribut1()
print(valeur_attribut1)  # Affiche "valeur1"

# Modifiez la valeur de l'attribut1 en utilisant la méthode de mutation
objet.set_attribut1("nouvelle_valeur")
nouvelle_valeur_attribut1 = objet.get_attribut1()
print(nouvelle_valeur_attribut1)  # Affiche "nouvelle_valeur"
