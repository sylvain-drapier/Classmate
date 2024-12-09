from Contraintes import *
from Contraintes_plaques import *
from materiau import *
from utils import Utils, m, time, read_excel, np, plt
from CalculResistances import CalculResistances

#  pour moi
from scipy.stats import linregress
# from sklearn.linear_model import LinearRegression
import pandas as pd

from mpl_toolkits.mplot3d import axes3d

# ----- Pour le batch
import pickle



'''
Script de test des classes Contraintes et materiau

0/ Propriétés au sens de l'ingénieur calculées pour tests rigidité
1/ Création de plis
2/ Création de séquences
3/ Test d'importation de fichiers excels
4/ Test du calculateur de contraintes
5/ Verification des critères de résistance
6/ Affichages console
7/ Tests du stockage json
8/ Tests matrice rigidité
'''


# =============================================================================
# Choix théorie
# =============================================================================
Utils.plaque = 1 # 1 -> théorie de plaque, 0 -> théorie de poutre
Utils.pagano = 1 # Pour accélérer les calculs
print(f'Utils.pagano = {Utils.pagano}')


''' 0/ Propriétés calculées pour tests rigidité'''
# L11_T =	161506
# L12_T =	6456.036
# L22_T =	14475.954326
# L23_T =	5826.045674
# L44_T =	4324.954325999999
# L66_T =	5120.372861


# L11_E =	6892.895358
# L12_E =	2208.128872
# L22_E =	6472.474563
# L23_E =	2289.929053
# L66_E =	4714.38291

# c4_neg = np.cos(m.radians(-45))**4
# s4_neg = np.sin(m.radians(-45))**4
# c2_neg = np.cos(m.radians(-45))**2
# s2_neg = np.sin(m.radians(-45))**2
# c4 = np.cos(m.radians(45))**4
# s4 = np.sin(m.radians(45))**4
# c2 = np.cos(m.radians(45))**2
# s2 = np.sin(m.radians(45))**2
# s = np.sin(m.radians(45))
# c = np.cos(m.radians(45))
# s_neg = np.sin(m.radians(-45))
# c_neg = np.cos(m.radians(-45))
# s3 = np.sin(m.radians(45))**3
# c3 = np.cos(m.radians(45))**3
# s3_neg = np.sin(m.radians(-45))**3
# c3_neg = np.cos(m.radians(-45))**3



'''1/ Création de plis'''
### Données matérielles
# # ----- GPa et mm
Dict_mat = dict({'T300_914': dict({'nom' : 'T300_914', "Vf":0.6, "Em":3.5, "num":0.3, "Ef":260, "nuf":0.33, "Gflt":97.7, "ms": 242.E-9, "rho_r": 1240.E-9, "rho_f": 1800.E-9}),
                  'E_914': dict({'nom' : 'E_914', "Vf":0.6, "Em":3.5, "num":0.3, "Ef":73, "nuf":0.22, "Gflt":35.2, "ms": 242.E-9, "rho_r": 1240.E-9, "rho_f": 1800.E-9})})

# ----- GPa et mm
Dict_mat = dict({'T300_914': dict({'nom' : 'T300_914', "Vf":0.6, "Em":3.5, "num":0.3, "Ef":260, "nuf":0.33, "Gflt":97.7}),
                  'E_914': dict({'nom' : 'E_914', "Vf":0.6, "Em":3.5, "num":0.3, "Ef":73, "nuf":0.22, "Gflt":35.2})})


# ----- MPa et mm 
Dict_mat = dict({'T300_914': dict({'nom' : 'T300_914', "Vf":0.6, "Em":35.E+2, "num":0.3, "Ef":260.E+3, "nuf":0.33, "Gflt":977.E+2, "ms": 242.E-6, "rho_r": 1240.E-6, "rho_f": 1800.E-6}),
                  'E_914': dict({'nom' : 'E_914', "Vf":0.6, "Em":35.E+2, "num":0.3, "Ef":73.E+3, "nuf":0.22, "Gflt":352.E+2, "ms": 242.E-6, "rho_r": 1240.E-6, "rho_f": 1800.E-6})})
Dict_mat = dict({'T300_914': dict({'nom' : 'T300_914', "Vf":0.6, "Em":35.E+2, "num":0.3, "Ef":260.E+3, "nuf":0.33, "Gflt":977.E+2, "ms": 242.E-6, "rho_r": 1240.E-6, "rho_f": 1800.E-6,
                                    "resistances": dict({"TsaiWu":dict({"F11": 0.45*10**(-6), "F22": 100*10**(-6), "F12": -3.36*10**(-6), "F66": 2.16*10**(-6), "F1": 0, "F2": 20.1*10**(-3)}),
                                                        "cont_Max":dict({"Xt":1380, "Xc":1430, "Yt":40, "Yc":245, "S":70})})}),
                  'E_914': dict({'nom' : 'E_914', "Vf":0.6, "Em":35.E+2, "num":0.3, "Ef":73.E+2, "nuf":0.22, "Gflt":352.E+2, "ms": 242.E-6, "rho_r": 1240.E-6, "rho_f": 1800.E-6,
                                  "resistances": dict({"TsaiWu":dict({"F11": 1.55*10**(-6), "F22": 275*10**(-6), "F12": -10.25*10**(-6), "F66": 195*10**(-6), "F1": 0.7*10**(-3), "F2": 23.8*10**(-3)}),
                                                      "cont_Max":dict({"Xt":1400, "Xc":910, "Yt":35, "Yc":110, "S":70})})})})


# ep1 = 157.E-3
# ep1 = 158.4E-3ù
# ep1 = 170E-3
# ep1 = 160.E-3
# ep2 = 180.E-3

### Plis

# T300_914 = Materiau(Dict_mat["T300_914"],  ep = ep1)
# epaisseur = np.linspace(0.100, 0.200, 100)
# liste_vf = []
# for k in range(len(epaisseur)):
#     T300_914 = Materiau(Dict_mat["T300_914"],  ep = epaisseur[k])
#     liste_vf.append(T300_914.props["Vf"])
# plt.plot(epaisseur, liste_vf)
# print(T300_914)

# start_time = time.time()
# T300_914_pli_0  = Pli(Dict_mat["T300_914"], 0,  ep = ep1)
# T300_914_pli_45 = Pli(Dict_mat["T300_914"], 45,  ep = ep1)
# T300_914_pli_45_neg = Pli(Dict_mat["T300_914"], -45,  ep = ep1)
# T300_914_pli_90 = Pli(Dict_mat["T300_914"], 90,  ep = ep1)
# # end_time = time.time()
# # print(f'temps calcul plis = {end_time-start_time}')
# T300_914_pli_90_neg = Pli(Dict_mat["T300_914"], -90,  ep = ep1)
# T300_914_pli_0_bis  = Pli(Dict_mat["T300_914"], 0,  ep = ep1)
# T300_914_pli_20 = Pli(Dict_mat["T300_914"], 20,  ep = ep1)

# E_914_pli_0  = Pli(Dict_mat["E_914"], 0, ep = ep2)
# E_914_pli_45 = Pli(Dict_mat["E_914"], 45, ep = ep2)
# E_914_pli_90 = Pli(Dict_mat["E_914"], 90, ep = ep2)

# ame_pli = Pli(Dict_mat["âme"], 0, ep = ep2)

# print(T300_914_pli_0)
# print(E_914_pli_0)



'''2/ Création de séquences'''
### Séquences exemples
# largeur = 1.E-1
# largeur = 15.2
largeur = 1.5

# orientation = 90
# seq0 = [Pli(Dict_mat["T300_914"], orientation,  ep = ep1), Pli(Dict_mat["T300_914"], orientation,  ep = ep1), Pli(Dict_mat["T300_914"], orientation,  ep = ep1), Pli(Dict_mat["T300_914"], orientation,  ep = ep1), Pli(Dict_mat["T300_914"], orientation,  ep = ep1)] + [Pli(Dict_mat["T300_914"], orientation,  ep = ep1), Pli(Dict_mat["T300_914"], orientation,  ep = ep1), Pli(Dict_mat["T300_914"], orientation,  ep = ep1), Pli(Dict_mat["T300_914"], orientation,  ep = ep1), Pli(Dict_mat["T300_914"], orientation,  ep = ep1)]
# T300_914_emp0 = Empilement(seq0, largeur)
# # T300_914_emp0.Dessin_pli('')
# T300_914_emp0.Affichage(0)
# print(T300_914_emp0.masse)
# T300_914_emp0.Affichage_pol_cart(true, true, [0], '')

# seq0 = [T300_914_pli_0, E_914_pli_0]
# T300_914_emp0 = Empilement(seq0, largeur)
# # # T300_914_emp0.Dessin_pli('')
# T300_914_emp0.Affichage(0)

# seqEchec = [T300_914_pli_0] * 12
# T300_914_empEchec = Empilement(seqEchec, largeur)
# T300_914_empEchec.Dessin_pli('')
# T300_914_empEchec.Affichage(0)

# seq1 = [T300_914_pli_0,T300_914_pli_0,T300_914_pli_0,T300_914_pli_0,T300_914_pli_0,T300_914_pli_0,T300_914_pli_0]
# T300_914_emp1 = Empilement(seq1, largeur)
# coef_nuls = T300_914_emp1.Affichage_pol_cart(True, True, [0, 1, 2, 3, 4], 0)
# if not coef_nuls:
#     print('Pas de coefficient nuls')
# else:
#     print('coef_nuls')
# T300_914_emp1.Dessin_pli('')
# T300_914_emp1.Dessin_pli('mod')


# # Section symétrique
# seq2 = [T300_914_pli_0,T300_914_pli_0,T300_914_pli_90,T300_914_pli_90,T300_914_pli_90,T300_914_pli_0,T300_914_pli_0]
# T300_914_emp2 = Empilement(seq2, largeur)
# T300_914_emp2.Dessin_pli('')

# # Section symétrique
# seq6 = [T300_914_pli_0,T300_914_pli_0,T300_914_pli_45,T300_914_pli_45,T300_914_pli_45_neg,T300_914_pli_45_neg,T300_914_pli_0, T300_914_pli_0]
# T300_914_emp6 = Empilement(seq6, largeur)
# T300_914_emp6.Dessin_pli('')

# seq9 = [T300_914_pli_45, T300_914_pli_45_neg, T300_914_pli_45_neg, T300_914_pli_45]
# T300_914_emp9 = Empilement(seq9, largeur)

# Section anti-symétrique
# seq4 = [T300_914_pli_0,T300_914_pli_0,T300_914_pli_90,T300_914_pli_90,T300_914_pli_90_neg,T300_914_pli_90_neg,T300_914_pli_0, E_914_pli_0, T300_914_pli_0]
# T300_914_emp4 = Empilement(seq4, largeur)
# T300_914_emp4.Dessin_pli('')
# T300_914_emp4.Dessin_pli('mod')

# seq10 = [T300_914_pli_0,E_914_pli_0]
# T300_914_emp10 = Empilement(seq10, largeur)
# T300_914_emp10.Dessin_pli('')


# # Section croisée asymétrique
# seq5 = [T300_914_pli_0,T300_914_pli_0,T300_914_pli_90,T300_914_pli_90,T300_914_pli_0,T300_914_pli_0,T300_914_pli_90, T300_914_pli_90]
# T300_914_emp5 = Empilement(seq5, largeur)
# T300_914_emp5.Dessin_pli('')

# # Section croisée asymétrique
# seq7 = [T300_914_pli_0,T300_914_pli_0,T300_914_pli_45_neg,T300_914_pli_45_neg,T300_914_pli_0,T300_914_pli_0,T300_914_pli_45_neg, T300_914_pli_45_neg]
# T300_914_emp7 = Empilement(seq7, largeur)
# coef_nuls = T300_914_emp7.Affichage_pol_cart(True, True, [0, 1, 2, 3, 4], 0)
# T300_914_emp7.Dessin_pli('')
# T300_914_emp7.Affichage(0)

# # Section croisée asymétrique
# seq3 = []
# n = 1
# for k in range(n):
#     seq3.append(T300_914_pli_0)
# for k in range(n):
#     seq3.append(T300_914_pli_90)
# T300_914_emp3 = Empilement(seq3, largeur)
# T300_914_emp3.Dessin_pli('')

# Section croisée asymétrique
# seq3 = []
# n = 2
# for k in range(n):
#     seq3.append(T300_914_pli_0)
# for k in range(n):
#     seq3.append(E_914_pli_90)
# T300_914_emp3 = Empilement(seq3, largeur)
# T300_914_emp3.Dessin_pli('')


# print(T300_914_emp1)
# print(T300_914_emp2)

# Section avec âme
# seq_ame = [T300_914_pli_0, ame_pli, T300_914_pli_0]
# # seq_ame = [ame_pli]
# T300_914_emp_ame = Empilement(seq_ame, largeur)
# T300_914_emp_ame.Dessin_pli('')
# T300_914_emp_ame.Affichage(0)

""" 2bis/ Empilements TP """
# seq0_bis = [T300_914_pli_0] * 12
# T300_914_emp0_bis = Empilement(seq0_bis, largeur)
# # print(T300_914_emp0_bis.L_section)
# # T300_914_emp0_bis.Affichage(0)
# T300_914_emp0_bis.Dessin_pli('')
# L_section_0_bis = T300_914_emp0_bis.L_section

# seq2 = [T300_914_pli_0] * 3 + [T300_914_pli_90] * 6 + [T300_914_pli_0] * 3
# T300_914_emp2 = Empilement(seq2, largeur)
# # print(T300_914_emp2.L_section)
# T300_914_emp2.Affichage(90)
# L_section_2 = T300_914_emp2.L_section

# seq3 = [T300_914_pli_0] * 3 + [E_914_pli_0] * 6 + [T300_914_pli_0] * 3
# T300_914_emp3 = Empilement(seq3, largeur)
# # print(T300_914_emp3.L_section)
# L_section_3 = T300_914_emp3.L_section

# seq4 = [T300_914_pli_90] * 3 + [E_914_pli_0] * 6 + [T300_914_pli_90] * 3
# T300_914_emp4 = Empilement(seq4, largeur)
# # print(T300_914_emp4.L_section)
# L_section_4 = T300_914_emp4.L_section

"""Empilements tests GA"""
# seq1 = [Pli(Dict_mat["T300_914"], 0, ep=ep1)] + [Pli(Dict_mat["T300_914"], 45, ep=ep1)]  + [Pli(Dict_mat["T300_914"], 90, ep=ep1)] + [Pli(Dict_mat["T300_914"], 90, ep=ep1)] + [Pli(Dict_mat["T300_914"], 45, ep=ep1)]  + [Pli(Dict_mat["T300_914"], 0, ep=ep1)]
# seq1 = [Pli(Dict_mat["T300_914"], 0, ep=ep1)] + [Pli(Dict_mat["T300_914"], 0, ep=ep1)]
# empGA = Empilement(seq1, largeur)
# empGA.Dessin_pli('')
# empGA.Affichage(0)

""" 3/ Test d'importation de fichiers excels """
def Plis_from_excel(chemin):
    plis = read_excel(chemin).iloc[:, :3].values
    seq = [Pli(Dict_mat[row[0]], row[1], ep=row[2]) for row in plis]
    emp = Empilement(seq, largeur)
    return emp

# start_time = time.time()
emp_pan = Plis_from_excel(chemin_pour_sphinx('Ressources/Template_batch.xlsx'))
# end_time = time.time()
# print(f'temps rigi loc = {end_time-start_time}')

# coef_nuls = emp_pan.Affichage_pol_cart(True, True, [0, 1, 2, 3, 4], 0)
emp_pan.Dessin_pli('')
emp_pan.Affichage(0)
# emp_pan.Dessin_pli('mod')
# print(emp_pan)

# emp_big_pan = Plis_from_excel(chemin_pour_sphinx('Ressources/Template_big_batch.xlsx'))



''' 4/ Test du calculateur de contraintes'''
emp_test = emp_pan # emp_pan, T300_914_empEchec, T300_914_emp0, T300_914_emp9, emp_big_pan, T300_914_emp0_bis, T300_914_emp_ame

# ''' POUTRES '''
# '''Efforts'''
Fy = 750
T = -Fy
M = Fy*20
Force = (4.2)*emp_test.get_ep_emp()*largeur
# # print(f'Force généralisée {Force} N')
# eff_gen = [Force,0,0,0,0,0]

# '''Géométrie'''
alt = 0 
coord = [0, 0, alt]

# '''Contraintes, déformations'''
indice_voigt = 5
liste_indice_voigt = [1,5,6]
nb_point = 30
methode_rupt = 'Tsaï-Wu' # Tsaï-Wu ou Contraintes Max ou Hill ou Hill_lam ou Tsaï-Wu_lam


# calculateur = CalculContraintes(emp_test)
# rig = calculateur.get_rigidite_angle()
# def_gen = calculateur.def_gen(rig, eff_gen)

# def_memb, def_courb = calculateur.def_memb_cour(def_gen)
# def_loc, def_loc_pli = calculateur.def_loc(eff_gen, coord)
# sig_struct, sig_pli, pli, def_loc_struct, def_loc_pli = calculateur.contraintes_et_def_loc(eff_gen, coord, -1)
# pli_voulu = calculateur.cherche_pli(coord)
# L_i = calculateur.Li_struct(pli_voulu)

# # '''Calculs états contraintes et déformations dans la section'''
# tableau_coord, hauteur_grid, largeur_grid = calculateur.tableau_coord(nb_point)
# contraintes_section, def_section = calculateur.contraintes_et_def_section(eff_gen, tableau_coord, methode_rupt, 'total')

# Utils.stockage_final()

# ''''Dessins'''
# for mode in ['def', 'cont']:
#     if mode == 'def':
#         tableau = def_section
#     else:
#         tableau = contraintes_section
#     for ind_voigt in [1,5,6]:
#         CalculContraintes.dessin_section(calculateur, tableau, largeur_grid, hauteur_grid, ind_voigt, mode)


# ''' 5/ Verification des critères '''
# CalculResistances.dessin_rupture(largeur_grid, hauteur_grid, calculateur.rupture)


'''Test contrainte dans les plaques'''
# eff_gen = [Force,Force,Force,Force,Force,Force,Force,Force]
eff_gen = [Force,0,0,0,0,0,0,0]

# SD, 03/10/2024
# Pour tester simplement les critères de résistance Hill ou Tsai-Wu, on travaille d'abord sur un pli seul
# pli_test = emp_test.liste_de_pli[0]
# resist_test = CalculResistances(pli_test)
# calculateur = CalculContraintesPlaques(emp_test)
# tableau_coord, hauteur_grid, largeur_grid = calculateur.tableau_coord(nb_point)
# rig = calculateur.get_rigidite_angle()
# def_gen = calculateur.def_gen(rig, eff_gen)

# sig_struct, sig_pli, pli, def_loc_struct, def_loc_pli = calculateur.contraintes_et_def_loc(eff_gen, coord, -1)

# crit, reserve = CalculResistances.Tsai_Wu(pli_test) 


# SD, 03/10/2024
# les méthodes de calcul des résistances ci-dessous sont à vérifier (XX_lam), mais elles ont l'avantage de traiter
# les séquences d'empilement complètes en 1 seule fois.

calculateur = CalculContraintesPlaques(emp_test)
# resist_test = CalculResistances
tableau_coord, hauteur_grid, largeur_grid = calculateur.tableau_coord(nb_point)
rig = calculateur.get_rigidite_angle()
def_gen = calculateur.def_gen(rig, eff_gen)
start_time = time.time()

# def_memb, def_courb = calculateur.def_memb_cour(def_gen)
# def_loc, def_loc_pli = calculateur.def_loc(eff_gen, coord)
sig_struct, sig_pli, pli, def_loc_struct, def_loc_pli = calculateur.contraintes_et_def_loc(eff_gen, coord, -1)

if methode_rupt == 'Hill_lam':
    crit, reserve = CalculResistances.Hill_lam(emp_test, def_gen[0:3], def_gen[4:6])
elif methode_rupt == 'Tsaï-Wu_lam':
    crit, reserve = CalculResistances.Tsai_Wu_lam(emp_test, def_gen[0:3], def_gen[4:6])  
else:
    def_memb, def_courb, def_cis = calculateur.def_memb_cour(def_gen)
    def_loc, def_loc_pli = calculateur.def_loc(eff_gen, coord)
    sig_struct, sig_pli, pli, def_loc_struct, def_loc_pli = calculateur.contraintes_et_def_loc(eff_gen, coord, -1)
    contraintes_brin, def_brin = calculateur.contraintes_et_def_section(eff_gen, tableau_coord, methode_rupt, 'total')
    
    # # # Dessins
    for mode in ['def', 'cont']:
        if mode == 'def':
            tableau = def_brin
        else:
            tableau = contraintes_brin
        for ind_voigt in [1, 2, 4, 5, 6]:
            CalculContraintesPlaques.dessin_section(calculateur, tableau, largeur_grid, hauteur_grid, ind_voigt, mode)
    
    CalculResistances.dessin_rupture(largeur_grid, hauteur_grid, calculateur.rupture)
end_time = time.time()
# print(f'temps cont = {end_time-start_time}')

''' 6/ Affichages console'''
# print(f'rigigdité dans la direction de sollicitation : {rig}\n')
# print(f'déformations généralisées : {def_gen}\n')
# print(f'déformations de membrane : {def_memb},\ndéformations de courbure : {def_courb}\n')
# print(f'déformations localisées : {def_loc}\n')
# print(f"Le pli cherché à une altitude de {coord[2]} mm est:\n{pli_voulu}\n")
# print(f"L_i du pli recherché :\n{L_i}\n")
# print(f"Contrainte localisée (N.mm^(-2)): {contraintes_loc}\n")
# print(f"Contraintes dans la section (N.mm^(-2)): {contraintes_section}\n")
print(f"Tableau de coordonées : {tableau_coord}")
# print(f"Critère de rupture {methode_rupt} : {calculateur.rupture['rupt_max']['crit']}\nReserve : {calculateur.rupture['rupt_max']['reserve']}")

# cont_max, coord_max_cont = calculateur.res_max[cont_ind_max]['axe_struct']['valeur'], calculateur.res_max[cont_ind_max]['axe_struct']['coord']
# cont_max_pli, coord_max_cont_pli = calculateur.res_max[cont_ind_max]['axe_pli']['valeur'], calculateur.res_max[cont_ind_max]['axe_pli']['coord']
# non_zero_index = next((i for i, digit in enumerate('{:.15f}'.format(cont_max)) if digit != '0' and digit != '.'), 0)
# print(f"Contrainte{indice_voigt} max : {round(cont_max, non_zero_index)}, de coord {coord_max_cont}")
# non_zero_index = next((i for i, digit in enumerate('{:.15f}'.format(cont_max_pli)) if digit != '0' and digit != '.'), 0)
# print(f"Contrainte{indice_voigt} max pli: {round(cont_max_pli, non_zero_index)}, de coord {coord_max_cont_pli}")
# def_ind_max = 'def_' + str(indice_voigt) + '_max'
# cont_ind_max = 'cont_' + str(indice_voigt) + '_max'
# non_zero_index = next((i for i, digit in enumerate('{:.15f}'.format(calculateur.res_max[def_ind_max]['axe_struct']['valeur'])) if digit != '0' and digit != '.'), 0)
# print(f"Déformation{indice_voigt} max : {round(calculateur.res_max[def_ind_max]['axe_struct']['valeur'], non_zero_index)}, de coord {calculateur.res_max[def_ind_max]['axe_struct']['coord']}")


# print(f"Mode de rupture : {calculateur.rupture['rupt_max']['mode_rupt']['nom_rupt']}\nValeur : {calculateur.rupture['rupt_max']['mode_rupt']['val_rupt_pli']:.2e} MPa")



''' 7/ Tests du stockage json '''
# dico_rupture_deseral = Utils.destockage("Ressources/donnees_json/rupture.json")

# from utils import Utils
# L_section = Utils.destockage("Ressources/donnees_json/L_section.json")


# Utils.vider_les_doss()

''' 8/ Autres Tests '''
# emp_test_cont = T300_914_empEchec
# emp_test_cont.L_section # Il faut que ce soit la même que rig utilisée par contraintes
# def_gen_main = np.dot(np.linalg.inv(emp_test_cont.L_section),np.array(eff_gen).T)
# calculateur.pli_dans_section[0,0].props['nom']
# calculateur.pli_dans_section[29,0].props['nom']
# calculateur.pli_dans_section[29,0].orientation
# calculateur.pli_dans_section[15,0].orientation

# print(Utils.plaque)
# Utils.plaque = 1
# print(Utils.plaque)
# pts_exp_def = pts_exp_cont = []
# pts_exp_def = [0.005, 0.01, 0.02]
# pts_exp_cont = [100, 250, 500]
# pts_exp_def = [0.5, 1.5, 2.5]
# pts_exp_cont = [10000, 40000, 60000]
# Utils.plot_def_cont(L_section_2[0,0], 0.02, pts_exp_def, pts_exp_cont)

''' Essai de flexion 4 points '''
# Propriétés géométriques
# a = 20
# l = 60
# # Grp 5
# b = 1.9
# h = 15.2
# # # Grp 6
# # b = 2.41
# # h = 15.5
# # # Grp 8
# # b = 1.9
# # h = 15.6
# EI = L_section_2[2,2] # L_section_0_bis (0C), L_section_2 (0C, 90C), L_section_3 (0V, 0C), L_section_4 (0V, 90C)
# GLT = 75272.17876705294
# # GLT = 72228.48944186453 
# force_test = 1300/2 # Force qui borne le domaine élastique , 1300/2 , 300/2



# # Modèle analytique
# def dep(Fy):
#     return (Fy*a**2/(6*EI)*(4*a-3*l))                     # Sans cisaillement
#     # return Fy*a/(2*EI)*((a**2)/3+a*(a-l)-EI*2/(GLT*b*h))    # Avec cisaillement
# liste_force = np.linspace(0, force_test, 100)

# # Modèle expérimentale
# df = pd.read_excel('C:/Users/lbonn/Documents/EMSE/Cours_EMSE/majeures/Méca/Up_Comportements équivalents/Tp/Tp2/C5_bis.xlsx')
# # df = pd.read_excel('C:/Users/lbonn/Documents/EMSE/Cours_EMSE/majeures/Méca/Up_Comportements équivalents/Tp/Tp2/C6.xlsx')  # (0V, 90C)
# # df = pd.read_excel('C:/Users/lbonn/Documents/EMSE/Cours_EMSE/majeures/Méca/Up_Comportements équivalents/Tp/Tp2/C7.xlsx')  # (0V, 0C)
# # df = pd.read_excel('C:/Users/lbonn/Documents/EMSE/Cours_EMSE/majeures/Méca/Up_Comportements équivalents/Tp/Tp2/C8.xlsx')  # (0C, 90C)


# # Get the first two columns
# pts_exp_def = np.array(df.iloc[:, 0].tolist())-np.array([3.2]*len(np.array(df.iloc[:, 0].tolist())))  # First column
# pts_exp_cont = np.array(df.iloc[:, 1].tolist())/2 # Second column
# # pts_exp_def = np.array([0, 0.8571428571428571, 1.7142857142857142, 2.5714285714285716, 2.7857142857142856,3.2142857142857144])
# # pts_exp_cont = np.array([0, 200, 500, 600, 800, 1000])/2



# # Tracé des courbes
# fig, ax = plt.subplots(dpi=250)
# model = LinearRegression()
# x_reshaped = pts_exp_def.reshape(-1, 1)
# model.fit(x_reshaped, pts_exp_cont)
# slope = model.coef_[0]
# EI_exp = - slope / (6/((4*a-3*l)*a**2))
# intercept = model.intercept_
# ax.scatter(pts_exp_def, pts_exp_cont, label='Points expérimentaux', marker='+', color='g')
# ax.plot(pts_exp_def, slope * pts_exp_def + intercept, color='red', label=f'Regression Linéaire: <EI>  = {EI_exp:.1e}')
# ax.plot(abs(dep(liste_force)), liste_force, label='Courbe analytique')
# correlation_coefficient = np.corrcoef(pts_exp_def, pts_exp_cont)[0, 1]
# ax.set_title('Courbe force-déplacement en a')
# ax.set_xlabel('Déplacement (mm)')
# ax.set_ylabel('Force (N)')
# ax.legend()

# print(f'Le déplacement est de : {dep(force_test)} pour une force de {force_test}\n')
# print(f'Le coefficient de correlation est {correlation_coefficient}\n')
# print(f"EI: {EI}, EI_exp: {EI_exp}, l'écart est de {abs((EI_exp-EI)/EI*100):.2f} %\n")


