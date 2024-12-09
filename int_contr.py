# from tests_manu import emp_pan, T300_914_pli_0, T300_914_emp0_bis
from utils import np, tk, ttk, Image, ImageTk

import Contraintes as cont
import interface as interface
from CalculResistances import CalculResistances


class Int_contr:
    def __init__(self, Empilement):
        self.empilement = Empilement
        self.l = self.empilement.largeur/2
        self.h = self.empilement.get_ep_emp()/2
        
        root = tk.Tk()
        self.root = root
        root.title("Calculs de contrainte et de rupture")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window_width = root.winfo_screenwidth()
        self.window_height = root.winfo_screenheight()
        # Calculate the position for the window to be centered
        self.x_coordinate = 0
        self.y_coordinate = 0
        # Set the geometry of the window to center it
        root.geometry(f"{self.window_width}x{self.window_height}+{int(self.x_coordinate)}+{int(self.y_coordinate)}")
        
        self.window_width = self.root.winfo_screenwidth()
        self.window_height = self.root.winfo_screenheight()
        self.champs_height = 21
        self.champs_moy_width = 143
        self.champs_petit_width = 13
        
        self.taille_image = 199
        
        self.table_width = self.window_width / 6
        self.col_width = int(self.table_width / 6)
        self.table_height = 90
        self.updated_height = 227
        
        self.indices_voigt = [1, 5, 6]
        self.nb_pt_pr_aff = 40

        # Legend for the boxes
        x, y = self.position_pr_aff("moy_champs", 0)
        nom_coef = tk.Label(self.root, text=f"Effort en [N]")
        nom_coef.place(x = x, y = y)
        # Six Entry Boxes
        self.entry_widgets = []
        noms_eff_gen = ['N', 'Mt', 'Mf2', 'Mf3', 'T2', 'T3'] 
        for i in range(0, 6):
            x, y = self.position_pr_aff("moy_champs", 2*i+1)
            x1, y1 = self.position_pr_aff("moy_champs", 2*i+2)
            nom_coef = tk.Label(root, text=f"{noms_eff_gen[i]}")
            nom_coef.place(x = x, y = y)
            val_ef_gen = tk.Entry(self.root)
            val_ef_gen.insert(0, "0")
            self.entry_widgets.append(val_ef_gen)
            val_ef_gen.place(x = x1, y = y1)
        
        # On place l'image de l'empilement à côté de efforts
        self.Set_image_init('dess_emp')
        self.Set_image_init('plaque_eff')
        
        # Champs pour Y and Z
        x, y = self.position_pr_aff("petit_champs", 13)
        y_champs = tk.Label(text="x2")
        y_champs.place(x = x, y = y)
        x, y = self.position_pr_aff("petit_champs", 15)
        z_champs = tk.Label(text="x3")
        z_champs.place(x = x, y = y)
        x, y = self.position_pr_aff("petit_champs", 45)
        y_enca = tk.Label(text=f" -{self.l} < x2 < +{self.l}")
        y_enca.place(x = x, y = y)
        x, y = self.position_pr_aff("petit_champs", 46)
        z_enca = tk.Label(text=f"-{self.h:.1e} < x3 < +{self.h:.1e}")
        z_enca.place(x = x, y = y)
        x, y = self.position_pr_aff("moy_champs", 14)
        self.y_entree = tk.Entry(self.root)
        self.y_entree.insert(0, "0")
        self.y_entree.place(x = x, y = y)
        x, y = self.position_pr_aff("moy_champs", 16)
        self.z_entree = tk.Entry(self.root)
        self.z_entree.insert(0, "0")
        self.z_entree.place(x = x, y = y)


        # Dropdown Menu
        options = ["Contraintes Max", "Tsaï-Wu"]
        self.dropdown_var = tk.StringVar()
        self.dropdown_var.set(options[0])
        self.dropdown_menu = ttk.Combobox(values=options, textvariable=self.dropdown_var)
        x, y = self.position_pr_aff("moy_champs", 17)
        self.dropdown_menu.place(x = x, y = y)

        # Update Button
        x, y = self.position_pr_aff("moy_champs", 19)
        maj_bouton = tk.Button(text="Mettre à jour", command=self.update_values)
        maj_bouton.place(x = x, y = y)
        
        self.root.mainloop()
    
    def update_values(self):
        # On récupère les données utiles et on initialise les champs
        critere_rupture = self.dropdown_var.get()
        eff_gen = []
        for k in range(len(self.entry_widgets)):
            eff_gen.append(float(self.entry_widgets[k].get()))
        coord = [0, float(self.y_entree.get()), float(self.z_entree.get())]
        val = []
        val_pli = []
        val_max = []
            
        self.calculateur_cont = cont.CalculContraintes(self.empilement)
        
        # On calcul les propriétés
        tableau_coord, hauteur_grid, largeur_grid = self.calculateur_cont.tableau_coord(self.nb_pt_pr_aff)
        contraintes_section, def_section = self.calculateur_cont.contraintes_et_def_section(eff_gen, tableau_coord, critere_rupture, 'total')
        for indice_voigt in self.indices_voigt:
            sig_struct, sig_pli, pli = self.calculateur_cont.contraintes_loc(eff_gen, coord, indice_voigt)
            val.append(sig_struct)
            val_pli.append(sig_pli)
        
        for mode in ['def', 'cont']:
            if mode == 'def':
                tableau = def_section
            else:
                tableau = contraintes_section
            for ind_voigt in [1,5,6]:
                cont.CalculContraintes.dessin_section(self.calculateur_cont, tableau, largeur_grid, hauteur_grid, ind_voigt, mode)
        
        # On affiche les dessins
        img = ['sig_1', 'sig_5', 'sig_6', 'def_1', 'def_5', 'def_6']
        leg = [self.replace_greek_symbols(element) for element in img]
        for i in range(len(img)):
            self.Set_image(img[i])
            
        # On affiche la valeur de la contrainte et de la déformation au point demandé
        def_loc_struct, def_loc_pli = self.calculateur_cont.def_loc(eff_gen, coord)
        val = np.concatenate((val, def_loc_struct), axis= 0)
        val_pli = np.concatenate((val_pli, def_loc_pli), axis= 0)
        self.tableaux('val_ponct_struct', leg, val)
        self.tableaux('val_ponct_pli', leg, val_pli)
        
        # On extrait les valeurs des maximums
        tabl_max = np.zeros((6, 6))
        row_index = 0
        for prefix in ['cont', 'def']:
            for indice_voigt in [1,5,6]:
                key = f'{prefix}_{indice_voigt}_max'
                coord_max_struct = self.calculateur_cont.res_max[key]['axe_struct']['coord']
                coord_max_pli = self.calculateur_cont.res_max[key]['axe_pli']['coord']
                tabl_max[row_index, 0] = self.calculateur_cont.res_max[key]['axe_struct']['valeur']
                tabl_max[row_index, 1:3] = coord_max_struct[1:]
                tabl_max[row_index, 3] = self.calculateur_cont.res_max[key]['axe_pli']['valeur']
                tabl_max[row_index, 4:] = coord_max_pli[1:]
                row_index += 1
        self.tableaux('max_struct', leg, tabl_max)
        self.tableaux('max_pli', leg, tabl_max)
                    
        # On affiche les critères de rupture
        coord_rupt_max = self.calculateur_cont.rupture['rupt_max']['coord']
        tabl_rupt = np.array([self.calculateur_cont.rupture['rupt_max']['crit'], self.calculateur_cont.rupture['rupt_max']['reserve'], coord_rupt_max[1], coord_rupt_max[2]])
        self.tableaux('resistance_struct', img, tabl_rupt)
        CalculResistances.dessin_rupture(largeur_grid, hauteur_grid, self.calculateur_cont.rupture)
        self.Set_image('rupt')
        
    def tableaux(self, type_table, leg, val):
        if type_table == 'val_ponct_struct' or type_table == 'val_ponct_pli' :
            if type_table == 'val_ponct_struct':
                titre = "Valeurs au point choisi (axes structure)"
                pos_titre = 30
                pos_tableau = 31
            else:
                titre = "Valeurs au point choisi (axes pli)"
                pos_titre = 35
                pos_tableau = 36
            title_label = tk.Label(self.root, text=titre)
            x, y = self.position_pr_aff("moy_champs", pos_titre)
            title_label.place(x=x, y=y)
            columns = ('Cont_leg', 'Cont_val', 'def_leg', 'def_val')

            self.tree = ttk.Treeview(self.root, columns=columns, show='headings')

            # define headings
            self.tree.heading('Cont_leg', text='σ')
            self.tree.heading('Cont_val', text='Valeur')
            self.tree.heading('def_leg', text='ε')
            self.tree.heading('def_val', text='Valeur')

            data = [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
            for k in range(len(leg)//2):
                data[k % 3][0] = leg[k]
                if val[k] != 0:
                    data[k % 3][1] = f"{val[k]:.1e}" # round(val[k], 2) 
                else:
                    data[k % 3][1] = "0"
                data[k % 3][2] = leg[k + 3]
                if val[k+3] != 0:
                    data[k % 3][3] = f"{val[k+3]:.1e}" # round(val[k], 2) 
                else:
                    data[k % 3][3] = "0"
            for row in data:
                self.tree.insert('', 'end', values=row)
                
            for col in self.tree["columns"]:
                    self.tree.column(col, width=self.col_width)
                
            x, y = self.position_pr_aff("moy_champs", pos_tableau)
            self.tree.place(x=x, y=y, width=self.table_width, height=self.table_height)
            
        elif type_table == 'max_struct' or type_table == 'max_pli':
            if type_table == 'max_struct':
                titre = "Maximums (axes structure)"
                pos_titre = 32
                pos_tableau = 33
                offset = 0
            else:
                titre = "Maximums (axes pli)"
                pos_titre = 37
                pos_tableau = 38
                offset = 3
            title_label = tk.Label(self.root, text=titre)
            x, y = self.position_pr_aff("moy_champs", pos_titre)
            title_label.place(x=x, y=y)
            columns = ('Légende', 'Valeur', 'x2', 'x3')

            self.tree = ttk.Treeview(self.root, columns=columns, show='headings')

            # define headings
            self.tree.heading('Légende', text='σ, ε')
            self.tree.heading('Valeur', text='Valeur')
            self.tree.heading('x2', text='x2')
            self.tree.heading('x3', text='x3')


            data = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
            nb_l, nb_c = np.shape(data)
            for i in range(nb_l):
                data[i][0] = leg[i]
                if val[i,offset] != 0:
                    data[i][1] = f"{val[i,offset]:.1e}" # round(val[k], 2) 
                else:
                    data[i][1] = "0"
                if val[i,offset + 1] != 0:
                    data[i][2] = f"{val[i,offset + 1]:.1e}" # round(val[k], 2) 
                else:
                    data[i][2] = "0"
                if val[i,offset + 2] != 0:
                    data[i][3] = f"{val[i,offset + 2]:.1e}" # round(val[k], 2) 
                else:
                    data[i][3] = "0"
            for row in data:
                self.tree.insert('', 'end', values=row)
                
            for col in self.tree["columns"]:
                    self.tree.column(col, width=self.col_width)
                
            x, y = self.position_pr_aff("moy_champs", pos_tableau)
            self.tree.place(x=x, y=y, width=self.table_width, height=1.7 * self.table_height)
            
        elif type_table == 'resistance_struct' or type_table == 'resistance_pli':
            if type_table == 'resistance_struct':
                titre = "Critère de rupture max (axes pli)"
                pos_titre = 39
                pos_tableau = 40
                offset = 0
            else:
                titre = "Critère de rupture (axes pli)"
                pos_titre = 37
                pos_tableau = 38
                offset = 3
            title_label = tk.Label(self.root, text=titre)
            x, y = self.position_pr_aff("moy_champs", pos_titre)
            title_label.place(x=x, y=y)
            x, y = self.position_pr_aff("petit_champs", 50)
            z_enca = tk.Label(text=f"{self.calculateur_cont.rupture['rupt_max']['mode_rupt']['nom_rupt']} = {self.calculateur_cont.rupture['rupt_max']['mode_rupt']['val_rupt_pli']:.2e}") 
            z_enca.place(x = x, y = y)
            columns = ('Critère', 'Réserve', 'x2', 'x3', 'ind_pli')

            self.tree = ttk.Treeview(self.root, columns=columns, show='headings')

            # define headings
            self.tree.heading('Critère', text='Critère')
            self.tree.heading('Réserve', text='Réserve')
            self.tree.heading('x2', text='x2')
            self.tree.heading('x3', text='x3')
            self.tree.heading('ind_pli', text='ind_pli')

            data = [[0,0,0,0,0]]
            nb_l, nb_c = np.shape(data)
            for i in range(nb_l):
                if val[0] != 0:
                    data[i][0] = f"{val[0]:.1e}" # round(val[k], 2) 
                else:
                    data[i][0] = "0"
                if val[1] != 0:
                    data[i][1] = f"{val[1]:.1e}" # round(val[k], 2) 
                else:
                    data[i][1] = "0"
                if val[2] != 0:
                    data[i][2] = f"{val[2]:.1e}" # round(val[k], 2) 
                else:
                    data[i][2] = "0"
                if val[3] != 0:
                    data[i][3] = f"{val[3]:.1e}" # round(val[k], 2) 
                else:
                    data[i][3] = "0"
                indice_pli=self.calculateur_cont.cherche_indice_pli([0,0,val[3]])
                data[i][4]= str(indice_pli)
            for row in data:
                self.tree.insert('', 'end', values=row)
                
            for col in self.tree["columns"]:
                    self.tree.column(col, width=self.col_width)
                
            x, y = self.position_pr_aff("moy_champs", pos_tableau)
            self.tree.place(x=x, y=y, width=self.table_width, height=2/3 * self.table_height)
        
    def position_pr_aff(self, taille, pos):
        if taille == "petit_champs":
            largeur = self.champs_petit_width
            hauteur = self.champs_height
        elif taille == "moy_champs":
            largeur = self.champs_moy_width
            hauteur = self.champs_height
        elif taille == "image":
            largeur = self.taille_image
            hauteur = self.taille_image
        else:
            largeur, hauteur = taille
            
        width = self.window_width
        height = self.window_height
        ta = self.taille_image
        offset = 70

        # -------------------------------------------
        #   1  | 2    |43  |              |       |       | 
        #   3  | 4         |     20       |   21  |  22   | 
        #   5  | 6         |              |       |       | 
        #   7  | 8         |              |       |       | 
        #   9  | 10        |     23       |   24  |  25   | 
        #   11 | 12   
        
        #         44      |              |       |       | 
        # -------------------------------------------
        # 13 | 14| 15 | 16 |      26      |  27   |   28  | 
        #     17           |     29       |   30 |  31   | 
        #                  |-------------------------------
        #     18           |              |       |       | 
        #     19
        # -------------------------------------------

        x, y = 0, 0
        incr_part_hg = (height/2 - 6*hauteur)/ 7
            
        if pos == -1 or pos == 1 or pos == 3 or pos == 5 or pos == 7 or pos == 9 or pos == 11 or pos == 44:
            x = 0
        elif pos == 0 or pos == 2 or pos == 4 or pos == 6 or pos == 8 or pos == 10 or pos == 12:
            x = (width/4 - 2*largeur)/3
        elif pos == 43:
            x = width/8
        if pos == 1 or pos == 2:
            y = hauteur #incr_part_hg
        elif pos == -1 or pos == 0 or pos == 43:
            y = 0
        elif pos == 3 or pos == 4:
            y = hauteur * 2#incr_part_hg * 2 + hauteur
        elif pos == 5 or pos == 6:
            y = hauteur * 3#incr_part_hg * 3 + hauteur * 2
        elif pos == 7 or pos == 8:
            y = hauteur * 4#incr_part_hg * 4 + hauteur * 3
        elif pos == 9 or pos == 10:
            y = hauteur * 5#incr_part_hg * 5 + hauteur * 4
        elif pos == 11 or pos == 12:
            y = hauteur * 6#incr_part_hg * 6 + hauteur * 5
        elif pos == 44:
            y = height/4#incr_part_hg * 6 + hauteur * 5
                
        incr_part_bg = (height/2 - 4*hauteur)/ 5
        incr_part_bg_larg = width/4 - 2*self.champs_petit_width - 2*self.champs_moy_width
        if pos == 13:
            x = incr_part_bg_larg/5
        elif pos == 14 or pos == 45:
            x = 2 * incr_part_bg_larg/5 + self.champs_petit_width
        elif pos == 15:
            x = 3 * incr_part_bg_larg/5 + self.champs_petit_width + self.champs_moy_width
        elif pos == 16 or pos == 46:
            x = 4 * incr_part_bg_larg/5 + 2 * self.champs_petit_width + self.champs_moy_width
        elif pos == 17 or pos == 18 or pos == 19:
            x = (width/4 - largeur)/2
        if pos == 13 or pos == 14 or pos == 15 or pos == 16:
            y = height*3/4
        elif pos == 17:
            y = height*3/4 + 2 * hauteur
        elif pos == 18:
            y = height*3/4 + 4 * hauteur
        elif pos == 19:
            y = height*3/4 + 4 * hauteur
        elif pos == 45 or pos == 46:
            y = height*3/4 +  hauteur
    
        # -------------------------------------------
        #   1  | 2 |43     |              |       |       | 
        #   3  | 4         |     20       |   21  |  22   | 
        #   5  | 6         |              |       |       | 
        #   7  | 8         |              |       |       | 
        #   9  | 10        |     23       |   24  |  25   | 
        #   11 | 12        |              |       |       | 
        # -------------------------------------------
        # 13 | 14| 15 | 16 |      26      |      27       |
        #     17           |      28      |      29       | 
        #                  |-------------------------------
        #     18           |              |       |       | 
        #     19           |
        # -------------------------------------------
        incr_part_hd_haut = (height/2 - 2*ta)/3
        incr_part_hd_larg = (width*3/4 - 3*ta)/4
        
        if pos == 20 or pos == 21 or pos == 22:
            y = incr_part_hd_haut
        elif pos == 23 or pos == 24 or pos == 25:
            y = incr_part_hd_haut * 2 + hauteur
        if pos == 20 or pos == 23:
            x = width/4 + incr_part_hd_larg
        elif pos == 21 or pos ==  24:
            x = width/4 + incr_part_hd_larg * 2 + largeur
        elif pos == 22 or pos == 25:
            x = width/4 + incr_part_hd_larg * 3 + 2 * largeur
            
        incr_part_milieud_haut = (height/4 - 2*hauteur)/ 3
        incr_part_milieud_larg = (width*3/4 - 2*largeur)/ 3
        if pos == 26 or pos == 28:
            x = width/4 + incr_part_milieud_larg
        elif pos == 27 or pos ==  29:
            x = width/4 + incr_part_milieud_larg * 2 + largeur
        if pos == 26 or pos == 27:
            y = height/2 + incr_part_milieud_haut
        elif pos == 28 or pos == 29:
            y = height/2 + 2 * incr_part_milieud_haut + hauteur
            
        # -------------------------------------------
        # 13 | 14| 15 | 16 |       30      |    35       |   39
        #     17           |       31      |    36       |   40
        #                                                    45
        #                  |       32      |    37       |   41
        #     18           |       33      |    38       |   42
        #     19           |       34      |           | 
        # -------------------------------------------
        incr_part_milieu_bas = (width/2 - largeur)/2
        incr_part_milieu_bas_haut = (width/2 - 3*self.champs_height -2*self.table_height)/6
        if pos == 30 or pos == 32 or pos == 34:
            x = width/12 + incr_part_milieud_larg # width/4
        elif pos == 31 or pos == 33:
            x = width/4
        elif pos == 35 or pos == 36 or pos == 37 or pos == 38:
            x = width/2
        elif pos == 39 or pos == 40 or pos == 41 or pos == 42 or pos == 50:
            x = width*3/4
        if pos == 30 or pos == 35 or pos == 39:
            y = height/2 #+ incr_part_milieu_bas_haut
        elif pos == 31 or pos == 36 or pos == 40:
            y = height/2 + height/20# height/2 + 2 * incr_part_milieu_bas_haut + self.champs_height - offset
        elif pos == 32 or pos == 37 or pos == 41:
            y =  height*3/4 - height/12 #height/2 + 3 * incr_part_milieu_bas_haut + self.champs_height + self.updated_height - offset
        elif pos == 33 or pos == 38:
            y = height*3/4 + height/20 - height/12#height/2 + 4 * incr_part_milieu_bas_haut + 2 * self.champs_height + self.updated_height - offset
        elif pos == 34:
            y = height/2 + 5 * incr_part_milieu_bas_haut + 2 * self.champs_height + 2 * self.updated_height - offset
        elif pos == 50:
            y =  height*3/4 - height/12 - height/20       
        
        return x, y
    
    def on_close(self):
        empilement = self.empilement
        self.root.destroy()
        aj = interface.int_gra(empilement.liste_de_pli, empilement.largeur)
        
    def Set_image(self, figure):
        resampling_filter = Image.LANCZOS
        largeur_max = self.window_width/3 - 30
        figure_mapping = {
            'sig_1': (20, 'Ressources/images_gen/figure_section_contraintes_1.png'),
            'sig_5': (21, 'Ressources/images_gen/figure_section_contraintes_5.png'),
            'sig_6': (22, 'Ressources/images_gen/figure_section_contraintes_6.png'),
            'def_1': (23, 'Ressources/images_gen/figure_section_def1.png'),
            'def_2': (24, 'Ressources/images_gen/figure_section_def5.png'),
            'def_3': (25, 'Ressources/images_gen/figure_section_def6.png'),
            'rupt': (41, 'Ressources/images_gen/figure_section_rupture.png'),
            }
        
        for figure, (label_number, image_path) in figure_mapping.items():
            #P Thomas ajout de la contrainte pour etirer l'image rupt
            if figure != 'rupt':
                x, y = self.position_pr_aff("image", label_number)
                image_ind = Image.open(image_path)
                image_ind = image_ind.resize((self.taille_image, self.taille_image), resampling_filter)
                photo = ImageTk.PhotoImage(image_ind)
                setattr(self, f'photo_{figure}', photo)
                label = tk.Label(image=photo).place(x=x, y=y)
            else:
                x, y = self.position_pr_aff("image", label_number)
                image_ind = Image.open(image_path)
                image_ind = image_ind.resize((self.taille_image, int(1.4*self.taille_image)), resampling_filter)
                photo = ImageTk.PhotoImage(image_ind)
                setattr(self, f'photo_{figure}', photo)
                label = tk.Label(image=photo).place(x=x, y=y)
                
    def Set_image_init(self, figure):
        resampling_filter = Image.LANCZOS
        largeur_max = self.window_width/3 - 30
        if figure == 'dess_emp':
            self.empilement.Dessin_pli('') # On met à jour le graphique de la section
            image_0 = Image.open("Ressources/images_gen/dessin_empilement.jpeg")
            width, height = image_0.size
            new_height = 200
            new_width = int((new_height * width) / height)
            image_0 = image_0.resize((new_width, new_height), resampling_filter)
            self.photo_0 = ImageTk.PhotoImage(image_0)
            width, height = image_0.size
            x, y = self.position_pr_aff(image_0.size, 43)
            self.label_0 = tk.Label(image=self.photo_0)
            self.label_0.place(x = x, y = y)
        elif figure == 'plaque_eff':
            image_1 = Image.open("Ressources/images_fixes/poutre_efforts.png")
            width, height = image_1.size
            new_height = int(self.window_width/4)
            new_width = int((new_height * width) / height)
            image_1 = image_1.resize((new_width, new_height), resampling_filter)
            self.photo_1 = ImageTk.PhotoImage(image_1)
            width, height = image_1.size
            x, y = self.position_pr_aff(image_1.size, 44)
            self.label_1 = tk.Label(image=self.photo_1)
            self.label_1.place(x = x, y = y)
            
    def replace_greek_symbols(self, input_string):
        # Replace 'sig_' with Greek letter sigma (σ)
        input_string = input_string.replace('sig_', 'σ')
    
        # Replace 'def_' with Greek letter epsilon (ε)
        input_string = input_string.replace('def_', 'ε')
    
        return input_string

if __name__ == "__main__":
    app = Int_contr() # T300_914_emp0_bis, emp_pan
    # app = Int_contr(emp_pan) # T300_914_emp0_bis, emp_pan
    
