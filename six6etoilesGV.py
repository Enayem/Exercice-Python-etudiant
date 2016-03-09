#############################################################################
#                                                                           #
#   Gregoire Viot le 12/01/2016                                             #
#   Créer cinq étoile à 6 branches croissante et décroissantes en taille    #                            #
#                                                                           #
#############################################################################

from turtle import *

##############################################################################

haut=-120
bas=120

title('Cinq etoiles a six branches')

def trianglee(pas,couleur,direction):

    color(couleur)
    forward(pas)
    right(direction)
    color(couleur)
    forward(pas)
    right(direction)
    color(couleur)
    forward(pas)
    color(couleur)

def etoile6(pas,couleur):

    trianglee(pas,couleur,haut)

    up()
    left(30)
    left(180)
    forward(pas/2)
    right(90)
    down()

    trianglee(pas,couleur,bas)

def allergauche(pas):
    up()
    left(180)
    forward(pas*2)
    left(180)
    down()

def etoilesuivante(pas):
    up()
    right(120)
    forward(pas)
    right(90)
    forward(pas/2)
    left(90)
    down()

    
##############################################################################

speed('fastest')
allergauche(120)
etoile6(30,'blue')
etoilesuivante(30)
etoile6(60,'purple')
etoilesuivante(60)
etoile6(120,'red')
etoilesuivante(120)
etoile6(60,'purple')
etoilesuivante(60)
etoile6(30,'blue')

##############################################################################
#                                                                            #
#Pour le fun                                                                 #
#                                                                            #
##############################################################################

up()
right(210)
forward(80)
right(90)
forward(150)
left(180)
down()

color('black')
write('FUCK YEAH')



