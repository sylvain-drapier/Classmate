# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 11:05:56 2023

@author: lbonn
"""
# from sympy import *
from utils import Utils, m, np, plt, make_axes_locatable, Line2D, Rectangle, cm
from CalculResistances import CalculResistances




class CalculContraintesPlaques():
    """Calcul les propriétés relatives aux contraintes

    .. attribute:: Empilement : Empilement
    
        Objet contenant l'empilement à étudier
        
    .. attribute:: l : float
    
        demi largeur de l'empilement
        
    .. attribute:: h : float
    
        demi hauteur de l'empilement
        
    .. attribute:: nb_grad_x : float
    
        nombre de graduation pour les abscisses des sections

    .. attribute:: nb_grad_y : np.array((nbr d'angle, 6, 6))
                                            
        nombre de graduation pour les ordonnées des sections
        
    .. attribute:: res_max : float
    
        Dictionnaire contenant les déformations et contraintes maximales dans la section
        
    .. attribute:: rupture : float
    
        Dictionnaire contenant le nom du critère du rupture choisi, les informations sur le maximum de rupture, l et h
    
    """
    offset_eps = Utils.offset_eps
    offset_sig = Utils.offset_sig
    
    def __init__(self, Empilement):
        """
        Constructeur de la classe Empilement.

        Parameters:
        - Empilment (Empilement) : objet Empilement sur lequel est calculé les contraintes localisées
        """
        self.Empilement = Empilement
        self.l = self.Empilement.largeur/2
        self.h = self.Empilement.get_ep_emp()/2
        self.nb_grad_x, self.nb_grad_y = 3, 7
        self.res_max = { # cf p eq.5.123
            'def_1_max': {'axe_struct': {'valeur': 0, 'coord': [0,0,0]}, 'axe_pli': {'valeur': 0, 'coord': [0,0,0]}},
            'def_2_max': {'axe_struct': {'valeur': 0, 'coord': [0,0,0]}, 'axe_pli': {'valeur': 0, 'coord': [0,0,0]}},
            'def_4_max': {'axe_struct': {'valeur': 0, 'coord': [0,0,0]}, 'axe_pli': {'valeur': 0, 'coord': [0,0,0]}},
            'def_5_max': {'axe_struct': {'valeur': 0, 'coord': [0,0,0]}, 'axe_pli': {'valeur': 0, 'coord': [0,0,0]}},
            'def_6_max': {'axe_struct': {'valeur': 0, 'coord': [0,0,0]}, 'axe_pli': {'valeur': 0, 'coord': [0,0,0]}},
            'cont_1_max': {'axe_struct': {'valeur': 0, 'coord': [0,0,0]}, 'axe_pli': {'valeur': 0, 'coord': [0,0,0]}},
            'cont_2_max': {'axe_struct': {'valeur': 0, 'coord': [0,0,0]}, 'axe_pli': {'valeur': 0, 'coord': [0,0,0]}},
            'cont_4_max': {'axe_struct': {'valeur': 0, 'coord': [0,0,0]}, 'axe_pli': {'valeur': 0, 'coord': [0,0,0]}},
            'cont_5_max': {'axe_struct': {'valeur': 0, 'coord': [0,0,0]}, 'axe_pli': {'valeur': 0, 'coord': [0,0,0]}},
            'cont_6_max': {'axe_struct': {'valeur': 0, 'coord': [0,0,0]}, 'axe_pli': {'valeur': 0, 'coord': [0,0,0]}}
        }
        self.rupture = {
            'rupt_max': {'crit': 0, 'reserve': 0, 'coord': [0,0,0], 'ind': [0,0]},
            'crit_section': None,
            'l': self.l,
            'h': self.h}

        
    def tableau_coord(self, n): 
        """
        Génère un tableau n*1 représentant un brin transverse au plan moyen. Chaque case du tableau est un tableau possédant les coordonées [x1, x2, x3] du point qu'il représente'

        Parameters
        ----------
        n : int
            paramètre non utilisé.

        Returns
        -------
        tableau_coord np.array((nbr_pt_par_pli x nbr_pli, 1, 3))
            tableau possédant les coordonées 3D (donné par la profondeur du tableau) de chaque point du brin.
        hauteur_grid : np.array((nbr_pt_par_pli x nbr_pli, 1, 3))
            tableau possédant l'ordonnée de chaque point de la section.
        largeur_grid : np.array((nbr_pt_par_pli x nbr_pli, 1, 3))
            tableau possédant l'abscisse de chaque point de la section.

        """
        offset = 0.00001
        nb_pt_largeur = 1 # On intègre sur un brin
        nbr_pt_g = 2
        
        H = self.Empilement.get_ep_emp() / 2 - offset
        largeur = self.Empilement.largeur - offset
        
        # largeur_table = np.linspace(-largeur/2, largeur/2, nb_pt_largeur) ## n-> 5
        largeur_table = np.array([0])
        
        # Plusieurs types de tableau
        # hauteur_table = np.linspace(-H, H, n) # n valeurs réparties uniformément adns la hauteur
        hm = -H
        hauteur_table = np.zeros(len(self.Empilement.liste_de_pli)*nbr_pt_g) # une hauteur par pli
        k = 0
        while k < len(self.Empilement.liste_de_pli):
            for i in range(nbr_pt_g):
                hauteur_table[k*nbr_pt_g+i] = hm + (i+1)*(self.Empilement.liste_de_pli[k].props["ep"]/(nbr_pt_g+1))
            hm += self.Empilement.liste_de_pli[k].props["ep"]
            k += 1
        
        # Create coordinate grids
        hauteur_grid, largeur_grid= np.meshgrid(hauteur_table, largeur_table, indexing='ij')
        
        # On crée un tableau contenant les plis pour chaque hauteur (désigné par l'indice)
        self.pli_dans_section = np.zeros((np.shape(hauteur_grid)[0],1), dtype = object)
        for k in range(np.shape(hauteur_grid)[0]):
            self.pli_dans_section[k] = self.cherche_pli([0,0,hauteur_grid[k,0]])
        
        # Stack the grids to create a 3D array
        return np.stack([np.zeros_like(largeur_grid), largeur_grid, hauteur_grid], axis=-1), hauteur_grid, largeur_grid

    def get_rigidite_angle(self):
        """
        Calcule la rigidité de l'empilement.

        Returns:
        --------
        L_section : np.array((8,8))
            Matrice de rigidité de l'empilement
        """
        return self.Empilement.L_section[0]

    def def_gen(self, emp_dir_sol, eff_gen):
        """
        Inverse la relation de comportement

        Parameters
        ----------
        eff_gen : np.array((6,6)): 
            effort généralisé. np.array([N11, N22, N12, M11, M22, M12, Q1, Q2])
        
        emp_dir_sol : float
            empilement dans la direction de l'effort généralisé.

        Returns:
        --------
        def_gen : np.array((1,6))
            déformation généralisée. np.array([e11, e22, e12, k11, k22, k12, gam1, gam2])
            
        """
        # print(emp_dir_sol, eff_gen)
        
        return np.linalg.solve(emp_dir_sol, eff_gen)

    def def_memb_cour(self, def_gen):
        """
        Déformations de membrane et de courbure à partir des déformations généralisées

        Parameters
        ----------
        def_gen : np.array((1,8))
            np.array([e11, e22, e12, k11, k22, k12, gam1, gam2])

        Returns:
        --------
        def_memb : np.array((1,3))
            déformation de membrane
            
        def_courb : np.array((1,3))
            déformation de courbure
            
        def_cis : np.array((1,2))
            déformation de cisaillement
        """
        ind_memb_plaque = [[0,3]]   # e11, e22, e12
        ind_courb_plaque = [[3,6]]  # k11, k22, k12
        ind_cis_plaque = [[6,8]]    # gamma1, gamma2

        
        # Faire une condition pour choisir le bon tableau dans le cas des plaques
        ind_memb = ind_memb_plaque
        ind_courb = ind_courb_plaque
        ind_cis = ind_cis_plaque
        
        def_memb = np.concatenate([def_gen[start:end] for start, end in ind_memb])
        def_courb = np.concatenate([def_gen[start:end] for start, end in ind_courb])
        def_cis = np.concatenate([def_gen[start:end] for start, end in ind_cis])
            
        return def_memb, def_courb, def_cis

    def def_loc(self, eff_gen, coord):
        """
       Calcul la déformation localisée en fonction de l'effet généralisé.

        Parameters
        ----------
        eff_gen : np.array((1,8))
            déformation généralisée.
        
        coord : np.array((1,3))
            coordonnées

        Returns:
        --------
        def_loc_struct : np.array((1,5))
            déformation localisée dans les axes de la structure np.array([eps1, eps2, eps4, eps5, eps6])
            
        def_loc_pli : np.array((1,5))
            déformation localisée dans les axes du pli
        """
        emp_dir_sol = self.get_rigidite_angle() # Matrice de rigidité de l'empilement dans la direction de sollicitation
        def_gen = self.def_gen(emp_dir_sol, eff_gen) # On calcul les déformations généralisées en inversant la relation 5.50
        def_memb, def_courb, def_cis = self.def_memb_cour(def_gen) # On récupère les déformations de membrane et de courbure et de cisaillement
        def_loc_struct = def_memb + coord[2]*def_courb # on applique la cinématique 5.123, coord[2] = x3

        # On calcule les valeurs dans les axes du pli        
        pli = self.cherche_pli(coord)
        eps1, eps2, eps4, eps5, eps6 = self.T_eps(def_loc_struct, def_cis, -pli.orientation)
        def_loc_pli = np.array([eps1, eps2, eps6, eps4, eps5])
        
        return np.concatenate((def_loc_struct, def_cis), axis=0), def_loc_pli

    def cherche_pli(self, coord):
        """
        Cherche un pli en fonction des coordonnées.

        Parameters
        ----------
        coord : np.array((1,3)) ou int
        si coord est un entier, il représente l'indice en ordonnée du pli dans le tableau self.pli_dans_section

        Returns:
        --------
        Pli : Pli
        
        """
        if isinstance(coord, int):
            return self.pli_dans_section[coord]
        else:
            H = self.Empilement.get_ep_emp() / 2
            altitude_souhaitee = coord[2]
            hm = -H
            hM = -H
            for k in range(len(self.Empilement.liste_de_pli)):
                hM += self.Empilement.liste_de_pli[k].props["ep"]
                # print(f'k:{k}, H-hM:{H - hM},  H - hm:{H - hm}, alt = {altitude_souhaitee}')
                if hm <= altitude_souhaitee and altitude_souhaitee <= hM:
                    return self.Empilement.liste_de_pli[k]
                else:
                    hm = hM
            return None
        
    #P Thomas 12/11 renvoyer indice avec coordonnes
    def cherche_indice_pli(self, coord):
        """
        Cherche un pli en fonction des coordonnées.

        Parameters
        ----------
        coord : np.array((1,3)) ou int
        si coord est un entier, il représente l'indice en ordonnée du pli dans le tableau self.pli_dans_section

        Returns:
        --------
        Pli : Pli
        
        """
        if isinstance(coord, int):
            return self.pli_dans_section[coord]
        else:
            H = self.Empilement.get_ep_emp() / 2
            altitude_souhaitee = coord[2]
            hm = -H
            hM = -H
            for k in range(len(self.Empilement.liste_de_pli)):
                hM += self.Empilement.liste_de_pli[k].props["ep"]
                # print(f'k:{k}, H-hM:{H - hM},  H - hm:{H - hm}, alt = {altitude_souhaitee}')
                if hm <= altitude_souhaitee and altitude_souhaitee <= hM:
                    return k+1
                else:
                    hm = hM
            return None
        
        
    def Q_L(self, Pli):
        '''
        
        Parameters
        ----------
        Pli : Pli

        Returns
        -------
        Lcp_temp : np.array(4)
            Q et L (voir relation 5.123, comportement d'un pli avec cisaillement transverse')

        '''
        Lp11, Lp55, Lp66, Lp16, Lp12, Lp22, Lp26, Lp44, Lp45 = Pli.Lcp_oriente
        return np.array([
            [Lp11, Lp12, Lp16],
            [Lp12, Lp55, Lp26],
            [Lp16, Lp26, Lp66]]), np.array([[Lp44, Lp45],[Lp45, Lp55]])
    
    def T_eps(self, eps, eps_cis, orientation):
        """
        Parameters
        ----------
        eps : np.array((1,3)) 
            eps1, eps2, eps6
        
        eps : np.array((1,2)) 
            eps4, eps5
            
        orientation : float
            orientation en degré

        Returns
        -------
        eps : np.array((1,5)) 
            eps1, eps2, eps4, eps5, eps6
        """
        theta = m.radians(orientation)
        return np.array([cos(theta)**2 * eps[0] + sin(theta)**2 * eps[1] + sin(theta)*cos(theta) * eps[2],
                         sin(theta)**2 * eps[0] + cos(theta)**2 * eps[1] - sin(theta)*cos(theta) * eps[2],
                         cos(theta)*eps_cis[0] - sin(theta)*eps_cis[1],
                         sin(theta)*eps_cis[0] + cos(theta)*eps_cis[1],
                         (-sin(2*theta)) * eps[0] + sin(2*theta) * eps[1] + (cos(theta)**2-sin(theta)**2) * eps[2]])
     
    def T_sig(self, sig, sig_cis, orientation):
        """
        Parameters
        ----------
        sig : np.array((1,3)) 
            sig1', sig2', sig6', 
            
        sig_cis : np.array((1,2)) 
            sig4', sig5'
            
        orientation : float
            orientation en degré

        Returns
        -------
        sig : np.array((1,5)) 
            sig1, sig2, sig4, sig5, sig6
        """
        theta = m.radians(orientation)
        return np.array([cos(theta)**2 * sig[0] + sin(theta)**2 * sig[1] + sin(2*theta) * sig[2], 
                         sin(theta)**2 * sig[0] + cos(theta)**2 * sig[1] - sin(2*theta) * sig[2], 
                         cos(theta) * sig_cis[0] -sin(theta) * sig_cis[1],
                         sin(theta) * sig_cis[0] +cos(theta) * sig_cis[1],
                         (-sin(theta)*cos(theta)) * sig[0] + sin(theta)*cos(theta) * sig[1] + (cos(theta)**2-sin(theta)**2) * sig[2]])

    def contraintes_loc(self, eff_gen, coord, indice_voigt):
        """
        Calcule les contraintes locales en fonction des coordonnées et de l'effort généralisé et de l'indice de Voigt

        Parameters
        ----------
        eff_gen : np.array((1,6))
            déformation généralisée.

        Returns
        -------
        sig_struct_complet[ind_L_i] : float
            contrainte localisée dans les axes de la structure donnée par l'indice de voigt
            
        sig_pli[ind_L_i] : float
            contrainte localisée dans les axes du pli donnée par l'indice de voigt
        """
        ind_L_i = self.mapping_voigt(indice_voigt)
        
        def_loc_struct, def_loc_pli = self.def_loc(eff_gen, coord)
        
        pli = self.cherche_pli(coord)
        Q, L = self.Q_L(pli)
        
        # Axes structure
        sig_struct = np.dot(Q, def_loc_struct[0:3].T)
        sig_cis_struct = np.dot(L,def_loc_struct[3:5].T)
        # Axes pli
        sig1, sig2, sig4, sig5, sig6 = self.T_sig(sig_struct, sig_cis_struct, -pli.orientation)
        sig_pli = np.array([sig1, sig2, sig6, sig4, sig5])
        sig_struct_complet = np.concatenate((sig_struct, sig_cis_struct), axis=0)
        
        return sig_struct_complet[ind_L_i], sig_pli[ind_L_i], pli
    
    def contraintes_et_def_loc(self, eff_gen, coord, ind_tabl_cherche_pli):
        """
        Calcule les contraintes et déformations locales en fonction des coordonnées et de l'effort généralisé.

        Parameters
        ----------
        eff_gen : np.array((1,6))
            déformation généralisée.
        
        ind_tabl_cherche_pli : int
            si -1, on cherche le pli avec self.cherche_pli sinon c'est l'indice qui désigne le pli stocké dans self.pli_dans_section

        Returns
        -------
        sig_struct : np.array((1,5)) 
            contrainte localisée dans les axes de la structure : sig1, sig2, sig4, sig5, sig6
            
        sig_pli : np.array((1,5)) 
            contrainte localisée dans les axes du pli : sig1, sig2, sig4, sig5, sig6
            
        pli : Pli
            Pli désigné par les coord
            
        def_loc_struct : np.array((1,5)) 
            déformation localisée dans les axes de la structure : eps1, eps2, eps4, eps5, eps6
           
        def_loc_pli : np.array((1,5)) 
            déformation localisée dans les axes du pli : eps1, eps2, eps4, eps5, eps6
        
        """
        
        def_loc_struct, def_loc_pli = self.def_loc(eff_gen, coord)
        
        if ind_tabl_cherche_pli == -1:
            pli = self.cherche_pli(coord)
        else:
            pli = self.pli_dans_section[ind_tabl_cherche_pli,0]    
        
        Q, L = self.Q_L(pli)
        
        # Axes structure
        sig_struct = np.dot(Q, def_loc_struct[0:3].T)
        sig_cis_struct = np.dot(L,def_loc_struct[3:5].T)
        # Axes pli
        sig1, sig2, sig4, sig5, sig6 = self.T_sig(sig_struct, sig_cis_struct, -pli.orientation)
        sig_pli = np.array([sig1, sig2, sig6, sig4, sig5])
        
        return np.concatenate((sig_struct, sig_cis_struct), axis=0), sig_pli, pli, def_loc_struct, def_loc_pli
    
    def contraintes_et_def_section(self, eff_gen, tableau_coord, crit_rupt, mode):
        """
        Calcule les contraintes et déformations dans la section

        Parameters
        ----------
        eff_gen : np.array((1,8))
            déformation généralisée.
            
        tableau_coord : np.array((n,1,3))
        
        crit_rupt : str
            'Contraintes Max' ou 'Tsaï-Wu'
        
        mode : str
            inutil

        Returns
        -------
        contr_section : np.array((n, n, 5))
            Contrainte dans la section, la profondeur correspond aux indices de voigt.
        """
        
        nb_l, nb_c, data  = np.shape(tableau_coord)
        nbr_ind_voigt = 5
        contr_section = np.zeros((nb_l, nb_c, nbr_ind_voigt))
        crit_section = np.zeros((nb_l, nb_c))
        def_section = np.zeros((nb_l, nb_c, nbr_ind_voigt))
        for k in range(nb_l):
            for i in range(nb_c):
                contr_section[k,i,:], liste_contr_pli, pli, def_loc_struct, def_loc_pli = self.contraintes_et_def_loc(eff_gen, tableau_coord[k, i], k)
                liste_rupt_pli = liste_contr_pli[0:3] # sig1, sig2, sig6
                
                for ind_L_i in range(nbr_ind_voigt):
                    contr_pli = liste_contr_pli[ind_L_i]
                    cont_ind_max = 'cont_' + str(self.mapping_L_i_to_voigt(ind_L_i)) + '_max'
                    if abs(contr_section[k,i,ind_L_i]) > abs(self.res_max[cont_ind_max]['axe_struct']['valeur']):
                        self.res_max[cont_ind_max]['axe_struct']['valeur'] = contr_section[k,i,ind_L_i]
                        self.res_max[cont_ind_max]['axe_struct']['coord'] = tableau_coord[k,i]
                    if abs(contr_pli) > abs(self.res_max[cont_ind_max]['axe_pli']['valeur']):
                        self.res_max[cont_ind_max]['axe_pli']['valeur'] = contr_pli
                        self.res_max[cont_ind_max]['axe_pli']['coord'] = tableau_coord[k,i]
                    
                    def_ind_max = 'def_' + str(self.mapping_L_i_to_voigt(ind_L_i)) + '_max'
                    # Recherche du maximum de déformation dans l'axe de la structure
                    if abs(def_loc_struct[ind_L_i]) > abs(self.res_max[def_ind_max]['axe_struct']['valeur']):
                        self.res_max[def_ind_max]['axe_struct']['valeur'] = def_loc_struct[ind_L_i]
                        self.res_max[def_ind_max]['axe_struct']['coord'] = tableau_coord[k, i]
                    # Recherche du maximum de déformation dans l'axe du pli
                    if abs(def_loc_pli[ind_L_i]) > abs(self.res_max[def_ind_max]['axe_pli']['valeur']):
                        self.res_max[def_ind_max]['axe_pli']['valeur'] = def_loc_pli[ind_L_i]
                        self.res_max[def_ind_max]['axe_pli']['coord'] = tableau_coord[k, i]
                    # TODO : retirer le paramètre mode
                    def_section[k,i,ind_L_i] = def_loc_struct[ind_L_i]
                
                calculateurResistance = CalculResistances(pli)
                if crit_rupt == 'Contraintes Max':
                    crit, reserve = calculateurResistance.cont_Max(liste_rupt_pli)
                elif crit_rupt == 'Tsaï-Wu':
                    crit, reserve = calculateurResistance.Tsai_Wu(liste_rupt_pli)
                elif crit_rupt == 'Hill':
                    crit, reserve = calculateurResistance.Hill(liste_rupt_pli)
                                        
                if self.rupture['rupt_max']['crit'] <= crit or self.rupture['rupt_max']['crit'] == 0:
                    self.rupture['rupt_max']['crit'] = crit
                    self.rupture['rupt_max']['coord'] = tableau_coord[k, i]
                    self.rupture['rupt_max']['reserve'] = reserve
                    self.rupture['rupt_max']['ind'] = [k,i]
                    self.rupture['rupt_max']['mode_rupt'] = calculateurResistance.mode_rupture(liste_rupt_pli, crit_rupt)
                crit_section[k,i] = crit
                
        self.rupture['crit_section'] = crit_section
        Utils.stockage("vals_max", self.res_max)
        Utils.stockage("rupture", self.rupture)
        
        return contr_section, def_section
        
    def dessin_section(Contraintes, tableau, largeur_grid, hauteur_grid, indice_voigt, mode): 
        """
        Dessine la déformation ou la contrainte dans la section. Sauvegarde le dessin dans Ressources/images_gen/

        Parameters
        ----------
        tableau : np.array((n, n, 5))
            contrainte dans la section
        largeur_grid : np.array((n, 1))
        hauteur_grid : np.array((n, 1))
        indice_voigt : int
            1,2,4,5,6

        Returns
        -------
        None.
        """
        import materiau as mat
        
        if mode == "def":
            titre = 'Déformation [mm]'
            titre2 = fr"$\varepsilon_{{{indice_voigt}}}$ max quasi nulle : {Contraintes.res_max['def_'+str(indice_voigt)+'_max']['axe_struct']['valeur']:.1e}"
            titre3 = fr"Déformation $\varepsilon_{{{indice_voigt}}}$ dans la section"
            res_max_key = 'def_'
            offset = Contraintes.offset_eps
            chem_abs = r"Ressources/images_gen/figure_plaque_section_def"
        else:
            titre = 'Contrainte [N.mm^-2]'
            titre2 = fr"$\sigma_{{{indice_voigt}}}$ max quasi nulle : {Contraintes.res_max['cont_'+str(indice_voigt)+'_max']['axe_struct']['valeur']:.1e}"
            titre3 = fr"Contrainte $\sigma_{{{indice_voigt}}}$ dans la section"
            res_max_key = 'cont_'
            offset = Contraintes.offset_sig
            chem_abs = r"Ressources/images_gen/figure_plaque_section_contraintes_"

        
        taille_grid = np.shape(largeur_grid)
        gradu_haut = np.linspace(-Contraintes.h, Contraintes.h, int(taille_grid[0]))
        gradu_larg = np.linspace(0, Contraintes.l, int(taille_grid[1]))
        tick_positions_x = np.linspace(0, len(gradu_larg) - 1, Contraintes.nb_grad_x, dtype=int)
        tick_positions_y = np.linspace(0, len(gradu_haut) - 1, Contraintes.nb_grad_y, dtype=int)

        
        fig, ax = plt.subplots(dpi=300)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="50%", pad=0.05)
        # styles de cmap : viridis, plasma, inferno, magma, coolwarm, bwr, hsv, tab10, tab20, tab20b
        max_value = abs(Contraintes.res_max[res_max_key+str(indice_voigt)+'_max']['axe_struct']['valeur'])
        affich_seq = ax.imshow(tableau[:,:,Contraintes.mapping_voigt(indice_voigt)],cmap=plt.cm.bwr, origin='lower', vmin=-max_value, vmax=max_value)
        # affich_seq = ax.imshow(tableau[:,:,Contraintes.mapping_voigt(indice_voigt)],cmap=plt.cm.bwr, origin='lower')
        
        cbar = fig.colorbar(affich_seq, cax = cax)
        cbar.set_label(titre)
        ax.set_xticks(tick_positions_x)
        ax.set_xticklabels(np.round(gradu_larg[tick_positions_x], decimals=2))
        ax.set_yticks(tick_positions_y)
        ax.set_yticklabels(np.round(gradu_haut[tick_positions_y], decimals=2))
        
        # On dessine une croix quand la déformation est presque nulle cf offset_eps
        if abs(Contraintes.res_max[res_max_key+str(indice_voigt)+'_max']['axe_struct']['valeur']) < offset:
            ax.set_title(titre2, pad=15)
            ax.plot([0, len(gradu_larg) - 1], [0, len(gradu_haut) - 1], color='black', linestyle='-', linewidth=2)
            ax.plot([len(gradu_larg) - 1, 0], [0, len(gradu_haut) - 1], color='black', linestyle='-', linewidth=2)
        else:
            ax.set_title(titre3, pad=15)
            
        ext = r".png"
        chemin = chem_abs + str(indice_voigt) + ext
        fig.savefig(mat.chemin_pour_sphinx(chemin), bbox_inches="tight")
        fig.tight_layout()
        plt.close(fig)

        
    def mapping_voigt(self, indice_voigt):
        if indice_voigt == 1:
            ind_L_i = 0
        elif indice_voigt == 2:
            ind_L_i = 1
        elif indice_voigt == 4:
            ind_L_i = 3
        elif indice_voigt == 5:
            ind_L_i = 4
        elif indice_voigt == 6:
            ind_L_i = 2
        return ind_L_i
    
    def mapping_L_i_to_voigt(self, indice_tab):
        if indice_tab == 0:
            ind_voigt = 1
        elif indice_tab == 1:
            ind_voigt = 2
        elif indice_tab == 2:
            ind_voigt = 6
        elif indice_tab == 3:
            ind_voigt = 4
        elif indice_tab == 4:
            ind_voigt = 5
        return ind_voigt

