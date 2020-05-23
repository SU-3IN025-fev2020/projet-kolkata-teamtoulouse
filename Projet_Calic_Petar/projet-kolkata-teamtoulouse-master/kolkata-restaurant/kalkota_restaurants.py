# -*- coding: utf-8 -*-

# Nicolas, 2020-03-20

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
import pygame
import glo

import random 
import numpy as np
import sys

import queue as qu



    
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'kolkata_6_10'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():

    #for arg in sys.argv:
    iterations = 20 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)
    
    init()
    
    
    

    
    #-------------------------------
    # Initialisation
    #-------------------------------
    nbLignes = game.spriteBuilder.rowsize
    nbColonnes = game.spriteBuilder.colsize
    print("lignes", nbLignes)
    print("colonnes", nbColonnes)
    
    
    players = [o for o in game.layers['joueur']]      # Nombre de jouers
    nbPlayers = len(players)
    print('nb joueurs:',nbPlayers)  #affiche le nombre de jouers
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    
    # on localise tous les objets  ramassables (les restaurants)
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    print ("Goal states:", goalStates)
    
    
    nbRestaus = len(goalStates)
    
    print('nbRestaus',nbRestaus)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    #print ("Wall states:", wallStates)
    
    # on liste toutes les positions permises  ::::: super important!!
    allowedStates = [(x,y) for x in range(nbLignes) for y in range(nbColonnes)\
                     if (x,y) not in wallStates or  goalStates] 
    
    #-------------------------------
    # Placement aleatoire des joueurs, en évitant les obstacles
    #-------------------------------
        
    posPlayers = initStates

    
    for j in range(nbPlayers):
        x,y = random.choice(allowedStates)
        players[j].set_rowcol(x,y)      # set la position
        game.mainiteration()    #???
        posPlayers[j]=(x,y)    #ajuste la table de position

        
        
        
    
    #-------------------------------
    # chaque joueur choisit un restaurant
    #-------------------------------

    restau=[0]*nbPlayers            #[0, 0, 0, 0...] Initialisation 
    for j in range(nbPlayers):
        c = random.randint(0,nbRestaus-1)
        print(c)
        restau[j]=goalStates[c]             #On set pour chaque jouer un resteau
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
    
        
    # bon ici on fait juste plusieurs random walker pour exemple...
    ''' 
    for i in range(iterations):
        
        for j in range(nbPlayers):  # on fait bouger chaque joueur séquentiellement!
            row,col = posPlayers[j]

            x_inc,y_inc = random.choice([(0,1),(0,-1),(1,0),(-1,0)])    #Random function
            next_row = row+x_inc
            next_col = col+y_inc
            # and ((next_row,next_col) not in posPlayers)
           
            if ((next_row,next_col) not in wallStates) and next_row>=0 and next_row<=19 and next_col>=0 and next_col<=19:
                players[j].set_rowcol(next_row,next_col)    #set
                print ("pos :", j, next_row,next_col)
                game.mainiteration()
    
                col=next_col
                row=next_row
                posPlayers[j]=(row,col)
            
      
        
            
            # si on est à l'emplacement d'un restaurant, on s'arrête
            if (row,col) == restau[j]:
                #o = players[j].ramasse(game.layers)
                game.mainiteration()
                print ("Le joueur ", j, " est à son restaurant.")
               # goalStates.remove((row,col)) # on enlève ce goalState de la liste
                
                
                break
            
    
    pygame.quit() '''    
    
    #Maintenant faisons la version BreadthFirst
    def voisins(pos):
        directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]  #On ne peut pas aller daigonalement dans ce jeu
        res = []
        x,y = pos
        for dir in directions:
            next_x = x + dir[0]
            next_y = y + dir[1]
            if next_x>=1 and next_y>=1 and next_x<20 and next_y<20:
                res.append((next_x, next_y))
        return res
                
                
     

    path = []    #Chemin que l algo doit remplir: c'est un tableau à double entrée(pour chaque joueur il existe une route)
    
    #goal == restau[]
    for k in range(nbPlayers):
        x,y = posPlayers[k]
        start = (x,y)
        print("on commence pour",k)   #
        frontiere = qu.Queue()
        frontiere.put(start)
        visited = {}
        visited[start] = None
        print(visited)              #
        print(voisins(start))       #
        
        while not frontiere.empty():       
            it = frontiere.get()
            for next in voisins(it):
                if next not in visited:
                    frontiere.put(next)
                    visited[next] = it
                    
        #On va a l'envers pour tracer les routes jusqu aux restaurants
        current = restau[k] 
        print("curent",current)
        route = []
        while current != start:
            route.append(current)
            current = visited[current]
        route.append(start)
        route.reverse()        #La route pour le joueur K
        path.append(route)         #Le tableau avec toutes les routes
   


    #Maintenant a chaque itération chaque joueur fait un pas
    for i in range(iterations):
        
        for j in range(nbPlayers):  # on fait bouger chaque joueur séquentiellement!
            row,col = posPlayers[j]
            
            route_joueur = path[j]
            next_row , next_col = route_joueur[i+1]
            
           
            if ((next_row,next_col) not in wallStates) and next_row>=0 and next_row<=19 and next_col>=0 and next_col<=19:
                players[j].set_rowcol(next_row,next_col)    #set
                print ("pos :", j, next_row,next_col)
                game.mainiteration()
    
                col=next_col
                row=next_row
                posPlayers[j]=(row,col)
            
      
        
            
            # si on est à l'emplacement d'un restaurant, on s'arrête
            if (row,col) == restau[j]:
                #o = players[j].ramasse(game.layers)
                game.mainiteration()
                print ("Le joueur ", j, " est à son restaurant.")
               # goalStates.remove((row,col)) # on enlève ce goalState de la liste
                
                
                break
            
    
    pygame.quit()
    
        
    
 

if __name__ == '__main__':
    main()
    


