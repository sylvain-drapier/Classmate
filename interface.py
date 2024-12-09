0# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 17:28:35 2023

@author: lbonn
"""
import sys
import os
# sys.path.append(r'C:\Users\33645\Documents\Mines3A\Projet_industriel\Classmate')
# os.chdir(r'C:\Users\33645\Documents\Mines3A\Projet_industriel\Classmate')
# =============================================================================
# Décommenter les plt.close dans chaque fonctions d'affichage des scripts pour 
# empêcher la génération des images utilisées dans l'interface
# CalculResistances, Contraintes, Contraintes_plaques, materiau
# =============================================================================
from utils import Utils, m, showerror, showinfo, filedialog, os, tk, ttk, Image, ImageTk

import int_contr as ic
import int_contr_plaque as icp
import materiau as mat

Mat_map = mat.Mat_map
Mat_map_plaque = mat.Mat_map_plaque
Dict_mat = mat.Dict_mat



###############################################################################
class InterfaceChoixStructure:
    def __init__(self):
        self.on_button_click()
    
    def on_button_click(self):
        self.root = tk.Tk()
        self.root.title("Choix structure")
        self.root.geometry("150x110+{}+{}".format(int(self.root.winfo_screenwidth()/2 - 150), int(self.root.winfo_screenheight()/2 - 100)))
        
        button_labels = ['Pli unique', 'Poutre stratifiée', 'Plaque stratifiée']
        button_commands = [self.creat_pli, self.creat_poutre_strat, self.creat_plaque_strat]
        
        for label, command in zip(button_labels, button_commands):
            tk.Button(self.root, text=label, command=command).pack(pady=5)
            
        self.root.mainloop()
    
    def creat_pli(self):
        self.root.destroy()
        root = tk.Tk()
        InterfaceInitialisationSequence(root, "Pli", [], '', 0)
        
    def creat_poutre_strat(self):
        Utils.plaque = 0
        self.root.destroy()
        root = tk.Tk()
        InterfaceInitialisationSequence(root, "Initialisation", [], '', 0)
        
    def creat_plaque_strat(self):
        self.root.destroy()
        Utils.plaque = 1
        root = tk.Tk()
        InterfaceInitialisationSequence(root, "Initialisation", [], '', 0)
        



###############################################################################
class InterfaceInitialisationSequence:
    def __init__(self, root, Mode, seq, chemin, largeur):
        self.root = root
        self.Mode = Mode # "Initialisation", "Ajout", "Retrait"
        self.seq = seq
        self.chemin = chemin
        self.largeur_val = largeur
        self.mode_pli = ""

        if Mode == "Initialisation" or Mode == "Pli":
            Mode2 = self.Mode = "Initialisation"
            if Mode == "Pli":
                self.mode_pli = "Pli"
        else:
            Mode2 = None
        
        # titre = texte =  ''
        if Mode2 == "Initialisation":
            titre = "Initialisation de la séquence"
            texte = "Nombre de plis"
        elif Mode == "Ajout":
            titre = "Ajout de plis"
            texte = "Nombre de plis à ajouter"
        elif Mode == "Retrait":
            titre = "Retrait de plis"
            texte = "Nombre de plis à retirer"
        root.title(titre)
        window_width = 300
        if Mode2 == "Initialisation":
            window_height = 160
        else:
            window_height = 70
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (window_width / 2)
        y_coordinate = (screen_height / 2) - (window_height / 2)
        root.geometry(f"{window_width}x{window_height}+{int(x_coordinate)}+{int(y_coordinate)}")

        # Créer et placer une étiquette pour le champ "Nombre de pli"
        self.etiquette = tk.Label(root, text=texte)
        self.etiquette.pack()
        # Créer un champ de saisie pour que l'utilisateur entre un nombre
        self.champ_saisie = tk.Entry(root)
        if Mode == "Pli":
            self.champ_saisie.insert(0, "1")
            self.champ_saisie.config(state="readonly")
        self.champ_saisie.pack()
        
        if Mode2 == "Initialisation": 
            # Créer et placer une étiquette pour le champ "Largeur"
            self.largeur = tk.Label(root, text='Largeur des plis (mm)')
            self.largeur.pack()
            self.largeur_saisie = tk.Entry(root)
            if Utils.plaque == 1:
                self.largeur_saisie.config(state="readonly")
                self.largeur_saisie.insert(0, "-")
            else:
                self.largeur_saisie.insert(0, "0.1")
            self.largeur_saisie.pack()
            self.select_file_button = tk.Button(root, text="Choisir un fichier excel", command=self.open_file_dialog)
            self.select_file_button.pack(pady=10)

        # Créer un bouton pour continuer
        self.bouton_continuer = tk.Button(root, text="Continuer", command=self.continuer_sequence)
        self.bouton_continuer.pack()
            
        root.mainloop()

    def continuer_sequence(self):
        # Récupérer le nombre de pli saisi par l'utilisateur
        nombre_de_pli = int(self.champ_saisie.get())
        if self.Mode == "Initialisation":
            if Utils.plaque == 0:
                self.largeur_val = float(self.largeur_saisie.get())
            else:
                self.largeur_val =  0
        self.root.destroy()
        if self.mode_pli == "Pli":
            cm = Choixmateriaux(nombre_de_pli, 0, self.mode_pli)
        elif self.Mode == "Initialisation":
            cm = Choixmateriaux(nombre_de_pli, 0, 'Initialisation')
        else:
            cm = Choixmateriaux(nombre_de_pli, dict({'seq' : self.seq, 'largeur' : self.largeur_val}), self.Mode)
        cm.choix()
        seq = cm.seq
        int_gra(seq, self.largeur_val)
            
    def open_file_dialog(self):
        script_directory = os.path.dirname(os.path.abspath(__file__)) + '/Ressources' # Emplacement où s'ouvre l'explorateur de fichier
        seq = tk.filedialog.askopenfilename(initialdir=script_directory, title="Sélectionner un fichier", filetypes=(("Excel files", "*.xlsx"), ("all files", "*.*")))
        if Utils.plaque == 0:
            self.largeur_val = float(self.largeur_saisie.get())
        else:
            self.largeur_val =  0
        self.root.destroy()
        int_gra(seq, self.largeur_val)
        


###############################################################################
class Choixmateriaux:
    
    def __init__(self, nbr_pli, dict_mod, mode):
        self.nbr_pli = nbr_pli
        self.seq = []
        self.mode = mode
        if dict_mod != 0:
            self.dict_mod = dict_mod
            self.seq = dict_mod['seq']
            self.largeur = dict_mod['largeur']
            self.empilement = mat.Empilement(self.seq, self.largeur)
        else:
            self.dict_mod = dict_mod
        
    def choix(self):
        for k in range(self.nbr_pli):
            self.interface_choix_un_mat(k)
            
    def interface_choix_un_mat(self, k):
        def continuer_selection():
            # Récupérer le matériau sélectionné et l'inclinaison saisie
            if self.mode == 'Ajout' or self.mode == 'Retrait':
                indice_du_pli = int(champ_ind_aj.get())-1
                #P Thomas 07/10/24 ajout du -1 et condition
                if self.mode == 'Ajout':
                    if indice_du_pli >= 0 and indice_du_pli < len(self.seq)+1:
                        self.pli_k = mat.Pli(Dict_mat[materiau_selectionné.get()], float(champ_inclinaison.get()), ep = float(etiquette_epaisseur.get()))
                        self.seq = self.seq[:indice_du_pli] + [self.pli_k] + self.seq[indice_du_pli:]
                    else :
                        showerror(title='Error',message="L'indice saisi est incorrect") 
                else:
                    try:
                        self.seq.pop(indice_du_pli)
                    except:
                        showerror(title='Error',message="L'indice saisi est incorrect")   
                # On met à jour les dessins de l'empilement
                self.empilement = mat.Empilement(self.seq, self.largeur)
                self.empilement.Dessin_pli('')
            else:
                self.pli_k = mat.Pli(Dict_mat[materiau_selectionné.get()], float(champ_inclinaison.get()), ep = float(etiquette_epaisseur.get()))
                self.seq.append(self.pli_k)
            root.destroy()
            return
        
        root = tk.Tk()
        root.title(f"Choix du matériau du pli n° {k+1}")  # Remplacez 'n' par le numéro de matériau souhaité
        
        if self.mode == 'Ajout':
            window_width = 600
            window_height = 550
            texte_indice = "Indice i:\n(Le pli sera ajouté entre les plis d'indice i-1 et i)"
        elif self.mode == 'Retrait':
            window_width = 600
            window_height = 400
            texte_indice = "Le pli d'indice i sera retiré"
        else:
            window_width = 300
            window_height = 180
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (window_width / 2)
        y_coordinate = (screen_height / 2) - (window_height / 2)
        root.geometry(f"{window_width}x{window_height}+{int(x_coordinate)}+{int(y_coordinate)}")
        
        if self.mode != 'Retrait':
            #P Thomas ajout du +1 dans n° materiau pour commencer numérotation à 1 dans l'affichage
            label = tk.Label(root, text = f"Choix du matériau n° {k+1}", font = ('Arial', 10, 'underline'))
            label.pack()
            
            # Créer une étiquette pour le menu déroulant
            etiquette_menu = tk.Label(root, text="Matériau:")
            etiquette_menu.pack()
            
            # Créer un menu déroulant avec des options
            options_materiau = list(Dict_mat)
            materiau_selectionné = tk.StringVar()
            menu_deroulant = ttk.Combobox(root, textvariable=materiau_selectionné, values=options_materiau)
            menu_deroulant.pack()
            
            # Créer une étiquette pour le champ "Inclinaison"
            etiquette_inclinaison = tk.Label(root, text="Orientation:")
            etiquette_inclinaison.pack()
            # Créer un champ de saisie pour "Inclinaison"
            champ_inclinaison = tk.Entry(root)
            if self.mode == "Pli":
                champ_inclinaison.insert(0, "0")
            champ_inclinaison.pack()
            
            etiquette_epaisseur = tk.Label(root, text="Epaisseur (mm):")
            etiquette_epaisseur.pack()
            etiquette_epaisseur = tk.Entry(root)
            etiquette_epaisseur.insert(0, "200.E-3")
            etiquette_epaisseur.pack()
        
        if self.dict_mod != 0:
            etiquette_ind_aj = tk.Label(root, text=texte_indice)
            etiquette_ind_aj.pack()
            champ_ind_aj = tk.Entry(root)
            champ_ind_aj.insert(0, "0")
            champ_ind_aj.pack()
            
            image_1 = Image.open("Ressources/images_gen/dessin_empilement.jpeg")
            width, height = image_1.size
            image_1 = image_1.resize((250, 300), Image.NEAREST)
            self.photo_1 = ImageTk.PhotoImage(image_1)
            width, height = image_1.size
            self.label_1 = tk.Label(image=self.photo_1)
            self.label_1.pack()
        
    
        # Créer un bouton pour continuer
        bouton_continuer = tk.Button(root, text="Continuer", command=continuer_selection)
        bouton_continuer.pack()
        
        root.mainloop()
                
        return



###############################################################################
class int_gra:
    
    button_width = 20
    button_height = 1
    checboxes_width = 8
    
    def __init__(self, seq, largeur):
        '''Création du materiau'''
        self.largeur = largeur
        self.empilement = mat.Empilement(seq,largeur)
        self.seq = self.empilement.liste_de_pli
        if len(seq) == 1: # On étudie un pli
            self.L = seq[0].get_L_Inge
        else: # On étudie un empilement
            self.L = self.empilement.L_section
            
        '''Création interface'''
        # On crée la fenêtre principale
        root = tk.Tk()
        self.root = root
        root.title("Graphiques polaire et cartésien")
        self.window_width = root.winfo_screenwidth()
        self.window_height = root.winfo_screenheight()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # Calculate the position for the window to be centered
        self.x_coordinate = 0
        self.y_coordinate = 0
        # Set the geometry of the window to center it
        root.geometry(f"{self.window_width}x{self.window_height}+{int(self.x_coordinate)}+{int(self.y_coordinate)}")
        image = Image.open("Ressources/images_fixes/eenuee_background.png")
        image = image.resize((self.window_width, self.window_height), Image.LANCZOS)  # Adjust the dimensions as per your requirements
        bg = ImageTk.PhotoImage(image)
        label = tk.Label(root, image=bg)
        label.place(x=0, y=0)
        
        self.checkbox_vars = []
        if Utils.plaque:
            self.nbr_coeff = 64
            self.checboxes_width = 5
        else:   
            self.nbr_coeff = 36
            
        for i in range(self.nbr_coeff):
            indice, leg_pli, leg_sec , indice_sec= self.mapper(i)
            if len(seq) == 1:
                legend = leg_pli
            else:
                legend = leg_sec
            self.checkbox_vars.append(tk.IntVar())
            if legend != None:
                if legend == 0:
                    state = tk.DISABLED
                else:
                    state = tk.NORMAL
                tk.Checkbutton(text=f'{legend}', state=state, variable=self.checkbox_vars[i], width=self.checboxes_width).grid(row=i // int(m.sqrt(self.nbr_coeff)), column=i % int(m.sqrt(self.nbr_coeff)), padx=2, pady=2)                
                
        x3, y3 = self.position_pr_aff((self.button_width, self.button_height), 16)
        tk.Button(root, width = self.button_width, text="Mettre à jour les graphes", command=self.calculate_and_update_plots).place(x = x3, y = y3)
        #P Thomas 22/10, retrait des boutons avec ou sans contraintes planes
        # x4, y4 = self.position_pr_aff((self.button_width, self.button_height), 19)
        # tk.Button(root, width = self.button_width, text=f"Correction con.t planes", command=self.int_gra_def_red).place(x = x4, y = y4)
        # x5, y5 = self.position_pr_aff((self.button_width, self.button_height), 21)
        # tk.Button(root, width = self.button_width, text=f"Sans correction cont. planes", command=self.int_gra_def_red_neglige).place(x = x5, y = y5)
        
        
        '''Affichage des courbes initiales'''
        if len(seq) == 1: # On étudie un pli
            self.orientation_sollicitation = 0
            self.Set_image('pol0')
            self.Set_image('cart0')
            self.Set_image('ldc')
        else:
            x1, y1 = self.position_pr_aff((0,0), 14)
            x2, y2 = self.position_pr_aff((0,0), 15)
            x3, y3 = self.position_pr_aff((0,0), 17)
            x4, y4 = self.position_pr_aff((0,0), 18)
            x5, y5 = self.position_pr_aff((0,0), 20)

            tk.Button(root, width = self.button_width, height = self.button_height, text="Retirer un pli", command=self.Retirer).place(x = x1, y = y1)
            tk.Button(root, width = self.button_width, text="Ajouter un pli", command=self.Ajouter).place(x = x2, y = y2)
            tk.Button(root, width = self.button_width, text="Contrainte localisée", command=self.Resistances).place(x = x3, y = y3)
            
            self.orientation_sollicitation = tk.Entry(self.root)
            self.orientation_sollicitation.insert(0, "0")
            self.orientation_sollicitation.place(x=x4, y=y4)
            self.orientation_sollicitation_label = tk.Label(text=f"Orientation de l'axe de structure [°]")
            self.orientation_sollicitation_label.place(x = x5, y = y5)
            
            self.Set_image('dess_emp')
            self.Set_image('section')
            self.Set_image('ldc')
        root.mainloop()
    
    def on_close(self):
        #for key in Utils.obj_to_save:
        #    print(key)
        #    print(Utils.obj_to_save[key])
        Utils.stockage_final()
        self.root.destroy()

    def Ajouter(self):
        self.root.destroy()
        root = tk.Tk()
        aj = InterfaceInitialisationSequence(root, "Ajout", self.seq, 'Ressources/images_gen/dessin_empilement.jpeg', self.largeur)
        
    def Retirer(self):
        self.root.destroy()
        root = tk.Tk()
        aj = InterfaceInitialisationSequence(root, "Retrait", self.seq, 'Ressources/images_gen/dessin_empilement.jpeg', self.largeur)
        
    def Resistances(self):
        self.root.destroy()
        if Utils.plaque == 1:
            aj = icp.Int_contr_plaque(self.empilement)
        else:
            aj = ic.Int_contr(self.empilement)
   
        
    def int_gra_def_red(self):
        Utils.def3_induite = 1
        self.root.destroy()
        int_gra(self.seq, self.largeur)
        
    def int_gra_def_red_neglige(self):
        Utils.def3_induite = 0
        self.root.destroy()
        int_gra(self.seq, self.largeur)
        
                
    def calculate_and_update_plots(self):
        boxes_vides = True
        for i in range(len(self.checkbox_vars)):
            if self.checkbox_vars[i].get() == 1:
                boxes_vides = False
                break
        if not boxes_vides:
            if len(self.seq) == 1:
                selected_checkboxes = []
                for i in range(len(self.checkbox_vars)):
                    indice, leg_pli, leg_sec , indice_sec = self.mapper(i)
                    if self.checkbox_vars[i].get() == 1:
                        if self.mapper(i) != None:
                            selected_checkboxes.append(i)
                self.seq[0].Affichage(True, True, selected_checkboxes, 0)
                self.Set_image('pol')
                self.Set_image('cart')
            else:
                selected_checkboxes = []
                for i in range(self.nbr_coeff):
                    indice, leg_pli, leg_sec, indice_sec = self.mapper(i)
                    if self.checkbox_vars[i].get() == 1:
                        if self.mapper(indice_sec) != None:
                            selected_checkboxes.append(indice_sec)
                            
                self.Set_image('dess_emp')
                self.Set_image('section')
                self.coef_nuls = self.empilement.Affichage_pol_cart(True, True, selected_checkboxes, 0) # On met à jour le graphique de la section
                self.Set_image('pol')
                self.Set_image('cart')
                if not self.coef_nuls:
                    pass
                else:
                    mess = 'Les coefficients suivants sont supposés nuls :\n' + '; '.join(self.coef_nuls)
                    showinfo(title='Info',message=mess)
        
    def position_pr_aff(self, taille, pos):
        largeur, hauteur = taille
        width = self.window_width
        height = self.window_height
        offset = 50
        # Cas un pli
        # -------------------------------------------
        #            |              1               |        
        # -------------------------------------------
        #      3     |              2               | 
        # -------------------------------------------
        if pos == 1:
            return width/3 + (width * 2/3 - largeur)/2, (height/2-hauteur)/2
        elif pos == 2:
            return width/3 + (width * 2/3 - largeur)/2, height/2 + (height/2-hauteur)/2
        elif pos == 3:
            return (width/3-largeur)/2, height/2 + (height/2-hauteur)/2
        # Cas empilements
        # -------------------------------------------
        #      8     |     4        |       5       |        
        # -------------------------------------------
        #      9     |              |               | 
        #      10    |     7        |       6       | 
        #      11    |              |               | 
        # -------------------------------------------
        
        # -------------------------------------------
        #      8     |     4        |       5       |        
        # -------------------------------------------
        #   14 | 15  |              |       |       | 
        #   16 | 17  |     7        |   13  |  12   | 
        #   18 | 19  |              |       |       | 
        # -------------------------------------------
        elif pos == 4:
            return width /3 + (width/3-largeur)/2, (height/2-hauteur)/2
        elif pos == 5:
            return width * 2/3 + (width/3-largeur)/2, (height/2-hauteur)/2
        elif pos == 6:
            return width * 2/3 + (width/3-largeur)/2, height/2 + (height/2-hauteur)/2 - offset
        elif pos == 7:
            return width /3 + (width/3-largeur)/2, height/2 + (height/2-hauteur)/2 - offset
        elif pos == 8:
            return (width/3-largeur)/2, height/4 + (height/4-hauteur)/2 + 30
        elif pos == 9:
            return (width/3 - self.button_width)/2, height/2 + (height/2 - 3 * self.button_height)/4 - offset
        elif pos == 10:
            return (width/3 - self.button_width)/2, height/2 + 2 * (height/2 - 3 * self.button_height)/4 + self.button_height - offset
        elif pos == 11:
            return (width/3 - self.button_width)/2, height/2 + 3 * (height/2 - 3 * self.button_height)/4 + 2 * self.button_height - offset
        elif pos == 14:
            return (width/3 - self.button_width*2)/4, height/2 + (height/2 - 3 * self.button_height)/4 - offset
        elif pos == 15:
            return (width/3 - self.button_width*2)*3/4 + self.button_width, height/2 + (height/2 - 3 * self.button_height)/4 - offset
        elif pos == 16:
            return (width/3 - self.button_width*2)/4, height/2 + 2 * (height/2 - 3 * self.button_height)/4 + self.button_height - offset
        elif pos == 17:
            return (width/3 - self.button_width*2)*3/4 + self.button_width, height/2 + 2 * (height/2 - 3 * self.button_height)/4 + self.button_height - offset
        elif pos == 12:
            return 5*width/6 + (width/6 - largeur)/2, height/2 + (height/2-hauteur)/2 - offset
        elif pos == 13:
            return 2*width/3  + (width/3 - largeur)/2, height/2 + (height/2-hauteur)/2 - offset
        elif pos == 18:
            return (width/3 - self.button_width*2)/4, height/2 + 3 * (height/2 - 3 * self.button_height)/4 + 2 * self.button_height - offset
        elif pos == 19:
            return (width/3 - self.button_width*2)*3/4 + self.button_width, height/2 + 3 * (height/2 - 3 * self.button_height)/4 + 2 * self.button_height - offset
        elif pos == 20:
            return (width/3 - self.button_width*2)/4, height/2 + 3 * (height/2 - 3 * self.button_height)/4 - self.button_width - offset
        elif pos == 21:
            return (width/3 - self.button_width*2)*3/4 + self.button_width, height/2 + 3 * (height/2 - 3 * self.button_height)/4 - 2*offset
        
    def Set_image(self, figure):
        resampling_filter = Image.LANCZOS
        largeur_max = self.window_width/3 - 30
        if figure == 'pol0' or figure == 'pol':
            if len(self.seq) == 1:
                if figure == 'pol0':
                    chemin = "Ressources/images_fixes/figure_polaire0.png"
                else:
                    chemin = "Ressources/images_gen/figure_polaire.jpeg"
                pos = 1
            else:
                chemin = "Ressources/images_gen/figure_polaire_emp.jpeg"
                pos = 4
            image_1 = Image.open(chemin)
            width, height = image_1.size
            image_1 = image_1.resize((int(largeur_max), int((largeur_max * height)/width)), resampling_filter) # Image.ANTIALIAS
            x, y = self.position_pr_aff(image_1.size, pos)
            self.photo_1 = ImageTk.PhotoImage(image_1)
            self.label_1 = tk.Label(image=self.photo_1).place(x = x, y = y)
        elif figure == 'cart0' or figure == 'cart':
            if len(self.seq) == 1:
                if figure == 'cart0':
                    chemin = "Ressources/images_fixes/figure_cartesienne0.png"
                else:
                    # chemin = "Ressources/figure_cartesienne.png"
                    chemin = "Ressources/images_gen/figure_cartesienne.jpeg"
                pos = 2
            else:
                # chemin = "Ressources/figure_cartesienne_emp.png"
                chemin = "Ressources/images_gen/figure_cartesienne_emp.jpeg"
                pos = 5
            image_2 = Image.open(chemin)
            width, height = image_2.size
            image_2 = image_2.resize((int(largeur_max), int((largeur_max * height)/width)), resampling_filter)  # Adjust width2 and height2 according to your needs
            self.photo_2 = ImageTk.PhotoImage(image_2)
            x, y = self.position_pr_aff(image_2.size, pos)
            self.label_2 = tk.Label(image=self.photo_2).place(x = x, y = y)
        elif figure == 'dess_emp':
            self.empilement.Dessin_pli('') # On met à jour le graphique de la section
            image_0 = Image.open("Ressources/images_gen/dessin_empilement.jpeg")
            width, height = image_0.size
            new_height = 250
            new_width = int((new_height * width) / height)
            image_0 = image_0.resize((new_width, new_height), resampling_filter)
            self.photo_0 = ImageTk.PhotoImage(image_0)
            width, height = image_0.size
            x, y = self.position_pr_aff(image_0.size, 13)
            self.label_0 = tk.Label(image=self.photo_0).place(x = x, y = y)
        elif figure == 'section':
            self.empilement.Affichage(int(self.orientation_sollicitation.get())) # On met à jour le graphique de la section
            image_01 = Image.open("Ressources/images_gen/figure_section.png")
            width, height = image_01.size
            largeur_sect = largeur_max = 350
            image_01 = image_01.resize((int(largeur_sect), int((largeur_sect * height)/width)), resampling_filter) # Image.NEAREST
            x, y = self.position_pr_aff(image_01.size, 7)
            self.photo_01 = ImageTk.PhotoImage(image_01)
            self.label_01 = tk.Label(image=self.photo_01).place(x = x, y = y)  
        elif figure == 'ldc':
            if len(self.seq) == 1:
                chemin = "Ressources/images_fixes/ldc_sym.png"
            else:
                if Utils.plaque:
                    chemin = "Ressources/images_fixes/ldc_gen_plaque_sym.png"
                else:
                    chemin = "Ressources/images_fixes/ldc_gen_sym.png"
            image_ldc = Image.open(chemin)
            width, height = image_ldc.size
            image_ldc = image_ldc.resize((int(largeur_max), int((largeur_max * height)/width)), resampling_filter) # Image.NEAREST
            x, y = self.position_pr_aff(image_ldc.size, 8)
            self.photo_ldc = ImageTk.PhotoImage(image_ldc)
            self.label_ldc = tk.Label(image=self.photo_ldc).place(x = x, y = y)  

    
    def mapper(self, i):
        '''
        Fonction qui transforme les indices de la grille avec les boites à cocher en les indices de la matrice colonne de rigidité 
    
        Parameters
        ----------
        i : int
            indice de la checkboxe.
    
        Returns
        -------
        L_indice : int
            Indice de la matrice colonne de la matrice de rigidité.
    
        '''
        if Utils.plaque:
            Dict_map = Mat_map_plaque
        else:
            Dict_map = Mat_map
        return Dict_map[0][i], Dict_map[1][i], Dict_map[2][i], Dict_map[5][i]
    
if __name__ == "__main__":
    # root = tk.Tk()
    # app = InterfaceInitialisationSequence(root, "Initialisation", [], '', 0)
    Utils.vider_les_doss()
    app = InterfaceChoixStructure()