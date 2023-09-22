# -*- coding: utf-8 -*-
"""
S. Drapier, Juin 2022

**************************************************************************************
**  Comportement de poutres et plaques composites - polycopié de cours S. Drapier   **
**************************************************************************************

0/ Structure de données = pli Rigidité d'un pli = =dict{angle,{data},{props},[L],[Lp],hmin,hmax}
1/ Comportement orthotrope DANS puis HORS de ses directions principales à partir des 
propriétés de ses constituants (fibre et matrice et leur arrangement) - Chapitre 3
" rigidite_plis.py" contient Rigidite_Inge(constituants), L(M)mat_Inge(mat_inge), L(M)p_Angle(Rigidite, angle), LCP(L,theta)
2/ Empilements dans sections de poutre rectangulaires symétriques b*h - Chapitre 5


Angle theta de Berthelot pour ne pas modifier toutes les relations du polycopié 
= rotation négative pour aller des axes du pli vers les axes de structure

"""

import numpy as np
from rigidites_plis import * 

# %%
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
pli["L"] = np.zeros((6,6))
pli["Lcp"] = np.zeros(4)
pli["ep"] = 0.0
pli["hmin"] = 0.0 

#%% 
''' 
    2/ Raideurs équivalentes - Assemblages des plis 

    Comportement 3D section de poutre
    
   Jeu de données d'essai : Comportement de plis isotropes transverses de type 
   UD T300/914 et UD Verre E/914   
'''
T300_914 = data.copy()
T300_914["Vf"] = 0.6
T300_914["Em"] = 3.5
T300_914["num"] = 0.3
T300_914["Ef"] = 260.
T300_914["nuf"] = 0.33
T300_914["Gflt"] = 97.7
T300_914["ep"] = 125.E-3

E_914 = data.copy()
E_914["Vf"] = 0.6
E_914["Em"] = 3.5
E_914["num"] = 0.22
E_914["Ef"] = 73.
E_914["nuf"] = 0.3
E_914["Gflt"] = 35.2
E_914["ep"] = 125.E-3

pli1 = dict.copy(pli) #pli=dict{angle,{data},{props},[L],[Lp],hmin,hmax}
pli1["data"] = T300_914
pli1["props"] = Rigidite_Inge(T300_914)
pli1["L"] = Lmat_Inge(pli1["props"])

pli2 = dict.copy(pli)
pli2["data"] = E_914
pli2["props"] = Rigidite_Inge(E_914)
pli2["L"] = Lmat_Inge(pli2["props"])

def Update_pli(pli,angle):
    pli["angle"] = angle
    pli["Lcp"] = LCP(pli["L"],angle*180/np.pi)
    return()


'''
    Rigidité de la section de poutre  - Eq. 5.50 polycopié - :
    Section symétrique dans la largeur en géométrie (b*h) et propriétés 
    => les couplages linéaires en x2 s'annulent : <x2 L'ij>=0 et <x2x3 L'ij>=0

    Parcourir la sequence d'empilement = 
    1/ récupérer les propriétés des plis et les mettre à jour en fonction de l'angle
    2/ intégrer les rigidités sur la section
'''

def Sequence(seq,largeur):
    hm = hM = 0.0
    Rig_Sec = np.zeros((6,6))
    for i in range(len(seq)):
        pli = seq[i][0]
        angle = seq[i][1]
        pli["angle"] = angle
        pli["Lcp"] = LCP(pli["L"],angle*180/np.pi)
        Lp = pli["Lcp"]  
        hM = hm + pli["data"]["ep"]
        # stockage Lcp = Lp11, Lp55, Lp66, Lp16
        Rig_Sec[0,0] += Lp[0]*(hM-hm)           #<Lp11>
        Rig_Sec[0,1] += -Lp[3]*(hM**2-hm**2)/2  #-<x3 Lp16>
        Rig_Sec[0,2] += Lp[0]*(hM**2-hm**2)/2   #<x3 Lp11>        
        Rig_Sec[0,4] += Lp[3]*(hM-hm)           #<Lp16>
        Rig_Sec[1,0] += Lp[3]*(hM**2-hm**2)/2   #<x3 Lp16>       
        Rig_Sec[1,1] += Lp[2]*(hM**3-hm**3)/12  #<x3^2 Lp66>
        Rig_Sec[1,2] += -Lp[3]*(hM**3-hm**3)/12 #<x3^2 Lp16>       
        Rig_Sec[1,4] += -Lp[2]*(hM**2-hm**2)/2  #-<x3 Lp66>
        Rig_Sec[2,0] += Lp[0]*(hM**2-hm**2)/2   #<x3 Lp11>        
        Rig_Sec[2,1] += Lp[3]*(hM**3-hm**3)/12  #<x3^2 Lp16>
        Rig_Sec[2,2] += Lp[0]*(hM**3-hm**3)/12  #<x3^2 Lp11>
        Rig_Sec[2,4] += Lp[3]*(hM**2-hm**2)/2   #<x3 Lp16>        
        Rig_Sec[3,3] += Lp[0]*(hM-hm)*largeur**2/12 #<x2^2 Lp11>        
        Rig_Sec[4,0] += Lp[3]*(hM-hm)           #<Lp16> 
        Rig_Sec[4,1] += -Lp[2]*(hM**2-hm**2)/2  #-<x3 Lp66>        
        Rig_Sec[4,2] += Lp[3]*(hM**2-hm**2)/2   #<x3 Lp16>
        Rig_Sec[4,4] += Lp[2]*(hM-hm)           #<Lp66>        
        Rig_Sec[5,5] += Lp[1]*(hM-hm)           #<Lp55>           
         
    return largeur*Rig_Sec   

''' Séquence d'empilement = propriétés du pli + orientation; depuis l'altitude 0'''
seq = ((pli1,0),(pli1,0),(pli1,0),(pli1,0),(pli1,0),(pli1,0),(pli1,0))

Rigidite_section = Sequence(seq,1.E-1)

#%%

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


seq1 = ((pli1,0),(pli1,0),(pli1,0),(pli1,0),(pli1,0),(pli1,0),(pli1,0))
seq2 = ((pli1,0),(pli1,0),(pli1,90),(pli1,90),(pli1,90),(pli1,0),(pli1,0))

# fig, (ax,ax1) = plt.subplots(1 ,2,figsize=(6.,4.),dpi=250 )
fig, ax = plt.subplots(1 ,1,figsize=(6.,4.),dpi=250 )

affich_seq1 = ax.imshow(Sequence(seq1,1.E-1),cmap=plt.cm.viridis,norm=LogNorm(vmin=0.01, vmax=1))
cbar = fig.colorbar(affich_seq1)
# seq2 = ax1.imshow(Sequence(seq2,1.E-1),cmap=plt.cm.viridis,norm=LogNorm(vmin=0.01, vmax=1))
# cbar = fig.colorbar(seq2)
plt.show()

    

