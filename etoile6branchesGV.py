# -*- coding: cp1252 -*-
#############################################################################
#                                                                           #
#   Gregoire Viot le 12/01/2016                                             #
#   Créer une étoile à 6 branches                                           #                            #
#                                                                           #
#############################################################################

from turtle import *

##############################################################################

haut=-120
bas=120


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

def etoile6(couleur):
    
    up()
    left(60)
    forward(30)
    down()

    trianglee(120,couleur,haut)

    up()
    right(120)
    forward(18)
    left(-120)
    left(90)
    forward(50)
    right(90)
    down()

    trianglee(120,couleur,bas)

##############################################################################

etoile6('blue')


#crééer 3 étoiles
#créer des étoiles qui grandissent et qui rétressissent
