# -*- coding: utf-8 -*-
"""
S. Drapier, Juin 2022

*****************************************************************************************
**  Comportement orthotrope DANS puis HORS de ses directions principales à partir des  **
** propriétés de ses constituants (fibre et matrice et leur arrangement) - Chapitre 3  **
*****************************************************************************************

1.1/ Rigidité dans les axes principaux à partir des propriétés constituants et leur arrangement
1.2/ Comportement du pli DANS puis HORS de ses axes d'orthotropie
1.3/ Comportements en contraintes planes POUTRES

2./ Calculs complets de changments de base 
3./ représentations polaires des comportements

Angle theta de Berthelot pour ne pas modifier toutes les relations du polycopié 
= rotation négative pour aller des axes du pli vers les axes de structure

"""

import numpy as np

# %%
'''
    1.1/ Calcul des rigidités du pli dans ses axes principaux à partir des propriétés de ses constituants
   
    Comportement ISOTROPE TRANSVERSE 
    
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

#%%
''' 
    1.2/ Comportement du pli DANS puis HORS de ses axes d'orthotropie - expressions vérifées dans "rigidites_polaires_verif_analytic.py" 

    Entrée = dictionnaire matériau - grandeurs ingénieurs
    Sortie = np.array(raideur/souplesse)
'''

L = M = np.zeros((6,6))
mat_inge={}

def Lmat_Inge(mat_inge):
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
    
def Mmat_Inge(mat_inge):
    M11 = 1/mat_inge["EL"]
    M12 = -mat_inge["nuTTp"]/mat_inge["EL"]
    M22 = 1/mat_inge["ET"]
    M23 = -mat_inge["nuTTp"]/mat_inge["ET"]
    M55 = 1/mat_inge["GLT"]
    # cas isotrope transverse
    M13 = M12
    M33 = M22
    M44 = (M22-M23)/2
    M66 = M55 
    
    M = np.array([[M11,M12,M13,0,0,0],
               [M12,M22,M23,0,0,0],
               [M13,M23,M33,0,0,0],
               [0,0,0,M44,0,0],
               [0,0,0,0,M55,0],
               [0,0,0,0,0,M66]] )
    
    return M


# %%
''' 1.3/ Comportements en contraintes planes - sans correction pour les poutres -
    Entrées = np.array(6,6)comportement 3D DANS les axes d'otrhotropie + angle
    Sortie = np.array(4): Lp11, Lp55, Lp66, Lp16
'''
Lcp_temp = np.zeros(4)
def LCP(L,theta):
    Lcp_temp[0] = L[0,0]*np.cos(theta)**4 + L[1,1]*np.sin(theta)**4+ 2*(L[0,1]+2*L[5,5])*np.sin(theta)**2*np.cos(theta)**2 #Lp11
    Lcp_temp[1] = L[3,3]*np.sin(theta)**2 + L[4,4]*np.cos(theta)**2 #Lp55
    Lcp_temp[2] = (L[0,0]+L[1,1]-2*(L[0,1]+L[5,5]))*np.sin(theta)**2*np.cos(theta)**2+L[5,5]*(np.sin(theta)**4+np.cos(theta)**4) #Lp66
    Lcp_temp[3] = (L[0,0]-L[0,1]-2*L[5,5])*np.sin(theta)*np.cos(theta)**3 + (L[0,1]-L[1,1]+2*L[5,5])*np.sin(theta)**3*np.cos(theta) #Lp16  
    
    return Lcp_temp

    
#%%
''' 

    2./ Calculs complets de changement de base pour les rigidités et souplesse 

    Entrées = raideurs et souplesse dans les axes principaux - L et M np.array(6,6)

    Sorties = 
        - raideurs et souplesse pour[0,2*Pi]
        - raideurs en contraintes planes pour L, pour un angle donné

'''
from sympy import *
theta=symbols('theta')
T_sig = lambdify(theta,
                 np.array([[cos(theta)**2,sin(theta)**2,0.,0.,0.,sin(2*theta)],
                 [sin(theta)**2,cos(theta)**2,0.,0.,0.,-sin(2*theta)],
                 [0.,0.,1.,0.,0.,0.],
                 [0.,0.,0.,cos(theta),-sin(theta),0.],
                 [0.,0.,0.,sin(theta),cos(theta),0.],
                 [-sin(theta)*cos(theta),sin(theta)*cos(theta),0.,0.,0.,cos(theta)**2-sin(theta)**2]])
                ,np)

T_eps = lambdify(theta,
                 np.array([[cos(theta)**2,sin(theta)**2,0.,0.,0.,sin(theta)*cos(theta)],
                 [sin(theta)**2,cos(theta)**2,0.,0.,0.,-sin(theta)*cos(theta)],
                 [0.,0.,1.,0.,0.,0.],
                 [0.,0.,0.,cos(theta),-sin(theta),0.],
                 [0.,0.,0.,sin(theta),cos(theta),0.],
                 [-sin(2*theta),sin(2*theta),0.,0.,0.,cos(theta)**2-sin(theta)**2]])
                ,np)

# Appels possibles directement des composantes
# (np.transpose(T_eps(angle[i]))*L*T_sig(angle[i]))[0,0]
 
'''     Applications numériques '''
nb_angle = 100
angle = np.linspace(0 , 2*np.pi , nb_angle)
Lp_num = np.zeros((13,nb_angle))
Mp_num = np.zeros((13,nb_angle))

''' toutes les composantes sur 2*Pi '''
def Lp_Angle(Rigidite, angle):
    for i in range(np.size(angle)):
        temp = np.transpose(T_sig(angle[i]))*Rigidite*T_eps(angle[i])
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
        Lp_num[12,i] = temp[3,5] #Lp36
    return Lp_num   


def Mp_Angle(Souplesse, angle):
    for i in range(np.size(angle)):
        temp = np.transpose(T_eps(angle[i]))*Souplesse*T_sig(angle[i])
        Mp_num[0,i] = temp[0,0] #Mp11
        Mp_num[1,i] = temp[0,1] #Mp12
        Mp_num[2,i] = temp[0,2] #Mp13
        Mp_num[3,i] = temp[1,1] #Mp22
        Mp_num[4,i] = temp[1,2] #Mp23
        Mp_num[5,i] = temp[2,2] #Mp33
        Mp_num[6,i] = temp[3,3] #Mp44
        Mp_num[7,i] = temp[4,4] #Mp55
        Mp_num[8,i] = temp[5,5] #Mp66
        Mp_num[9,i] = temp[3,4] #Mp45
        Mp_num[10,i] = temp[0,5] #Mp16
        Mp_num[11,i] = temp[1,5] #Mp26   
        Mp_num[12,i] = temp[3,5] #Mp36
    return Mp_num   


#%%

# ''' 
# 3./ Tracés polaires et cartésiens des rigidités du pli 
# ''' 

import matplotlib.pyplot as plt

fig, ax = plt.subplots(1 ,1,figsize=(4.,4.),dpi=250, subplot_kw={'projection': 'polar'})

nb_angle = 100
angle = np.linspace(0 , 2*np.pi , nb_angle)

xT=plt.xticks()[0]
xL=['0',r'$\frac{\pi}{4}$',r'$\frac{\pi}{2}$',r'$\frac{3\pi}{4}$',\
    r'$\pi$',r'$\frac{5\pi}{4}$',r'$\frac{3\pi}{2}$',r'$\frac{7\pi}{4}$']
plt.xticks(xT, xL)
# ax1.set_xticks(xT, xL)


''' Tracés polaires '''
ax.plot(angle, Lp_Angle(L,angle)[0], "r" , label= "$L_{11}/E_L$")
ax.plot(angle, Lp_Angle(L,angle)[1], "g" , label= "$L_{12}/E_T$")
# ax.plot(angle, Lp_angle(angle)[2]/ET, "c" , label= "$L_{13}/E_T$")
# ax.plot(angle, Lp_angle(L,angle)[3]/ET, "b" , label= "$L_{22}/E_T$")

ax.legend()
# ax1.legend()

# ''' Tracés en cartésien '''

# fig, ax1 = plt.subplots(1 ,1,figsize=(6.,4.),dpi=250 )

# angle = np.linspace(0 , np.pi/2 , nb_angle)

# ax1.plot(angle, Lp_Angle(L,angle)[0], "r" , label= "$L_{11}/E_L$")
# ax1.plot(angle, Lp_Angle(L,angle)[1], "g" , label= "$L_{12}/E_T$")
# # ax.plot(angle, Lp_angle(angle)[2], "c" , label= "$L_{13}/E_T$")
# ax1.plot(angle, Lp_Angle(L,angle)[3], "b" , label= "$L_{22}/E_T$")

# ax1.legend()

