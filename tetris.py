#########################################################################
#                                                                       #
#       Nom: BLANC Corentin    Classe: LIOVIS   Date: 22/01/16          #
#                                                                       #
#                             JEU TETRIS                                #
#                                                                       #
#########################################################################

#########################################################################

# Import de la librairie

from tkinter import *

#########################################################################
# Forme 4 carrés mouvement possible, coord X, coord Y ! Boutons, Vitesse
#########################################################################

root = Tk()
root.title("TETRIS")

#########################################################################

# Création du canvas

dessin = Canvas(width=700, height=800, bg="black")
dessin.pack()

framWid1=Frame()
framWid1.pack()

#########################################################################

# Création des carrés

def affEspaceJeu():
    global m
    dessin.delete('all')
    for indligne,liste in enumerate(m):
        for indcolonne,case in enumerate(liste):
            if case == 0:
                dessin.create_rectangle(indcolonne*20 +margex,(indligne*20) + margey,indcolonne*20+20+margex,(indligne*20)+20 + margey,fill='white')
            else:
                dessin.create_rectangle(indcolonne*20+margex,(indligne*20)+ margey,indcolonne*20+20+margex,(indligne*20)+20 + margey,fill='purple')
                
##########################################################################
       
# Définition des mouvements de chaque touches 

#########################################################################

# Definition d'une fonction pour le deplacement du carre

def avanceCarre():
            global x1,y1,dx,dy
            if ((x1 + dx) >= 0) and ((x1 + dx) <= 14) and ((y1 + dy) <= 30): #Tester l'espace de jeu
                if dx :
                    if m[y1][x1+dx] == 0 : #Tester si le déplacement est latéralle la superposition sur l'axe des X 
                        m[y1][x1] = 0
                        x1=x1+dx
                        y1=y1+dy
                        m[y1][x1] = 1
                        affEspaceJeu()
                else : #dy
                    m[y1][x1] = 0
                    x1=x1+dx
                    y1=y1+dy
                    m[y1][x1] = 1
                    affEspaceJeu()

#########################################################################

##########################################################################

# Fonction permettant de recréer un carré en haut de l'espace de jeu

def recreationCarre():
    global x1,y1,dx,dy      
    if ((y1 + dy) == 30) or (m[y1+dy][x1] == 1):
            detecteAnDeleteligne()
            m[y1][x1] = 1
            x1 = 7
            y1 = 0
            m[y1][x1] = 1
            affEspaceJeu()

            
##########################################################################
        
def Down():
    global dx,dy
    dx = 0
    dy = 1
    avanceCarre()
    recreationCarre()
    root.after(50,Down)

def actionKeyRight(event):
    global dx,dy
    dx,dy=1,0
    avanceCarre()
    
def actionKeyLeft(event):
    global dx,dy
    dx,dy=-1,0
    avanceCarre()
    
##########################################################################    

def antisup():
    if m[y1][x1+dx] == 0:
        avanceCarre()
        
##########################################################################

# Detection & supression de ligne

def detecteAnDeleteligne():
        for index, ligne in enumerate(m):
            if 0 not in ligne:
                print ("Ligne pleine detecté : ", index)
                m[index] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
                m[y1][x1] = 0

##########################################################################
           
def descentelignes():
    if detecteAnDeleteligne():
                m = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],ligne1,ligne2,ligne3,ligne4,ligne5,ligne6,ligne7,ligne8,ligne9,ligne10,ligne11,ligne12,ligne13,ligne14,ligne15,ligne16,ligne17,ligne18,ligne19,ligne20,ligne21,ligne22,ligne23,ligne24,ligne25,ligne26,ligne27,ligne28,ligne29]

#########################################################################

# Création d'une matrices m de 30 lignes de 15 valeurs

ligne1= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne2= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne3= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne4= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne5= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne6= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne7= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne8= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne9= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne10=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne11=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne12=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne13=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne14=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne15=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne16=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne17=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne18=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne19=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne20=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne21=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne22=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne23=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne24=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne25=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne26=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne27=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne28=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne29=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ligne30=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

m = [ligne1,ligne2,ligne3,ligne4,ligne5,ligne6,ligne7,ligne8,ligne9,ligne10,ligne11,ligne12,ligne13,ligne14,ligne15,ligne16,ligne17,ligne18,ligne19,ligne20,ligne21,ligne22,ligne23,ligne24,ligne25,ligne26,ligne27,ligne28,ligne29,ligne30]
margex, margey = 50, 50

x1,y1=7,0

#########################################################################

#Definition des actions de touche

root.bind("<Key-Right>", actionKeyRight)
root.bind("<Key-Left>", actionKeyLeft)

affEspaceJeu()
Down()

root.mainloop()
