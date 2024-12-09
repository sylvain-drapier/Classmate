# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 17:44:15 2023

@author: L. Bonneau
Ce module comporte trois classes permettant de calculer les propriétés de composites au niveau de matériau, du pli et de l'empilement.

Si problème de bibilothèque exécuter la commande suivante en ne gardant que les modules nécessaires:
pip install Pillow numpy sympy matplotlib pandas


.. attribute:: Mat_map : np.array((6,36))

    Tableau faisant la correspondance entre les cases de l'interface et leurs informations correspondantes. Les cases sont numérotées de 1 à 36 et la numérotation va de gauche à droite de haut en bas. Une ligne correspond à un type d'information
    
    :1ère ligne: l'indice correspond au numéro de la checkbox et la valeur à l'indice de la matrice de rigidité
    :2eme ligne: l'indice correspond au numéro de la checkbox et la valeur au nom du coefficient pour un pli
    :3eme ligne: l'indice correspond au numéro de la checkbox et la valeur au nom du coefficient pour un empilement
    :4eme ligne: l'indice correspond au numéro de la checkbox et la valeur à la ligne de la matrice de rigidité de l'empilement
    :5eme ligne: l'indice correspond au numéro de la checkbox et la valeur à la colonne de la matrice de rigidité de l'empilement
    
.. attribute:: Dict_mat : dict

    Dictionnaire contenant les propriétés de certains matériaux (GPa et en mm)
    
    La clé correspond au nom du matériau et la valeur à un dictionnaire contenant les caractéristiques
    

"""
from utils import Utils, np, plt, LogNorm, make_axes_locatable, m , time
# read_excel, m , time
# from sympy import *

global Mat_map, Mat_map_plaque, Dict_mat, chemin_sphinx, plaque
chemin_sphinx = 0

Mat_map = [[0, 1, 2, None, None, 10, None, 3, 4, None, None, 11, None, None, 5, None, None, 12, None, None, None, 6, 9, None, None, None, None, None, 7, None, None, None, None, None, None, 8],
 ["L'11", "L'12", "L'13", 0, 0, "L'16", None, "L'22", "L'23", 0, 0, "L'26", None, None, "L'33", 0, 0, "L'36", None, None, None, "L'44", "L'45", 0, None, None, None, None, "L'55", 0, None, None, None, None, None, "L'66"],
 ["<L'11>", "-<x3L'16>", "<x3L'11>", 0, "<L'16>", 0, None, "<x3²L'66>", "-<x3²L'16>" ,0, "-<x3L'66>", 0, None, None, "<x3²L'11>", 0, "<x3L'16>", 0, None, None, None, "<x2²L'11>", 0, 0, None, None, None, None, "<L'66>", 0, None, None, None, None, None, "<L'55>"],
 [0] * 6 + [1] * 6 + [2] * 6 + [3] * 6 + [4] * 6 + [5] * 6, 
 [i % 6 for i in range(6*6)],
 [0, 1, 2, 3, 4, None, None, 7, 8, 9, 10, 11, None, None, 14, 15, 16, None, None, None, None, 21, 22, None, None, None, None, None, 28, None, None, None, None, None, None, 35]]
# 1ere ligne : l'indice correspond au numéro de la checkbox et la valeur à l'indice de la matrice de rigidité
# 2eme ligne : l'indice correspond au numéro de la checkbox et la valeur au nom du coefficient pour un pli
# 3eme ligne : l'indice correspond au numéro de la checkbox et la valeur au nom du coefficient pour un empilement
# 4eme ligne : l'indice correspond au numéro de la checkbox et la valeur à la ligne de la matrice de rigidité de l'empilement
# 5eme ligne : l'indice correspond au numéro de la checkbox et la valeur à la colonne de la matrice de rigidité de l'empilement

Mat_map_plaque = [[0, 1, 2, None, None, 10, None, 3, 4, None, None, 11, None, None, 5, None, None, 12, None, None, None, 6, 9, None, None, None, None, None, 7, None, None, None, None, None, None, 8] + [None]*28,
           ["L'11", "L'12", "L'13", 0, 0, "L'16", None, "L'22", "L'23", 0, 0, "L'26", None, None, "L'33", 0, 0, "L'36", None, None, None, "L'44", "L'45", 0, None, None, None, None, "L'55", 0, None, None, None, None, None, "L'66"] + [None]*28,
           ["A11", "A12", "A16", "B11", "B12", "B16", 0, 0, None, "A22", "A26", None, "B22", "B26", 0, 0, None, None, "A36", None, None, "B36", 0, 0, None, None, None, "D11", "D12", "D16", 0, 0, None, None, None, None, "D22", "D26", 0, 0, None, None, None, None, None, "D36", 0, 0] + [None]*6 + ["F44", "F45"] + [None]*6 + [None, "F55"],  
           [0] * 8 + [1] * 8 + [2] * 8 + [3] * 8 + [4] * 8 + [5] * 8 + [6] * 8 + [7] * 8,
           [i % 8 for i in range(8*8)],
           [i for i in range(6)] + [None]*2 + [i for i in range(8,14)] + [None]*2 + [i for i in range(16,22)] + [None]*2 + [i for i in range(24,30)] + [None]*2 + [i for i in range(32,38)] + [None]*2 + [i for i in range(40,46)] + [None]*8 + [i for i in range(54,56)] + [None]*6 + [i for i in range(62,64)]]

# ----- MPa et mm 
# Voir Table 4.2 et table 4.4 pour les valeurs des résistances à rupture,
Dict_mat = dict({'T300_914': dict({'nom' : 'T300_914', "Vf":0.6, "Em":3.5E+3, "num":0.3, "Ef":230E+3, "nuf":0.33, "Gflt":977E+2, "ms": 242E-6, "rho_r": 1.240E-3, "rho_f": 1.760E-3,
                                   "resistances": dict({"TsaiWu":dict({"F11": 0.45*10**(-6), "F22": 100*10**(-6), "F12": -3.36*10**(-6), "F66": 2.16*10**(-6), "F1": 0, "F2": 20.1*10**(-3)}),
                                                        "cont_Max":dict({"Xt":1380, "Xc":1430, "Yt":40, "Yc":245, "S":70})})}),
                  'E_914': dict({'nom' : 'E_914', "Vf":0.6, "Em":35E+2, "num":0.3, "Ef":44E+2, "nuf":0.22, "Gflt":352E+2, "ms": 418E-6, "rho_r": 1.230E-3, "rho_f": 2.460E-3, # "ms": 242.E-6, "rho_r": 1240.E-6, "rho_f": 1800.E-6,
                                 "resistances": dict({"TsaiWu":dict({"F11": 1.55*10**(-6), "F22": 275*10**(-6), "F12": -10.25*10**(-6), "F66": 195*10**(-6), "F1": 0.7*10**(-3), "F2": 23.8*10**(-3)}),
                                                      "cont_Max":dict({"Xt":1400, "Xc":910, "Yt":35, "Yc":110, "S":70})})}),
                  'âme': dict({'nom' : 'PVC_Divinycell', "E":1.75E+2, "nu":0.32,
                               "resistances": dict({"TsaiWu":dict({"F11": 1.55*10**(-6), "F22": 275*10**(-6), "F12": -10.25*10**(-6), "F66": 195*10**(-6), "F1": 0.7*10**(-3), "F2": 23.8*10**(-3)}),
                                                    "cont_Max":dict({"Xt":4.2, "Xc":2.6, "Yt":4.2, "Yc":2.6, "S":2})})})})

# Fonction pour permettre la génération de documentation sphynx
def chemin_pour_sphinx(chemin):
    global chemin_sphinx
    if chemin_sphinx == 1:
        return r"../" + chemin
    else:
        return chemin



###############################################################################
class Materiau:
    '''
    Classe de données pour les propriétés des matériaux.


    .. attribute:: props : Dict
    
        Dictionnaire contenant les propriétés du matériau

        :nom: Nom du matériau
        :Vf: Fraction volumique des fibres
        :Em: Module d'Young de la matrice
        :num: Coefficient de Poisson de la matrice
        :Ef: Module d'Young de la fibre
        :nuf: Coefficient de Poisson de la fibre
        :Gflt: Module de cisaillement entre les plis
        :ep: Épaisseur du pli
        :ms: Masse surfacique du pli (optionnel)
        :rho_r: Masse volumique de la résine (optionnel)
        :rho_f: Masse volumique de la fibre (optionnel)
        :resistances: Dictionnaire contenant les résistances en fonction du critère
    
    .. attribute:: ep_ref : float
    
        épaisseur des plis par défaut, en mm

    Notes
    -----
        Les paramètres optionnels, si ils sont donnés, doivent tous être donnés à la fois.
    ''' 
    
    # ep_ref = 125.E-3
    
    def __init__(self, props, ep):
        """ Constructeur, prend en entrée un dictionnaire des propriétés du matériau en question

        Parameters
        ----------
        props : Dict
            Dictionnaire contenant les propriétés de certains matériaux (GPa et en mm)
            
            La clé correspond au nom du matériau et la valeur à un dictionnaire contenant les caractéristiques (cf props)
        ep : float
            épaisseur des plis par défaut, en mm. Par défaut pris à 125.E-3 mm.
            Si une épaisseur est saisie, la fraction volumique de fibre est recalculée.
            

        Returns
        -------
        Objet de type matériau

        """
        self.props = dict()
        self.props["nom"] = props["nom"]
        self.props["ep"] = ep
        self.props["resistances"] = props["resistances"]
        if all(k in props for k in ["E", "nu"]): # On a une âme
            self.props["E"] = props["E"]
            self.props["nu"] = props["nu"]
        else:
            self.props["Em"] = props["Em"]
            self.props["num"] = props["num"]
            self.props["Ef"] = props["Ef"]
            self.props["nuf"] = props["nuf"]
            self.props["Gflt"] = props["Gflt"]
            self.props["ms"] = props["ms"]
            self.props["rho_r"] = props["rho_r"]
            self.props["rho_f"] = props["rho_f"]
            self.props["Vf"] = ((props["ms"] / ep) - props["rho_r"]) / (props["rho_f"] - props["rho_r"])
            # print(f'l epaisseur pour Vf = 0.6 : {props["ms"]/(props["rho_f"]*0.6 + (1-0.6)*props["rho_r"])}') # 0.1559278350515464
            # print(f'Vf de {self.props["nom"]} pour : {self.props["Vf"]}')
        Utils.stockage("props_mat", self.props)
    
    def __str__(self):
        return f"Nom={self.props['nom']}, Vf={self.props['Vf']}, Em={self.props['Em']}, num={self.props['num']}, Ef={self.props['Ef']}, nuf={self.props['nuf']}, Gflt={self.props['Gflt']}, ep={self.props['ep']}\n"
    


###############################################################################
class Pli(Materiau):
    """Classe représentant un pli. Possède les méthodes pour calculer les propriétés d'un pli, pour afficher les courbes liées au pli. Possède également des attributs représentants les propriétés d'un pli.    
    
    
    .. inheritance-diagram:: materiau
    
    
    .. attribute:: props_inge : Dict
    
        Dictionnaire contenant les propriétés au sens de l'ingénieur'
        
        :KL: Compressibilité latérale
        :EL: Rigidité longitudinale (sens de la fibre)
        :ET: Rigidité transverse
        :nuLT: Coefficient de Poisson selon l'orientation de la fibre
        :GTTp: Cisaillement transverse
        :nuTTp: Coefficient de Poisson transeverse
    
    .. attribute:: orientation : float
    
        0 Par défaut, Angle theta de Berthelot pour ne pas modifier toutes les relations du polycopié
        = rotation négative pour aller des axes du pli vers les axes de la structure
        
    .. attribute:: L_Inge : np.array((6,6))
    
        Matrice de rigidité au sens de l'ingénieur'
       
    .. attribute:: Lcp_oriente : np.array(4)
    
        Matrice de rigidité pour la poutre orientée par rapport à l'axe principal:
        Lp11, Lp55, Lp66, Lp16
    
    """
    def __init__(self, props, orientation, ep):      
        Materiau.__init__(self, props, ep)
        self.props_inge = dict()
        self.orientation = 0
        self.L_Inge = np.zeros((6,6))
        self.Lcp_oriente = np.zeros(4)
        
        # ----- propriétés du homogénéisés du pli
        if all(k in self.props for k in ["E", "nu"]):
            E = props["E"]
            nu = props["nu"]
            self.L_Inge = E*(1-nu)/((1+nu)*(1-2*nu))*np.array([[1, nu/(1-nu), nu/(1-nu), 0, 0, 0],
                                                              [nu/(1-nu), 1, nu/(1-nu), 0, 0, 0],
                                                              [nu/(1-nu), nu/(1-nu), 1, 0, 0, 0],
                                                              [0, 0, 0, (1-2*nu)/(2*(1-nu)), 0, 0],
                                                              [0, 0, 0, 0, (1-2*nu)/(2*(1-nu)), 0],
                                                              [0, 0, 0, 0, 0, (1-2*nu)/(2*(1-nu))]])
        else:
            Vf = props["Vf"]
            Em = props["Em"]
            num = props["num"]
            Ef = props["Ef"]
            nuf = props["nuf"]
            Gflt = props["Gflt"]
            
            Gm = Em/(2*(1+num))
            Gf = Ef/(2*(1+nuf))
            kf = Ef/(3*(1-2*nuf))
            km = Em/(3*(1-2*num))
            Km = km + Gm/3
            
            KL = self.props_inge["KL"] = Km+Vf/(1/(kf-km+(Gf-Gm)/3)+(1-Vf)/(km+4*Gm/3))
            EL = self.props_inge["EL"] = Vf*Ef+(1-Vf)*Em
            nuLT = self.props_inge["nuLT"] =Vf*nuf+(1-Vf)*num
            GTTp = self.props_inge["GTTp"] =Gm*((1+Vf/(Gm/(Gf-Gm)+(km+7*Gm/3)/(2*km+8*Gm/3)*(1-Vf))))
            ET = self.props_inge["ET"] =2/(1/(2*KL)+1/(2*GTTp)+2*((nuLT**2)/EL)) # H-S
            # ET = self.props_inge["ET"] = Ef*Em/(Ef*(1-Vf)+Em*Vf)# LDM
            # autre possibilité GLT = 1/2*1/(2/ET-1/(2*KL)-2*(nuLT**2/EL))
            self.props_inge["GLT"] =Gm*(Gflt*(1+Vf)+Gm*(1-Vf))/(Gflt*(1-Vf)+Gm*(1+Vf)) # H-S
            # self.props_inge["GLT"] =1/(Vf/Gflt + (1-Vf)/Gm) # LDM
            # print(self.props_inge["GLT"])
            self.props_inge["nuTTp"] =ET/(2*GTTp)-1
            # ----- orientation
            self.orientation = orientation
            # ----- matrice de rigidité à l'échelle du pli
            self.L_Inge = self.L_Inge_calcul(self.props_inge)
            # ----- Méthode polaire
            if Utils.pagano or Utils.polaire:
                self.liste_gam = self.coef_laminate(self.L_Inge) # D'après Bruynel Optimization of laminated composite structures: problems, solution procedures and applications: [U1, U2, U3, U4, U5]
        
        # ----- Comportements en contraintes planes - sans correction pour les poutres
        self.Lcp_oriente = self.LCP(self.L_Inge, orientation)
        # self.Lcp = self.LCP(self.L_Inge, 0)
        
        
        
    def get_L_Inge(self):
        """
        
        Returns
        -------
        L : np.array((6,6))
            Matrice de rigité du pli homogénéisé.

        """
        return self.L_Inge
        
    def L_Inge_calcul(self, mat_inge):
        """Calcul la matrice de rigidité au sens de l'ingénieur
        

        Parameters
        ----------
        mat_inge : Dict
            Dictionnaire des caractéristiques du matériau au sens de l'ingénieur.
            Calculé par le constructeur et stocké par props_inge

        Returns
        -------
        L : np.array((6,6))
            Matrice de rigité du pli homogénéisé.

        """
        L11 = mat_inge["EL"]+4*mat_inge["nuLT"]**2*mat_inge["KL"]
        L12 = 2*mat_inge["KL"]*mat_inge["nuLT"]
        L22 = mat_inge["GTTp"]+mat_inge["KL"]
        L23 = -mat_inge["GTTp"]+mat_inge["KL"]
        L55 = mat_inge["GLT"]
        # cas isotrope transverse
        L13 = L12
        L33 = L22
        L66 = L55
        L44 = (L22-L23)/2
        
        L = np.array([[L11,L12,L13,0,0,0],
                   [L12,L22,L23,0,0,0],
                   [L13,L23,L33,0,0,0],
                   [0,0,0,L44,0,0],
                   [0,0,0,0,L55,0],
                   [0,0,0,0,0,L66]] )
        return L
    
    def coef_laminate(self, L_inge):
        # On prend en compte la déformation induite
        L11, L12, L13, L22, L23, L33, L44, L55, L66 = L_inge[0,0], L_inge[0,1], L_inge[0,2], L_inge[1,1], L_inge[1,2], L_inge[2,2], L_inge[3,3], L_inge[4,4], L_inge[5,5]
        L11 -= L13*L13/L33
        if Utils.plaque:
            L12 -= L13*L23/L33
            L22 -= L23*L23/L33
        else:
            L12 = L22 = L26 = L44 = L45 = 0

        '''
        gam0 -> 1, gam1 -> cos(2theta), gam2 -> cos(4theta), gam3 -> sin(2theta), gam4 -> sin(4theta)
        gam -> [Q11, Q22, Q44, Q55, Q66, Q26, Q16, Q12, Q45]
        '''
        U6, U7 = L44/2, L55/2
        if Utils.pagano:
            # D'après Bruynel Optimization of laminated composite structures: problems, solution procedures and applications: [U1, U2, U3, U4, U5]
            U1, U2, U3, U4, U5 = (3*L11 + 3*L22 + 2*L12 + 4*L66)/8, (L11 - L22)/2, (L11 + L22 - 2*L12 - 4*L66)/8, (L11 + L22 + 6*L12 - 4*L66)/8, (L11 + L22 - 2*L12 + 4*L66)/8
            gam0 = np.array([U1,    U1,     U6 + U7,    U6 + U7,    U5,     0,      0,      U4,     0])
            gam1 = np.array([U2,    -U2,    U6 - U7,    U7 - U6,         0,      0,      0,      0,      0])
            gam2 = np.array([U3,    U3,     0,          0,          -U3,    0,      0,      -U3,    0])
            gam3 = np.array([0,     0,      0,          0,        0,      U2/2,   U2/2,   0,      U7-U6])
            gam4 = np.array([0,     0,     0,           0,           0,      -U3,    U3,     0,    0])

        return [gam0, gam1, gam2, gam3, gam4]
    
    def LCP(self, L, theta):
        '''
        
        Parameters
        ----------
        L : np.array(6,6)
            comportement 3D DANS les axes d'orthotropie
        theta : float
            angle par rapport à l'axe principal

        Returns
        -------
        Lcp_temp : np.array(4)
            Lp11, Lp55, Lp66, Lp16 ou Lp11, Lp55, Lp66, Lp16, Lp12, Lp22, Lp26, Lp44, Lp45.

        '''
        theta = (theta*np.pi) / 180
        
        if all(k in self.props for k in ["E", "nu"]): # Si il s'agit d'une ame, on ne fait pas les calculs de changements d'axe, car le matériau est isotrope
            if Utils.plaque:
                Lcp_temp = np.zeros(9)   
                Lcp_temp[4] = L[0,1] # L12
                Lcp_temp[5] = L[1,1] # L22
                Lcp_temp[6] = L[1,5] # L26
                Lcp_temp[7] = L[3,3] # Lp44
                Lcp_temp[8] = L[3,4] # Lp45
            else:
                Lcp_temp = np.zeros(4)        
                
            Lcp_temp[0] = L[0,0] #Lp11
            Lcp_temp[1] = L[4,4] #Lp55
            Lcp_temp[2] = L[5,5] #Lp66
            Lcp_temp[3] = L[0,5] #Lp16  
            # print(f'Lp11 = {Lcp_temp[0]}, Lp16 = {Lcp_temp[3]}, Lp55 = {Lcp_temp[1]}, Lp66 = {Lcp_temp[2]}')
            
            # Correction contrainte planes
            if Utils.def3_induite == 1:
                Lp13 = L[0,2]
                Lp63 = 0
                Lp33 = L[2,2]
                Lcp_temp[0] -= Lp13*Lp13/Lp33
                Lcp_temp[2] -= Lp63*Lp63/Lp33
                Lcp_temp[3] -= Lp13*Lp63/Lp33
                if Utils.plaque:
                    Lp23 = L[1,2]
                    Lcp_temp[4] -= Lp13*Lp23/Lp33
                    Lcp_temp[5] -= Lp23*Lp23/Lp33
                    Lcp_temp[6] -= Lp23*Lp63/Lp33
        else:
            if Utils.pagano:
                gam0, gam1, gam2, gam3, gam4 = self.liste_gam

                Q = gam0 + gam1*np.cos(2*theta) + gam2*np.cos(4*theta) + gam3*np.sin(2*theta) + gam4*np.sin(4*theta)
                if Utils.plaque:
                    Lcp_temp = np.zeros(9)   
                    Lcp_temp[4] = Q[7] # Lp12
                    Lcp_temp[5] = Q[1] # Lp22
                    Lcp_temp[6] = Q[5] # Lp26
                    Lcp_temp[7] = Q[2] # Lp44
                    Lcp_temp[8] = Q[8] # Lp45
                else:
                    Lcp_temp = np.zeros(4)
                    
                Lcp_temp[0] = Q[0] #Lp11
                Lcp_temp[1] = Q[3] #Lp55
                Lcp_temp[2] = Q[4] #Lp66
                Lcp_temp[3] = Q[6] #Lp16
            else:
                if Utils.plaque:
                    Lcp_temp = np.zeros(9)   
                    Lcp_temp[4] = (L[0,0] + L[1,1] - 4*L[5,5])*(np.sin(theta)**2)*(np.cos(theta)**2) + L[0,1]*(np.cos(theta)**4 + np.sin(theta)**4)# Lp12
                    Lcp_temp[5] = L[0,0]*np.sin(theta)**4 + L[1,1]*np.cos(theta)**4 + 2*(L[0,1] + 2 * L[5,5])*(np.sin(theta)**2)*(np.cos(theta)**2)# Lp22
                    Lcp_temp[6] = (L[0,0] - L[0,1] - 2*L[5,5])*(np.sin(theta)**3)*np.cos(theta) + (L[0,1] - L[1,1] + 2*L[5,5])*(np.cos(theta)**3)*np.sin(theta)# Lp26
                    Lcp_temp[7] = L[3,3]*np.cos(theta)**2 + L[4,4]*np.sin(theta)**2 # Lp44
                    Lcp_temp[8] = (L[4,4]-L[3,3])*np.sin(theta)*np.cos(theta)# Lp45
                else:
                    Lcp_temp = np.zeros(4)        
                    
                Lcp_temp[0] = L[0,0]*np.cos(theta)**4 + L[1,1]*np.sin(theta)**4+ 2*(L[0,1]+2*L[5,5])*np.sin(theta)**2*np.cos(theta)**2 #Lp11
                Lcp_temp[1] = L[3,3]*np.sin(theta)**2 + L[4,4]*np.cos(theta)**2 #Lp55
                Lcp_temp[2] = (L[0,0]+L[1,1]-2*(L[0,1]+L[5,5]))*np.sin(theta)**2*np.cos(theta)**2+L[5,5]*(np.sin(theta)**4+np.cos(theta)**4) #Lp66
                Lcp_temp[3] = (L[0,0]-L[0,1]-2*L[5,5])*np.sin(theta)*(np.cos(theta)**3) + (L[0,1]-L[1,1]+2*L[5,5])*(np.sin(theta)**3)*np.cos(theta) #Lp16  
                
                # Correction contrainte planes
                if Utils.def3_induite == 1:
                    Lp13 = L[0,2]*np.cos(theta)**2 + L[1,2]*np.sin(theta)**2
                    # Lp63 = (L[0,1] - L[1,2])*np.sin(theta)*np.cos(theta)
                    Lp63 = (L[0,2] - L[1,2])*np.sin(2*theta)/2
                    Lp33 = L[2,2]
                    Lcp_temp[0] -= Lp13*Lp13/Lp33
                    Lcp_temp[2] -= Lp63*Lp63/Lp33
                    Lcp_temp[3] -= Lp13*Lp63/Lp33
                    if Utils.plaque:
                        Lp23 = L[0,2] * np.sin(theta)**2 + L[1,2] * np.cos(theta)**2
                        Lcp_temp[4] -= Lp13*Lp23/Lp33
                        Lcp_temp[5] -= Lp23*Lp23/Lp33
                        Lcp_temp[6] -= Lp23*Lp63/Lp33
        return Lcp_temp
    
    def Lp_Angle(self, Rigidite, angle):
        """Matrice de rigidité au sens de l'ingénieur calculé en fonction de l'orientation du repère d'observation par rapport à l'axe principal.
        

        Parameters
        ----------
        Rigidite : np.array((6,6))
            Matrice de rigité du pli homogénéisé.
        angle : liste
            liste d'angle en radian.

        Returns
        -------
            Lp_num : np.array((12,nb_angle))
                Matrice de rigité du pli homogénéisé sous tous les angles.

        """
        theta=symbols('theta')
        T_sig = lambdify(theta,
                         Matrix([[cos(theta)**2,sin(theta)**2,0.,0.,0.,sin(2*theta)],
                         [sin(theta)**2,cos(theta)**2,0.,0.,0.,-sin(2*theta)],
                         [0.,0.,1.,0.,0.,0.],
                         [0.,0.,0.,cos(theta),-sin(theta),0.],
                         [0.,0.,0.,sin(theta),cos(theta),0.],
                         [-sin(theta)*cos(theta),sin(theta)*cos(theta),0.,0.,0.,cos(theta)**2-sin(theta)**2]])
                        ,np)

        T_eps = lambdify(theta,
                         Matrix([[cos(theta)**2,sin(theta)**2,0.,0.,0.,sin(theta)*cos(theta)],
                         [sin(theta)**2,cos(theta)**2,0.,0.,0.,-sin(theta)*cos(theta)],
                         [0.,0.,1.,0.,0.,0.],
                         [0.,0.,0.,cos(theta),-sin(theta),0.],
                         [0.,0.,0.,sin(theta),cos(theta),0.],
                         [-sin(2*theta),sin(2*theta),0.,0.,0.,cos(theta)**2-sin(theta)**2]])
                        ,np)
        Lp_num = np.zeros((13,np.size(angle)))
        for i in range(np.size(angle)):
            tempo = np.dot( T_sig(angle[i]), Rigidite)
            temp = np.dot(tempo, np.linalg.inv(T_eps(angle[i])))
            Lp_num[0,i] = temp[0,0] #Lp11
            Lp_num[1,i] = temp[0,1] #Lp12
            Lp_num[2,i] = temp[0,2] #Lp13
            Lp_num[3,i] = temp[1,1] #Lp22
            Lp_num[4,i] = temp[1,2] #Lp23
            Lp_num[5,i] = temp[2,2] #Lp33
            Lp_num[6,i] = temp[3,3] #Lp44
            Lp_num[7,i] = temp[4,4] #Lp55
            Lp_num[8,i] = temp[5,5] #Lp66
            Lp_num[9,i] = temp[3,4] #Lp45
            Lp_num[10,i] = temp[0,5] #Lp16
            Lp_num[11,i] = temp[1,5] #Lp26   
            Lp_num[12,i] = temp[2,5] # cf 3.44
        return Lp_num   
    
    def figures(self, coef_a_aff, choix_normalisation):
        """Génère les diagrammes polaires et cartésien en fonction des coefficients voulus et de la normalisation
        

        Parameters
        ----------
        coef_a_aff : [int]
            Indices des checkboxs sélectionnées (entre 1 et 36)
            Convertit ensuite en l'indice de la matrice de rigidité (entre 1 et 12) par la focntion Mapping. Voir Mat_map pour le mapping entre le numéro des checkboxs et des coefficients
            
        choix_normalisation : str
            Mode de normalisation 
            # TODO

        Returns
        -------
        fig, ax
            Objets contenant les figures polaires (indicées 1) et cartésiennes (indicées 2)

        """
        def Mapping(i):
            """Retourne l'indice de L_inge correspondant à la checkbox cochée et la légende correspondante
            

            Parameters
            ----------
            i : int
                numéro de la checkbox sélectionnée (entre 1 et 36)

            Returns
            -------
            int
                indice de L_ingé correspondant à la checkbox cochée
            str
                nom du coefficient de la matrice

            """
            return Mat_map[0][i], Mat_map[1][i]
        
        ''' Tracés polaires '''
        fig1, ax1 = plt.subplots(1 ,1,dpi=250, subplot_kw={'projection': 'polar'})
        nb_angle = 100
        angle = np.linspace(0 , 2*np.pi , nb_angle)
        Lp_angle = self.Lp_Angle(self.L_Inge, angle)
        for i in range(len(coef_a_aff)):
            indice, leg = Mapping(coef_a_aff[i])
            if (max(abs(Lp_angle[indice]))) > Utils.seuil:
                ax1.plot(angle, Lp_angle[indice]/max(abs(Lp_angle[indice])), label= f'{leg}/max(|{leg}|)')
            else:
                print(f'\n\nLe coefficient {leg} est supposé nul\nIl vaut au maximum {max(abs(Lp_angle[indice]))}\n')
                # coef_nuls.append(leg)
        ax1.set_title(f"Rigidité du {self.props['nom']}", fontdict={'fontsize': 15}, pad = 15)
        # ax1.legend(loc="upper right", bbox_to_anchor=(1.7, 1.2))
        ax1.legend(loc="lower right", bbox_to_anchor=(1.3,0))
        # plt.show()
        
        ''' Tracés cartésiens '''
        fig2, ax2 = plt.subplots(1 ,1,dpi=250 )
        angle = np.linspace(0 , np.pi/2 , nb_angle)
        Lp_angle = self.Lp_Angle(self.L_Inge, angle)
        for i in range(len(coef_a_aff)):
            indice, leg = Mapping(coef_a_aff[i])
            if max(abs(Lp_angle[indice])) > Utils.seuil:
                ax2.plot(180*angle/np.pi, Lp_angle[indice]/max(abs(Lp_angle[indice])), label= f'{leg}/max(|{leg}|)')
        ax2.set_xlabel('Direction principale du pli par rapport à la direction globale (en degré)')
        ax2.set_title(f"Rigidité du {self.props['nom']}", fontdict={'fontsize': 15}, pad = 15)
        ax2.legend()

        # plt.show()
        
        plt.close(fig1)
        plt.close(fig2)
        return fig1, ax1, fig2, ax2
        
    def Affichage(self, polaire, cartesien, coef_a_aff, choix_normalisation):
        """Enregistre sous forme d'image au format jpeg dans le dossier Ressources les images souhaitées
        

        Parameters
        ----------
        polaire : boolean
            Si True, sauvegarde le diagramme polaire sinon non
        cartesien : boolean
            Si True, sauvegarde le diagramme cartésien sinon non
        coef_a_aff : [int]
            Indices des checkboxs sélectionnées (entre 1 et 36)
            Convertis ensuite en l'indice de la matrice de rigidité (entre 1 et 12) par la focntion Mapping'
        choix_normalisation : str
            Mode de normalisation

        Returns
        -------
        None.

        """
        fig1, ax1, fig2, ax2 = self.figures(coef_a_aff, choix_normalisation)
        if polaire and not cartesien:
            fig1.savefig(r"Ressources/images_gen/figure_polaire.png", bbox_inches="tight")
        elif cartesien and not polaire:
            fig2.savefig(r"Ressources/images_gen/figure_cartesienne.png")
        elif cartesien and polaire:
            # fig1.savefig(r"Ressources/figure_polaire.png", bbox_inches="tight")
            # fig2.savefig(r"Ressources/figure_cartesienne.png")
            fig1.savefig(r"Ressources/images_gen/figure_polaire.jpeg", bbox_inches="tight")
            fig2.savefig(r"Ressources/images_gen/figure_cartesienne.jpeg")
        
        plt.close(fig1)
        plt.close(fig2)
        
    def __str__(self):
        return f"{self.props['nom']}, {self.orientation}°, {self.get_L_Inge()}, {self.Lcp_oriente}\n"
        
        
   
###############################################################################
class Empilement:
    """Classe représentant un empilement. Possède les méthodes pour calculer les propriétés d'un empilement, pour afficher les courbes liés au empilement. Possède également des attributs représentants les propriétés d'un empilement.
    
    
    .. attribute:: L_section : np.array((6,6))
    
        Matrice de rigidité de l'empilement
        
    .. attribute:: largeur : float
    
        largeur de l'empilement en mm
        
    .. attribute:: liste_de_pli : [Pli] ou str
    
        liste de pli (d'objets Pli) ou chemin vers un excel contenant les plis de l'empilement
        
    .. attribute:: angle_pol : [float]
    
        liste des angles pour tracer le diagramme polaire

    .. attribute:: Lp_angle_pol : np.array((nbr d'angle, 6, 6))
                                            
        Matrice de rigidité de l'empilement pour chaque angle
        
    .. attribute:: angle_car : [float]
    
        liste des angles pour tracer le diagramme cartésien

    .. attribute:: Lp_angle_car : np.array((nbr d'angle, 6, 6))
                                            
        Matrice de rigidité de l'empilement pour chaque angle
        
    .. attribute:: L_section : np.array((6, 6))
    
        Matrice de rigidité dans son axe principal
    """
    
    def __init__(self, liste_de_pli, largeur):
        self.L_section = np.zeros((6,6))
        if largeur == None: # On a une plaque
            self.largeur = 0
        else:
            self.largeur = largeur            
        self.masse, self.surface = 0, 100
        if isinstance(liste_de_pli, str) == 1:
            plis = read_excel(liste_de_pli).iloc[:, :3].values
            self.liste_de_pli = [Pli(Dict_mat[row[0]], row[1], ep=row[2]) for row in plis]
        else:
            self.liste_de_pli = liste_de_pli

        self.L_section =  self.seq_Angle(np.array([0]))
        Utils.stockage("L_section", self.L_section)
        # self.Affichage(0)
    
    def change_angle(self, indice_pli, angle):
        self.liste_de_pli[indice_pli].orientation = angle
        self.L_section =  self.seq_Angle(np.array([0]))
    
    def get_ep_emp(self):
        """

        Returns
        -------
        epaisseur_emp : float
            épaisseur totale de l'empilement (h dans le polycopié).

        """
        epaisseur_emp = 0
        for k in range(len(self.liste_de_pli)):
            epaisseur_emp += self.liste_de_pli[k].props['ep']
        return epaisseur_emp 
    
    def seq_Angle(self, angle):
        """Créée une matrice (de dimension 3) contenant la matrice de rigidité de l'empilement pour chaque angle (donné par la première dimension).
        

        Parameters
        ----------
        angle : [float]
            liste des angles du repère d'observation de l'empilement par rapport à son axe principal

        Returns
        -------
        np.array((nbr d'angle, 6, 6))
            matrice (de dimension 3) contenant la matrice de rigidité de l'empilement pour chaque angle

        """
        if Utils.plaque:
            Rig_Sec = np.zeros((np.size(angle), 8,8))
            for k in range(np.size(angle)):
                hm = - self.get_ep_emp() / 2
                for i in range(len(self.liste_de_pli)):
                    Lp11, Lp55, Lp66, Lp16, Lp12, Lp22, Lp26, Lp44, Lp45 = self.liste_de_pli[i].LCP(self.liste_de_pli[i].L_Inge, self.liste_de_pli[i].orientation - (angle[k]*180)/np.pi)
                    hM = hm + self.liste_de_pli[i].props["ep"]
                    self.masse += self.surface * self.liste_de_pli[i].props['ms']
                    Rig_Sec[k,0,0] += Lp11*(hM-hm) # A11
                    Rig_Sec[k,0,1] += Lp12*(hM-hm) # A12
                    Rig_Sec[k,0,2] += Lp16*(hM-hm) # A16 
                    Rig_Sec[k,1,1] += Lp22*(hM-hm) # A22
                    Rig_Sec[k,1,2] += Lp26*(hM-hm) # A26 
                    Rig_Sec[k,2,2] += Lp66*(hM-hm) # A36

                    Rig_Sec[k,0,3] += Lp11*(hM**2-hm**2)/2 # B11
                    Rig_Sec[k,0,4] += Lp12*(hM**2-hm**2)/2 # B12
                    Rig_Sec[k,0,5] += Lp16*(hM**2-hm**2)/2 # B16 
                    Rig_Sec[k,1,4] += Lp22*(hM**2-hm**2)/2 # B22
                    Rig_Sec[k,1,5] += Lp26*(hM**2-hm**2)/2 # B26 
                    Rig_Sec[k,2,5] += Lp66*(hM**2-hm**2)/2 # B36
                    
                    Rig_Sec[k,3,3] += Lp11*(hM**3-hm**3)/3 # D11
                    Rig_Sec[k,3,4] += Lp12*(hM**3-hm**3)/3 # D12
                    Rig_Sec[k,3,5] += Lp16*(hM**3-hm**3)/3 # D16 
                    Rig_Sec[k,4,4] += Lp22*(hM**3-hm**3)/3 # D22
                    Rig_Sec[k,4,5] += Lp26*(hM**3-hm**3)/3 # D26 
                    Rig_Sec[k,5,5] += Lp66*(hM**3-hm**3)/3 # D36
                    
                    Rig_Sec[k,6,6] += Lp44*(hM-hm) # F44
                    Rig_Sec[k,6,7] += Lp45*(hM-hm) # F45
                    Rig_Sec[k,7,7] += Lp55*(hM-hm) # F55 
                    
                    # On symétrise les sous matrices
                    Rig_Sec[k,1,0] = Rig_Sec[k,0,1]
                    Rig_Sec[k,2,0] = Rig_Sec[k,0,2]
                    Rig_Sec[k,2,1] = Rig_Sec[k,1,2] 
                    
                    Rig_Sec[k,1,3] = Rig_Sec[k,0,4]
                    Rig_Sec[k,2,3] = Rig_Sec[k,0,5]
                    Rig_Sec[k,2,4] = Rig_Sec[k,1,5]
                    
                    Rig_Sec[k,4,3] = Rig_Sec[k,3,4]
                    Rig_Sec[k,5,3] = Rig_Sec[k,3,5]
                    Rig_Sec[k,5,4] = Rig_Sec[k,4,5]
                    
                    Rig_Sec[k,7,6] = Rig_Sec[k,6,7]
                    
                    Rig_Sec[k,3:6,0:3] = Rig_Sec[k,0:3,3:6]
                                        
                    hm = hM
            return Rig_Sec
        else:
            Rig_Sec = np.zeros((np.size(angle), 6,6))
            for k in range(np.size(angle)):
                hm = - self.get_ep_emp() / 2
                for i in range(len(self.liste_de_pli)):
                    Lp = self.liste_de_pli[i].LCP(self.liste_de_pli[i].L_Inge, self.liste_de_pli[i].orientation - (angle[k]*180)/np.pi)
                    hM = hm + self.liste_de_pli[i].props["ep"]
                    Rig_Sec[k,0,0] += Lp[0]*(hM-hm)           #<Lp11>
                    Rig_Sec[k,0,1] += -Lp[3]*(hM**2-hm**2)/2  #-<x3 Lp16>
                    Rig_Sec[k,0,2] += Lp[0]*(hM**2-hm**2)/2   #<x3 Lp11>   
                    Rig_Sec[k,0,4] += Lp[3]*(hM-hm)           #<Lp16>
                    Rig_Sec[k,1,0] = Rig_Sec[k,0,1]   #-<x3 Lp16>
                    Rig_Sec[k,1,1] += Lp[2]*(hM**3-hm**3)/3  #<x3^2 Lp66>
                    Rig_Sec[k,1,2] += -Lp[3]*(hM**3-hm**3)/3 #<x3^2 Lp16>       
                    Rig_Sec[k,1,4] += -Lp[2]*(hM**2-hm**2)/2  #-<x3 Lp66>
                    Rig_Sec[k,2,0] = Rig_Sec[k,0,2]   #<x3 Lp11>        
                    Rig_Sec[k,2,1] = -Rig_Sec[k,1,2]  #<x3^2 Lp16>
                    Rig_Sec[k,2,2] += Lp[0]*(hM**3-hm**3)/3  #<x3^2 Lp11>
                    Rig_Sec[k,2,4] += Lp[3]*(hM**2-hm**2)/2   #<x3 Lp16>        
                    Rig_Sec[k,3,3] += Lp[0]*(hM-hm)*self.largeur**2/3 #<x2^2 Lp11> 
                    Rig_Sec[k,4,0] = Rig_Sec[k,0,4]           #<Lp16> 
                    Rig_Sec[k,4,1] = Rig_Sec[k,1,4]  #-<x3 Lp66>        
                    Rig_Sec[k,4,2] = Rig_Sec[k,2,4]   #<x3 Lp16>
                    Rig_Sec[k,4,4] += Lp[2]*(hM-hm)           #<Lp66>        
                    Rig_Sec[k,5,5] += Lp[1]*(hM-hm)           #<Lp55>   
                    hm = hM
            return self.largeur*Rig_Sec
    
    def Affichage(self, angle):
        """Génère une image de la matrice de rigidité dans l'axe incliné à [angle] degrés par rapport à l'axe de la structure.
        Chaque coefficient est remplacé par sa valeur numérique.
        Attention, les valeurs en dessous de 10**(-12) ne sont pas affichées.
        

        Parameters
        ----------
        angle : [float]
            angle en degrés

        Returns
        -------
        None.

        """  
        if angle == 0:
            L_section = self.L_section[0,:,:]
        else:
            L_section = self.seq_Angle(np.array([m.radians(angle)]))[0]
        
        fig, ax = plt.subplots(dpi=250)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="10%", pad=0.05)
        # styles de cmap : viridis, plasma, inferno, magma, coolwarm, bwr, hsv, tab10, tab20, tab20b
        affich_seq = ax.imshow(L_section,cmap=plt.cm.coolwarm)
        cbar = fig.colorbar(affich_seq, cax = cax)
        for i in range(L_section.shape[0]):
            for j in range(L_section.shape[1]):
                if abs(L_section[i, j]) > Utils.seuil:
                    legende = f"{L_section[i, j]:.1e}"
                else:
                    legende = "0"
                text = ax.text(j, i, legende,
                                ha="center", va="center", color="k", fontsize=7)
        ax.set_title(f"Matrice de rigidité [N] et [N.mm]\nsollicitation à {angle}° de l'axe pcp")
        fig.savefig(chemin_pour_sphinx("Ressources/images_gen/figure_section.png"), bbox_inches="tight")
        fig.tight_layout()
        plt.close(fig)
        
    def Dessin_pli(self, mode):
        """Dessine l'empilement à partir de liste_de_pli. Chaque pli est schématisé par un bloc contenant un angle et ayant pour légende le nom du matériau. Sauvegarde les dessins dans Ressources
        

        Parameters
        ----------
        mode : str
           Fonctionnalité retirée
           # TODO
            

        Returns
        -------
        None.

        """
        fig, ax = plt.subplots(dpi=250)
        noms_mat = []
        incli_pli = np.zeros((len(self.liste_de_pli),1))
        for k in range(len(self.liste_de_pli)-1,-1,-1):
            noms_mat += ([self.liste_de_pli[k].props['nom'] + ', ' + str(k+1)])
            #P. Thomas 07/10/24 ajout du +1 dans str(k+1)
            incli_pli[len(self.liste_de_pli)-1-k,0] = self.liste_de_pli[k].orientation
        leg = incli_pli
        titre = "Dessin de l'empilement [°]"
        chemin = r"Ressources/images_gen/dessin_empilement.jpeg"
        affich_seq = ax.imshow(leg,cmap=plt.cm.coolwarm)
        for i in range(leg.shape[0]):
            text = ax.text(0, i, int(leg[i, 0]),
                            ha="center", va="center", color="k", fontsize=7)
    
        ax.set_xticks(np.arange(len([])))
        ax.set_yticks(np.arange(len(noms_mat)), labels=noms_mat)
        ax.set_title(titre)
        fig.savefig(chemin_pour_sphinx(chemin), bbox_inches="tight")
        fig.tight_layout()
        # plt.show()
        plt.close(fig)

    
    def figures(self, coef_a_aff, choix_normalisation):
        """Génère les diagrammes polaires et cartésien en fonction des coefficients voulus et de la normalisation
        

        Parameters
        ----------
        coef_a_aff : [int]
            Indices des checkboxs sélectionnées (entre 1 et 36)
            Convertis ensuite en l'indice de la matrice de rigidité (entre 1 et 12) par la fonction Mapping
            
        choix_normalisation : str
            Mode de normalisation

        Returns
        -------
        fig, ax
            Objets contenant les figures polaires (indicées 1) et cartésiennes (indicées 2)
        """        
        def Mapping(i):
            if Utils.plaque:
                Dict_map = Mat_map_plaque
            else:
                Dict_map = Mat_map
            return Dict_map[2][i], Dict_map[3][i], Dict_map[4][i]
        
        coef_nuls = []
    
        nb_angle = 100
        self.angle_pol = np.linspace(0 , 2*np.pi , nb_angle)
        self.Lp_angle_pol = Lp_angle_pol = self.seq_Angle(self.angle_pol)
        
        index = np.argmin(np.abs(self.angle_pol - np.pi/2))
        self.angle_car = self.angle_pol[0:index+1]
        self.Lp_angle_car = Lp_angle_pol[0:index+1,:,:]
        
        ''' Tracés polaires '''
        fig1, ax1 = plt.subplots(1 ,1,dpi=250, subplot_kw={'projection': 'polar'})
        for i in range(len(coef_a_aff)):
            leg, x, y = Mapping(coef_a_aff[i])
            if max(abs(self.Lp_angle_pol[:,x,y])) > Utils.seuil:
                ax1.plot(self.angle_pol, self.Lp_angle_pol[:,x,y]/max(abs(self.Lp_angle_pol[:,x,y])), label= f'{leg}/max(|{leg}|)')
            else:
                print(f'\n\nLe coefficient {leg} est supposé nul\nIl vaut au maximum {max(abs(self.Lp_angle_pol[:,x,y]))}\n')
                coef_nuls.append(leg)
        ax1.set_title("Rigidité de l'empilement\n(le max est pris en fonction de l'angle)", fontdict={'fontsize': 15}, pad = 15)
        ax1.legend(loc="lower right", bbox_to_anchor=(1.7,-0.1))
        # plt.show()
        
        ''' Tracés cartésiens '''
        fig2, ax2 = plt.subplots(1 ,1,dpi=250 )
        for i in range(len(coef_a_aff)):
            leg, x, y = Mapping(coef_a_aff[i])
            if max(abs(self.Lp_angle_car[:,x,y])) > Utils.seuil:
                ax2.plot(180*self.angle_car/np.pi, self.Lp_angle_car[:,x,y]/max(abs(self.Lp_angle_car[:,x,y])), label= f'{leg}/max(|{leg}|)')
        ax2.set_xlabel('Direction principale du pli par rapport à la direction de la structure [degrés]')
        ax2.set_title("Rigidité de l'empilement", fontdict={'fontsize': 15}, pad = 15)
        ax2.legend()
        
        plt.close(fig1)
        plt.close(fig2)
        return fig1, ax1, fig2, ax2, coef_nuls
        
    def Affichage_pol_cart(self, polaire, cartesien, coef_a_aff, choix_normalisation):
        """Enregistre sous forme d'image au format jpeg dans le dossier Ressources les images souhaitées
        

        Parameters
        ----------
        polaire : boolean
            Si True, sauvegarde le diagramme polaire sinon non
        cartesien : boolean
            Si True, sauvegarde le diagramme cartésien sinon non
        coef_a_aff : [int]
            Indices des checkboxs sélectionnées (entre 1 et 36)
            Convertit ensuite en l'indice de la matrice de rigidité (entre 1 et 12) par la focntion Mapping'
        choix_normalisation : str
            Mode de normalisation

        Returns
        -------
        None.

        """
        fig1, ax1, fig2, ax2, coef_nuls = self.figures(coef_a_aff, choix_normalisation)
        if polaire and not cartesien:
            fig1.savefig(r"Ressources/images_gen/figure_polaire_emp.png", bbox_inches="tight")
        elif cartesien and not polaire:
            fig2.savefig(r"Ressources/images_gen/figure_cartesienne_emp.png")
        elif cartesien and polaire:
            fig1.savefig(chemin_pour_sphinx("Ressources/images_gen/figure_polaire_emp.jpeg"), bbox_inches="tight")
            fig2.savefig(chemin_pour_sphinx(r"Ressources/images_gen/figure_cartesienne_emp.jpeg"))
        return coef_nuls
            
        
    def __str__(self):
        # mess = f'Rigidité section : \n{self.L_section}\n'
        mess = ''
        for k in range(len(self.liste_de_pli)):
            mess += f"pli n°{k+1} : {self.liste_de_pli[k].props['nom']}, {self.liste_de_pli[k].orientation}°\n"
        return mess
    
    
###############################################################################

