# -*- coding: utf-8 -*-
"""
Created on Tue Jan  2 19:44:39 2024

@author: lbonn

# =============================================================================
Classe pour les résistances
    1) Critères de rupture local
    2) Critères de rupture homogène
        Critères : Hill, contraintes-max, Tsaï-Wu
    3) Modes du rupture
    4) Affichage du critère dans la section
# =============================================================================


"""
from utils import Line2D, make_axes_locatable, plt, m, np, Utils, polar

''' Classe pour calculer les resistances'''
class CalculResistances():
    '''
    Les contraintes sont données par : [sig_1, sig_2, sig_6]

    .. attribute:: coeffs : Dict
    
        Dictionnaire contenant les résistances pour chaque critère pour le matériau en question
        
    .. attribute:: rupture : Dict
    
        Dictionnaire contenant les informations sur la rupture
        
    .. attribute:: l : float
    
        demi largeur de l'empilement
        
    .. attribute:: h : float
    
        demi hauteur de l'empilement
        
    .. attribute:: nb_grad_x : float
    
        nombre de graduation pour les abscisses des sections

    .. attribute:: nb_grad_y : np.array((nbr d'angle, 6, 6))
                                            
        nombre de graduation pour les ordonnées des sections
        
    '''
    def __init__(self, pli):
        self.coeffs = pli.props["resistances"]
        
    def cont_Max(self, cont):
        """
        Calcule le critère de rupture en contrainte max (réctifiée).
        Si R < 1 : pas de rupture
        Si R >= 1 : rupture

        Parameters
        ----------
        cont : np.array((1,3))
            [sig_1, sig_2, sig_6]

        Returns
        -------
        min_value : float
            Résistance
        reserve : float
            réserve à rupture en MPa

        """
        coef = self.coeffs["cont_Max"]
        sig1, sig2, sig6 = cont
        cont_tab = [sig1, sig2, sig6]
        Xt, Xc, Yt, Yc, S = coef["Xt"], coef["Xc"], coef["Yt"], coef["Yc"], coef["S"]
        
        res_tab = np.array([])
        if sig1 <= 0: # On est en compression
            res_tab =  np.append(res_tab, abs(sig1)/Xc)
        else:
            res_tab =  np.append(res_tab, abs(sig1)/Xt)
        if sig2 <= 0:
            res_tab =  np.append(res_tab, abs(sig2)/Yc)
        else:
            res_tab =  np.append(res_tab, abs(sig2)/Yt)
        res_tab = np.append(res_tab, abs(sig6)/S)
        
        
        max_index = np.argmax(res_tab)
        max_value = np.max(res_tab)
        sig = res_tab[max_index]
        
        return max_value, 1/max_value
    
    def Hill(self, cont):
        coef = self.coeffs["cont_Max"]
        sig1, sig2, sig6 = cont
        cont_tab = [sig1, sig2, sig6]
        Xt, Xc, Yt, Yc, S = coef["Xt"], coef["Xc"], coef["Yt"], coef["Yc"], coef["S"]
        
        X = Xt
        Y = Yt
        
        crit = (sig1/X)**2 + (sig2/Y)**2 - (sig1*sig2)/(X**2) + (sig6/S)**2
        
        return crit, 1/crit
    
    def Hill_lam(emp, eps, khi):
        """
        Critère de rupture de Hill homogénéisé

        Parameters
        ----------
        emp : Empilement
            empilement pour pouvoir accéder aux angles
        eps : np.array((1,3))
            tenseur des déformations de membrane généralisé.
        khi : np.array((1,3))
            tenseur des déformations de courbure généralisé.

        Returns
        -------
        Flam : float
            critère de rupture
        validite : int
            indique si les critères de validité du tenseur sont validées
            CATAPANO relation (1.72)
            0 -> non, 1 -> non

        """
        hm = - emp.get_ep_emp() / 2
        Ga , Gb, Gd = np.zeros((3,3)), np.zeros((3,3)), np.zeros((3,3))
        
        liste_G = []
        
        for i in range(len(emp.liste_de_pli)):
            hM = hm + emp.liste_de_pli[i].props["ep"]
            Lp11, Lp55, Lp66, Lp16, Lp12, Lp22, Lp26, Lp44, Lp45 = emp.liste_de_pli[i].Lcp_oriente
            coef = emp.liste_de_pli[i].props["resistances"]["cont_Max"]
            Xt, Xc, Yt, Yc, S = coef["Xt"], coef["Xc"], coef["Yt"], coef["Yc"], coef["S"]
            X, Y = Xt, Yt
            
            G = np.array([[1/(X**2), -1/(2*X**2), 0], [-1/(2*X**2), 1/(Y**2), 0], [0, 0, 1/(S**2)]])
                        
            Q = np.array([[Lp11, Lp12, Lp16], [Lp12, Lp22, Lp26], [Lp16, Lp26, Lp66]])
            
            Gk = np.dot(np.dot(Q.T, G), Q)
            
            liste_G.append(Gk)
            Ga += Gk*(hM-hm)
            
            Gb += Gk*(hM**2-hm**2)/2
            Gd += Gk*(hM**3-hm**3)/3
            
            # ----- Test de validité de la décomposition polaire : On construit Qa, commenter l138 et 139
            # liste_G.append(Q)
            # Ga += Q*(hM-hm)
            
            hm = hM
           
        # ----- On créer les représentations polaires de la matrice de resistance homogénéisée et de la matrice de résistance de chaque pli
        # 1) Représentation polaire de l'empilement
        validite = 1
        Gastar = Ga / emp.get_ep_emp()
        TB0 = 1/8*(Gastar[0,0] - 2*Gastar[0,1] + 4*Gastar[2,2] + Gastar[1,1])
        TB1 = 1/8*(Gastar[0,0] + 2*Gastar[0,1] + Gastar[1,1])
        LAMBDA0_Barre_8, OMEGA0_4 = polar(complex(Gastar[0,0] - 2*Gastar[0,1] - 4*Gastar[2,2] + Gastar[1,1], 4*Gastar[0,2] - 4*Gastar[1,2]))
        LAMBDA1_Barre_8, OMEGA1_2 = polar(complex(Gastar[0,0] - Gastar[1,1], 2*Gastar[0,2] + 2*Gastar[1,2]))
        LB0, LB1 = LAMBDA0_Barre_8/8, LAMBDA1_Barre_8/8
        # print(m.degrees(OMEGA0_4/4-OMEGA1_2/2))

        
        # 2) Représentation polaire d'un pli + vérification des bornes géométriques : rel 6.26
        G = liste_G[0]
        T0 = 1/8*(G[0,0] - 2*G[0,1] + 4*G[2,2] + G[1,1])
        T1 = 1/8*(G[0,0] + 2*G[0,1] + G[1,1])
        LAMBDA0_8, OMEGA0_4 = polar(complex(G[0,0] - 2*G[0,1] - 4*G[2,2] + G[1,1], 4*G[0,2] - 4*G[1,2]))
        LAMBDA1_8, OMEGA1_2 = polar(complex(G[0,0] - G[1,1], 2*G[0,2] + 2*G[1,2]))
        L0, L1 = LAMBDA0_8/8, LAMBDA1_8/8
        OMEGA0, OMEGA1 = OMEGA0_4/4, OMEGA1_2/2
        # print(m.degrees(OMEGA0-OMEGA1))
        
        if 2*((LB1/L1)**2) - 1 <= LB0 / L0 or (abs(2*((LB1/L1)**2) - 1) <= 10**(-9) and abs(LB0 / L0) <= 10**(-15)) and (abs(LB0) <= L0 or abs(L0-abs(LB0)) <= 10**(-10)) and L1 >= 0:
            pass
        else:
            validite = 0

        Flam = (1/emp.get_ep_emp())*(np.dot(np.dot(eps, Ga), eps.T) 
                                     + np.dot(np.dot(khi, Gd), khi.T) 
                                     + 2 * np.dot(np.dot(eps, Gb), khi.T) )
        return Flam, validite
    
    def Tsai_Wu(self,cont):
        """
        Calcule le critère de rupture de Tsaï-Wu

        Parameters
        ----------
        cont : np.array((1,3))
            [sig_1, sig_2, sig_6]

        Returns
        -------
        min_value : float
            Résistance
        reserve : float
            réserve à rupture en MPa

        """
        coef = self.coeffs["TsaiWu"]
        sig1, sig2, sig6 = cont
        F11, F22, F12, F66, F1, F2 = coef["F11"], coef["F22"], coef["F12"], coef["F66"], coef["F1"], coef["F2"]
        F12_star=F11*F12/((F11*F22)**0.5)
        # cont = np.array([cont[0], cont[4], cont[5]]) # On récupère les contraintes planes
        F_vect = np.array([F1, F2, 0])
        F_tens = np.array([[F11, F12_star, 0], [F12, F22, 0], [0, 0, F66]])
        crit = np.dot(F_vect, cont) + np.dot(np.dot(cont, F_tens), cont)
        # crit = F1*sig1 + F2*sig2 + F11*sig1**2 + F22*sig2**2 + 2*F12*sig1*sig2 + 2*F66*sig6**2
        
        b, a, c = F1 * sig1 + F2 * sig2, F11 * sig1**2 + F22 * sig2**2 + 2*F12_star * sig1 * sig2 + 2 * F66 * (sig6**2), -1
        discri = b**2 - 4 * a * c
        tab_cherhe_min = [0]
        if discri > 0:
            x1, x2 = (-b - m.sqrt(discri))/(2*a), (-b + m.sqrt(discri))/(2*a)
            # print("a",a, "b" ,b ,"discri : " , discri,"x1 :", x1,"x2 :", x2)
            # TODO : distinguer le cas où cont[k] < 0
            if x1 > 0:
                tab_cherhe_min = tab_cherhe_min + [x1]
            if x2 > 0:
                tab_cherhe_min = tab_cherhe_min + [x2]
    #P Thomas 22/10, modification pour ne pas renvoyer que 0
            if len(tab_cherhe_min)<=2: #1 seul élement on renvoie 0
                # print("crit :", crit, "max :" ,max(tab_cherhe_min))
                return crit, max(tab_cherhe_min)
            else:
                if x1 < x2 :
                    return crit, x1
                else :
                    return crit, x2
        # return crit, min(tab_cherhe_min)
    
    def Tsai_Wu_lam(emp, eps, khi):
        """
        Critère de rupture de Tsaï-Wu homogénéisé

        Parameters
        ----------
        emp : Empilement
            empilement pour pouvoir accéder aux angles
        eps : np.array((1,3))
            tenseur des déformations de membrane généralisé.
        khi : np.array((1,3))
            tenseur des déformations de courbure généralisé.

        Returns
        -------
        Flam : float
            critère de rupture
        validite : int
            indique si les critères de validité du tenseur sont validées
            CATAPANO relation (1.72)
            0 -> non, 1 -> non

        """
        hm = - emp.get_ep_emp() / 2
        Ga , Gb, Gd = np.zeros((3,3)), np.zeros((3,3)), np.zeros((3,3))
        Ha , Hb = np.zeros((3)), np.zeros((3))
        
        liste_G = []
        
        for i in range(len(emp.liste_de_pli)):
            hM = hm + emp.liste_de_pli[i].props["ep"]
            Lp11, Lp55, Lp66, Lp16, Lp12, Lp22, Lp26, Lp44, Lp45 = emp.liste_de_pli[i].Lcp_oriente
            coef = emp.liste_de_pli[i].props["resistances"]["TsaiWu"]
            F11, F22, F12, F66, F1, F2 = coef["F11"], coef["F22"], coef["F12"], coef["F66"], coef["F1"], coef["F2"]
            F_vect = np.array([F1, F2, 0])
            F_tens = np.array([[F11, F12, 0], [F12, F22, 0], [0, 0, F66]])
            
            Q = np.array([[Lp11, Lp12, Lp16], [Lp12, Lp22, Lp26], [Lp16, Lp26, Lp66]])
            # print(Q, F_tens)
            
            Gk = np.dot(np.dot(Q.T, F_tens), Q)
            liste_G.append(Gk)
            Hk = np.dot(F_vect.T, Q)
            
            Ga += Gk*(hM-hm)
            Gb += Gk*(hM**2-hm**2)/2
            Gd += Gk*(hM**3-hm**3)/3
            Ha += Hk*(hM-hm)
            Hb += Hk*(hM**2-hm**2)/2
            hm = hM
    
        Flam = (1/emp.get_ep_emp())*(np.dot(np.dot(eps, Ga), eps.T) 
                                 + np.dot(np.dot(khi, Gd), khi.T) 
                                 + 2 * np.dot(np.dot(eps, Gb), khi.T) 
                                 + np.dot(Ha, eps.T)
                                 + np.dot(Hb, khi.T))
           
        # ----- On créer les représentations polaires de la matrice de resistance homogénéisée et de la matrice de résistance de chaque pli
        # 1) Représentation polaire de l'empilement
        validite = 1
        Gastar = Ga / emp.get_ep_emp()
        LAMBDA0_Barre_8, OMEGA1_4 = polar(complex(Gastar[0,0] - 2*Gastar[0,1] - 4*Gastar[2,2] + Gastar[1,1], 4*Gastar[0,2] - 4*Gastar[2,1]))
        LAMBDA1_Barre_8, OMEGA1_2 = polar(complex(Gastar[0,0] - Gastar[1,1], 2*Gastar[0,2] + 2*Gastar[2,1]))
        LB0, LB1 = LAMBDA0_Barre_8/8, LAMBDA1_Barre_8/8
        
        # 2) Représentation polaire de chaque pli + vérification des bornes géométriques : rel 6.26
        for i in range(len(liste_G)):
            G = liste_G[i]
            # print(G)
            T0 = 1/8*(G[0,0] - 2*G[0,1] + 4*G[2,2] + G[1,1])
            T1 = 1/8*(G[0,0] + 2*G[0,1] + G[1,1])
            LAMBDA0_8, OMEGA0_4 = polar(complex(G[0,0] - 2*G[0,1] - 4*G[2,2] + G[1,1], 4*G[0,2] - 4*G[2,1]))
            LAMBDA1_8, OMEGA1_2 = polar(complex(G[0,0] - G[1,1], 2*G[0,2] + 2*G[2,1]))
            L0, L1 = LAMBDA0_8/8, LAMBDA1_8/8
            OMEGA0, OMEGA1 = OMEGA0_4/4, OMEGA1_2/2
            
            if T0 - LB0 > 0 and T1*(T0**2 - LB0**2) - 2*(LB1**2)*(T0 - LB0*np.cos(4*(OMEGA0-OMEGA1))) > 0:
                pass
            else:
                validite = 0
        
        return Flam, validite
    
    def mode_rupture(self, cont, critere):
        """
        Indique le mode de contrainte responsable de la rupture

        Parameters
        ----------
        cont : np.array((1,3))
            contraintes dans le plan du pli
        critere : str
            nom du critère de rupture

        Returns
        -------
        dict
            contient 
            1) 'nom_rupt' : le nom du mode de rupture désigné par la concaténation (si modes combinés responsables) des indices de voigt
            2) 'val_rupt_pli' : la valeur de ce mode de rupture

        """
        sig1, sig2, sig6 = cont
       # print('cont:', cont)
        cont_tab = [sig1, sig2, sig6]
        # crit_mode = 0
        ind_voigt_mode_rupt = []
        if critere == 'Tsaï-Wu':
            # coef = self.coeffs["TsaiWu"]
            # F11, F22, F12, F66, F1, F2 = coef["F11"], coef["F22"], coef["F12"], coef["F66"], coef["F1"], coef["F2"]
            coef = self.coeffs["cont_Max"]
            Xt, Xc, Yt, Yc, S = coef["Xt"], coef["Xc"], coef["Yt"], coef["Yc"], coef["S"]
            # if F1 != 0 and abs(sig1)/F1 > crit_mode:
            #     crit_mode = abs(sig1)/F1
            #     ind_voigt_mode_rupt = [0]
            # if abs(sig2)/F2 > crit_mode:
            #     crit_mode = abs(sig2)/F2
            #     ind_voigt_mode_rupt = [1]
            # if abs(sig2*sig1)/(2*F12) > crit_mode:
            #     crit_mode = abs(sig2*sig1)/(2*F12)
            #     ind_voigt_mode_rupt = [0,1]
            # if abs(sig1**2)/F11 > crit_mode:
            #     crit_mode = abs(sig1**2)/F11
            #     ind_voigt_mode_rupt = [0,0] 
            # if abs(sig2**2)/F22 > crit_mode:
            #     crit_mode = abs(sig2**2)/F22
            #     ind_voigt_mode_rupt = [1,1] 
            # if abs(sig6**2)/(2*F66) > crit_mode:
            #     crit_mode = abs(sig6**2)/(2*F66)
            #     ind_voigt_mode_rupt = [2,2]
            crit, R=self.Tsai_Wu(cont)
            res_tab1 = np.array([])
            if sig1<=0:
                res_tab1=np.append(res_tab1,R*abs(sig1)/Xc)
            else:
                res_tab1=np.append(res_tab1,R*abs(sig1)/Xt)
            if sig2<=0:
                res_tab1=np.append(res_tab1,R*abs(sig2)/Yc)
            else:
                res_tab1=np.append(res_tab1,R*abs(sig2)/Yt)
            res_tab1=np.append(res_tab1,R*abs(sig6)/S)
            indice = np.argmax(res_tab1)

        elif critere == 'Contraintes Max':
            # coef = self.coeffs["cont_Max"]
            # Xt, Xc, Yt, Yc, S = coef["Xt"], coef["Xc"], coef["Yt"], coef["Yc"], coef["S"]
            # res_tab = np.array([])
            # if sig1 <= 0: # On est en compression, valeur de résistance = Xc
            #     res_tab =  np.append(res_tab, abs(sig1)/Xc)
            # else:
            #     res_tab =  np.append(res_tab, abs(sig1)/Xt)
            # if sig2 <= 0:
            #     res_tab =  np.append(res_tab, abs(sig2)/Yc)
            # else:
            #     res_tab =  np.append(res_tab, abs(sig2)/Yt)
            # res_tab = np.append(res_tab, abs(sig6)/S)
            
            # ind_voigt_mode_rupt = np.argmax(res_tab)
            # max_value = np.max(res_tab)
            # sig = res_tab[ind_voigt_mode_rupt]
            # ind_voigt_mode_rupt = [ind_voigt_mode_rupt]
            # P Thomas 08/11, passage à R plutot que 1/R
            coef = self.coeffs["cont_Max"]
            Xt, Xc, Yt, Yc, S = coef["Xt"], coef["Xc"], coef["Yt"], coef["Yc"], coef["S"]
            res_tab = np.array([])
            if sig1 <= 0: # On est en compression, valeur de résistance = Xc
                res_tab =  np.append(res_tab, abs(sig1)/Xc)
            else:
                res_tab =  np.append(res_tab, abs(sig1)/Xt)
            if sig2 <= 0:
                res_tab =  np.append(res_tab, abs(sig2)/Yc)
            else:
                res_tab =  np.append(res_tab, abs(sig2)/Yt)
            res_tab = np.append(res_tab, abs(sig6)/S)
            
            indice = np.argmax(res_tab)
            # sig = res_tab[indice]
        ind_voigt_mode_rupt = [indice]
        
        cont = 1 # On reconstitue la contrainte responsable de la rupture
        ind_voigt_mode_rupt_final = ''
        nom_mode_rupt = ''
        for k in range(len(ind_voigt_mode_rupt)):
            if ind_voigt_mode_rupt[k] == 0:
                ind = 1
            elif ind_voigt_mode_rupt[k] == 1:
                ind = 2
            elif ind_voigt_mode_rupt[k] == 2:
                ind = 6
            if critere == 'Contraintes Max':
                cont *= cont_tab[ind_voigt_mode_rupt[k]]
                nom_mode_rupt ='     Critère en contraintes max donne : σ'+str(ind)
            elif critere == 'Tsaï-Wu':
                cont *= R*cont_tab[ind_voigt_mode_rupt[k]]
                nom_mode_rupt ='Critère en contraintes max donne : R*σ'+str(ind)
        #print('nom_rupt' , nom_mode_rupt, 'val_rupt_pli' , cont)
        return {'nom_rupt' : nom_mode_rupt, 'val_rupt_pli' : cont}
            
    
    def dessin_rupture(largeur_grid, hauteur_grid, rupture):  
        """
        Permet de déssiner l'évolution du critère de rupture sur 
        l'elément de cinématique représentatif (brin pour une plaque, section pour une poutre).
        Place une croix à l'emplacement de où le critère de rupture est maximal
        """
        import materiau as mat
        
        if Utils.plaque == 1:
            nb_grad_x = 1
            l = 0
            chemin = r"Ressources/images_gen/figure_section_rupture_plaque.png"
            largeur_leg = "10%" # Pourcentage de la largeur de l'image
        else:
            nb_grad_x = 3
            l = rupture["l"]
            chemin = r"Ressources/images_gen/figure_section_rupture.png"
            largeur_leg = "50%"
        nb_grad_y = 7
        h = rupture["h"]
        crit = rupture['crit_section']
        taille_grid = np.shape(crit)
        gradu_haut = np.linspace(-h, h, int(taille_grid[0]))
        gradu_larg = np.linspace(-l, l, int(taille_grid[1]))
        tick_positions_x = np.linspace(0, len(gradu_larg) - 1, nb_grad_x, dtype=int)
        tick_positions_y = np.linspace(0, len(gradu_haut) - 1, nb_grad_y, dtype=int)
        
        fig, ax = plt.subplots(dpi=250)
        # styles de cmap : viridis, plasma, inferno, magma, coolwarm, bwr, hsv, tab10, tab20, tab20b
        affich_seq = ax.imshow(crit[:,:],cmap=plt.cm.bwr, origin='lower', vmin=0, vmax=rupture['rupt_max']['crit'])
        
        cross_size = 1
        highlight_cross = Line2D([rupture['rupt_max']['ind'][1] - cross_size / 2, rupture['rupt_max']['ind'][1] + cross_size / 2],
                                 [rupture['rupt_max']['ind'][0], rupture['rupt_max']['ind'][0]], color='black', linewidth=2)
        ax.add_line(highlight_cross)
        
        highlight_cross = Line2D([rupture['rupt_max']['ind'][1], rupture['rupt_max']['ind'][1]],
                                 [rupture['rupt_max']['ind'][0] - cross_size / 2, rupture['rupt_max']['ind'][0] + cross_size / 2], color='black', linewidth=2)
        ax.add_line(highlight_cross)
        
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size=largeur_leg, pad=0.05)
        cbar = fig.colorbar(affich_seq, cax = cax)
        cbar.set_label('')
        ax.set_xticks(tick_positions_x)
        ax.set_xticklabels(np.round(gradu_larg[tick_positions_x], decimals=2))
        ax.set_yticks(tick_positions_y)
        ax.set_yticklabels(np.round(gradu_haut[tick_positions_y], decimals=2))
        ax.set_title("Critère de rupture")
        fig.savefig(mat.chemin_pour_sphinx(chemin), bbox_inches="tight")
        fig.tight_layout()
        plt.close(fig)
        