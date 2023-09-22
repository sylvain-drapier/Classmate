# -*- coding: utf-8 -*-
"""
    Rigidités d'un pli DANS et HORS de ses axes d'orthotropie à partir des propriétés de ses constituants
    - vérifications des relations analytiques du polycopié

1/ propriétés du pli à partir des proprétés des constituants
2/ rigidité d'un pli orthotrope DANS de ses directions principales
3/ rigidité d'un pli orthotrope HORS de ses directions principales

"""

from sympy import *
import numpy as np

''' Contraintes, déformations, lois de comportement en notations de Voigt'''
# tenseur de contraintes
sigma11, sigma12, sigma13, sigma23, sigma22, sigma33 = symbols('sigma11, sigma12, sigma13, sigma23, sigma22, sigma33')
sigma = Array([[sigma11, sigma12, sigma13], 
              [sigma12, sigma22, sigma23] ,
              [sigma13, sigma23, sigma33] ])

# tenseur des déformations
epsilon11, epsilon12, epsilon13, epsilon23, epsilon22, epsilon33 = symbols('epsilon11, epsilon12, epsilon13, epsilon23, epsilon22, epsilon33')
epsilon = Array([[epsilon11, epsilon12, epsilon13], 
              [epsilon12, epsilon22, epsilon23] ,
              [epsilon13, epsilon23, epsilon33] ])

# notations de Voigt
sig_V = Array([sigma11,sigma22,sigma33,sigma23,sigma13,sigma12])
eps_V = Array([epsilon11,epsilon22,epsilon33,epsilon23,epsilon13,epsilon12])


rot = lambdify('alpha', Matrix([[cos('alpha'),sin('alpha'),0],
                               [-sin('alpha'),cos('alpha'),0],
                               [0,0,1]]),np)

#%%
''' 
   1/ Détermination des propriétés du pli à partir des proprétés des constituants
        
'''

''' Caractéristiques au sens de l'ingénieur '''
Vf, Em, num, Ef, nuf, Gflt, EL, ET, GLT, GTTp, nuLT, nuTTp, KL = symbols('Vf, Em, num, Ef, nuLT, Gflt, EL, ET, GLT, GTTp, nuLT, nuTTp, KL')
theta = symbols('theta')

Gm,Gf, kf,km, Kf, Km = symbols('Gm,Gf, kf,km, Kf, Km')
Gm = Em/(2*(1+num))
Gf = Ef/(2*(1+nuf))
kf = Ef/(3*(1-2*nuf))
km = Em/(3*(1-2*num))
Km = km + Gm/3
Kf = kf + Gf/3

mat = {}
KL = mat["KL"] = Km+Vf/(1/(kf-km+(Gf-Gm)/3)+(1-Vf)/(km+4*Gm/3))
EL = mat["EL"] =Vf*Ef+(1-Vf)*Em
nuLT = mat["nuLT"] =Vf*nuf+(1-Vf)*num
GTTp = mat["GTTp"] =Gm*((1+Vf/(Gm/(Gf-Gm)+(km+7*Gm/3)/(2*km+8*Gm/3)*(1-Vf))))
ET = mat["ET"] =2/(1/(2*KL)+1/(2*GTTp)+2*(nuLT**2/EL))
# GLT = 1/2*1/(2/ET-1/(2*KL)-2*(nuLT**2/EL))
GLT = mat["GLT"] =Gm*(Gf*(1+Vf)+Gm*(1-Vf))/(Gf*(1-Vf)+Gm*(1+Vf))
nuTTp = mat["nuTTp"] =ET/(2*GTTp)-1

#%%
''' 
    2/ Détermination des propriétés du pli DANS ses axes d'orthotropie à partir des proprétés
    au sens de l'ingénieur - KL, EL, ...
        
'''

''' Comportement d'un pli orthorope DANS ses axes principaux - si isotrope transverse :
    L_(1,2)3 = L(,2)2
    L_33 = L_22
    L_44 = (L_22-L_66)/2
    L_55 = L_66
'''

''' Caractéristiques au sens de l'ingénieur '''
Vf, Em, num, Ef, nuf, Gflt, EL, ET, GLT, GTTp, nuLT, nuTTp, KL = symbols('Vf, Em, num, Ef, nuLT, Gflt, EL, ET, GLT, GTTp, nuLT, nuTTp, KL')

L11, L12, L13, L23, L22, L33, L44, L55, L66 = symbols('L11, L12, L13, L23, L22, L33, L44, L55, L66')
M11, M12, M13, M23, M22, M33, M44, M55, M66 = symbols('M11, M12, M13, M23, M22, M33, M44, M55, M66')

L11 = EL+4*nuLT**2*KL
L12 = 2*KL*nuLT
L22 = GTTp+KL
L23 = -GTTp+KL
L55 = GLT
# cas isotrope transverse
L13 = L12
L33 = L22
L66 = L55
L44 = (L22-L23)/2

L = Array([[L11,L12,L13,0,0,0],
           [L12,L22,L23,0,0,0],
           [L13,L23,L33,0,0,0],
           [0,0,0,L44,0,0],
           [0,0,0,0,L55,0],
           [0,0,0,0,0,L66]] )


M11 = 1/EL
M12 = -nuTTp/EL
M22 = 1/ET
M23 = -nuTTp/ET
M55 = 1/GLT
# cas isotrope transverse
M13 = M12
M33 = M22
M44 = (M22-M23)/2
M66 = M55 

M = Array([[M11,M12,M13,0,0,0],
           [M12,M22,M23,0,0,0],
           [M13,M23,M33,0,0,0],
           [0,0,0,M44,0,0],
           [0,0,0,0,M55,0],
           [0,0,0,0,0,M66]] )


#%% Comportement d'un pli orthotrope - cf section 3.2.2 poly Composites


''' 3/ Calculs symboliques - vérification des expressions littérales

    rotations obtenues directement avec Sympy : rot_axis3(Symbol('theta')) - autour de l'axe 3
    
    Par rapport au référentiel de Berthelot (Figure 4.2), la rotation est négative pour aller du repère principal R vers le repère de structure R''
    J'aurais plutôt tendance à définir un angle positif beta=pi/2-theta, ce qui revient à aller de l'axe 1 vers l'axe 2' sur la figure 4.2
    Je garde l'angle de theta de Berthelot pour ne pas modifier toutes les relations du polycopié
    
    structures = Array est une abbréviation de ImmutableDenseNDimArray - conversion possible toto = Array.zeros(3,3,3).as_mutable()
    1/ par défaut : Array ImmutableDenseNDimArray toto = Array.zeros(6,6) ou toto = Array([[x],[y],[z]]),
                    on peut forcer toto = MutableDenseNDimArray.zeros(6,6)
    2/ par défaut : array MutableDenseMatrix ou MutableDenseNDimArray, toto = zeros(6,6)    
'''
# vect = Array([[x],[y],[z]])
# vect_1 = ones(3,1)
# Essai : factoriser par rapport aux composantes de sig_V pour exprimer chaque ligne de T_sig
# on récupère un dictionnaire avec les coefficients de chaque facteur 
# d = collect(sigma_p[0,0],sig_V,evaluate=False)
# d[sig_V[i]]; problème d'initialisation de la structure Array par cette méthode


sigma_p = trigsimp(rot_axis3(theta)*sigma.tomatrix()*rot_axis3(theta).transpose()) 
eps_p = rot_axis3(theta)*epsilon.tomatrix()*rot_axis3(theta).transpose()

L11, L12, L13, L23, L22, L33, L44, L55, L66 = symbols('L11, L12, L13, L23, L22, L33, L44, L55, L66')
M11, M12, M13, M23, M22, M33, M44, M55, M66 = symbols('M11, M12, M13, M23, M22, M33, M44, M55, M66')

L = Array([[L11,L12,L13,0,0,0],
           [L12,L22,L23,0,0,0],
           [L13,L23,L33,0,0,0],
           [0,0,0,L44,0,0],
           [0,0,0,0,L55,0],
           [0,0,0,0,0,L66]] )

M = Array([[M11,M12,M13,0,0,0],
           [M12,M22,M23,0,0,0],
           [M13,M23,M33,0,0,0],
           [0,0,0,M44,0,0],
           [0,0,0,0,M55,0],
           [0,0,0,0,0,M66]] )

T_sig = zeros(6,6)
T_sig[0,0]=cos(theta)**2
T_sig[0,1]=sin(theta)**2
T_sig[0,5]=sin(2*theta)
T_sig[1,0]=sin(theta)**2
T_sig[1,1]=cos(theta)**2
T_sig[1,5]=-sin(2*theta)
T_sig[2,2]=1.
T_sig[3,3]=cos(theta)
T_sig[3,4]=-sin(theta)
T_sig[4,3]=sin(theta)
T_sig[4,4]=cos(theta)
T_sig[5,0]=-sin(theta)*cos(theta)
T_sig[5,1]=sin(theta)*cos(theta)
T_sig[5,5]=cos(theta)**2-sin(theta)**2


T_eps = zeros(6,6)
T_eps[0,0]=cos(theta)**2
T_eps[0,1]=sin(theta)**2
T_eps[0,5]=sin(theta)*cos(theta)
T_eps[1,0]=sin(theta)**2
T_eps[1,1]=cos(theta)**2
T_eps[1,5]=-sin(theta)*cos(theta)
T_eps[2,2]=1.
T_eps[3,3]=cos(theta)
T_eps[3,4]=-sin(theta)
T_eps[4,3]=sin(theta)
T_eps[4,4]=cos(theta)
T_eps[5,0]=-sin(2*theta)
T_eps[5,1]=sin(2*theta)
T_eps[5,5]=cos(theta)**2-sin(theta)**2

Lp_ana = trigsimp(T_sig.inv()*L.as_mutable()*T_eps)

Mp_ana = trigsimp(T_eps.inv()*M.as_mutable()*T_sig)


# %%
'''
    Autres calculs - pas abouti
    Comportement d'un pli orthotrope en dehors de ses axes principaux
    
    Utilisation de Numpy - pas de forme explicite en sortie

'''
Lp11, Lp12, Lp13, Lp23, Lp22, Lp33, Lp44, Lp55, Lp66, Lp45, Lp16, Lp26, Lp36 = symbols('Lp11, Lp12, Lp13, Lp23, Lp22, Lp33, Lp44, Lp55, Lp66, Lp45, Lp16, Lp26, Lp36')
Mp11, Mp12, Mp13, Mp23, Mp22, Mp33, Mp44, Mp55, Mp66, Mp45, Mp16, Mp26, Mp36 = symbols('Mp11, Mp12, Mp13, Mp23, Mp22, Mp33, Mp44, Mp55, Mp66, Mp45, Mp16, Mp26, Mp36')
theta = symbols('theta')


Lp = Array([[Lp11,Lp12,Lp13,0,0,Lp16],
           [Lp12,Lp22,Lp23,0,0,Lp26],
           [Lp13,Lp23,Lp33,0,0,Lp36],
           [0,0,0,Lp44,Lp45,0],
           [0,0,0,Lp45,Lp55,0],
           [Lp16,Lp26,Lp36,0,0,Lp66]] )

Mp = Array([[Mp11,Mp12,Mp13,0,0,Mp16],
           [Mp12,Mp22,Mp23,0,0,Mp26],
           [Mp13,Mp23,Mp33,0,0,Mp36],
           [0,0,0,Mp44,Mp45,0],
           [0,0,0,Mp45,Mp55,0],
           [Mp16,Mp26,Mp36,0,0,Mp66]] )


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





