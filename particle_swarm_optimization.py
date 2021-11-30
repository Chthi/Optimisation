#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import math
from random import randint, random
from collections import namedtuple
from copy import deepcopy

from time import sleep
import tkinter as tk

from thread_manager import spawnthread



def attractivity(pos, func="quadrillage"):
    """Attractivity of a position on the map.
    Between 0 and 1"""

    if func == "quadrillage":
        attractivity = (math.sin(pos.x / 10) + math.sin(pos.y / 10)) / 2
    elif func == "vagues":
        attractivity = (math.sin(math.sqrt(abs(pos.x)) * 2) + math.sin(math.sqrt(abs(pos.y)) * 2)) / 2  
    elif func == "diagonales":
        attractivity = math.sin(pos.x / 20 + pos.y / 20)
    elif func == "lignes":
        attractivity = math.sin(pos.x / 20)
    elif func == "sloppy":
        attractivity = math.log(pos.x)
    elif func == "chaotic":
        attractivity = 2 * random() - 1
    elif func == "uniforme":
        attractivity = 1
    return attractivity



# an object to store coefficients
Coefficient = namedtuple("Coefficient", ['inertie', 'social', 'cognitif', 'contrition'])


class Couple:
    """Represent a pair of values.
    Can be used as coordinates."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __rsub__(self, other):
        if isinstance(other, Couple):
            self.x -= other.x
            self.y -= other.y

    def __radd__(self, other):
        if isinstance(other, Couple):
            self.x += other.x
            self.y += other.y
        else:
            self.x += other
            self.y += other

    def __add__(self, other):
        if isinstance(other, Couple):
            return Couple(self.x + other.x, self.y + other.y)
        else:
            return Couple(self.x + other, self.y + other)

    def __sub__(self, other):
        if isinstance(other, Couple):
            return Couple(self.x - other.x, self.y - other.y)
        else:
            return Couple(self.x - other, self.y - other)

    def __mul__(self, other):
        if isinstance(other, Couple):
            return Couple(self.x * other.x, self.y * other.y)
        else:
            return Couple(self.x * other, self.y * other)

    def __truediv__(self, other):
        if isinstance(other, Couple):
            return Couple(self.x / other.x, self.y / other.y)
        else:
            return Couple(self.x / other, self.y / other)

    def __floordiv__(self, other):
        if isinstance(other, Couple):
            return Couple(self.x // other.x, self.y // other.y)
        else:
            return Couple(self.x // other, self.y // other)

    def __repr__(self):
        return "({0}, {1})".format(self.x, self.y)

    def __str__(self):
        return "({0}, {1})".format(self.x, self.y)

    def copy(self):
        return Couple(self.x, self.y)



class Particule():
    id_max = 1

    def __init__(self, largeur=200, hauteur=200, essaim=None):
        # id of the particule
        self.id = Particule.id_max
        Particule.id_max += 1
        # x, y
        x, y = randint(0, largeur), randint(0, hauteur)
        self.pos = Couple(x, y)
        # speed and direction
        self.vitesse = Couple(2*random()-1, 2*random()-1)

        inertie = 2.5 + ((2 * random() - 1) / 4)
        social = 0.10 + ((2 * random() - 1) / 20)
        cognitif = 0.08 + ((2 * random() - 1) / 10)
        # cognitif = 0.0
        contrition = 1

        self.coeffs = Coefficient(inertie, social, cognitif, contrition)
        # best encontered position of the particule since the begining
        self.best_pos = Couple(x, y)
        # the value corresponding to the best position
        self.best_val = attractivity(Couple(x, y))
        # the swarm in which is the particule 
        self.essaim = essaim
        # list of particule considered as social friends of this one
        self.friends = []


    def friends_pos(self):
        """return the best position between all the friends of the particule"""
        best_pos = self.friends[0].pos
        best_val = attractivity(self.friends[0].pos)
        for i in range(1, len(self.friends)):
            value = attractivity(self.friends[i].pos)
            if value > best_val:
                best_val = value
                best_pos = self.friends[i].pos
        return best_pos


    def normalise(self, vitesse):
        """Normalise the speed so it don't exeed the speed limit"""
        value = math.sqrt(vitesse.x**2 + vitesse.y**2)
        vitesse_max = 2
        # print("value : {}".format(value))
        if value > vitesse_max:
            vitesse = vitesse * vitesse_max / value
        return vitesse


    def move(self):
        self.vitesse =  self.vitesse * self.coeffs.inertie \
                        + (self.friends_pos() - self.pos) * self.coeffs.social \
                        + (self.best_pos - self.pos) * self.coeffs.cognitif
        self.vitesse = self.normalise(self.vitesse)
        # print(self.vitesse)
        # print("Vitesse ({0}, {1})".format(self.vitesse.x, self.vitesse.y))
        value = attractivity(self.pos)
        if value > self.best_val:
            self.best_pos = self.pos
            self.best_val = value
        self.pos = self.pos + self.vitesse
        # print("Moving to ({0}, {1})".format(self.pos.x, self.pos.y))



class Essaim(list):

    def __init__(self, largeur=200, hauteur=200):
        self.size = 20
        self.life_span = 0
        self.particules = [Particule(largeur, hauteur, self) for x in range(self.size)]
        
        self.nb_of_friends = 2
        for i, particule in enumerate(self.particules):
            for friend in range(1, self.nb_of_friends+1):
                particule.friends.append(self.particules[(i+friend) % self.size])
                print("particule {0} friend with {1}".format(i, (i+friend) % self.size))

        # TODO init
        self.best_pos = Couple(100, 100)
        self.best_val = attractivity(Couple(100, 100))
        # TODO init
        self.center_of_mass = Couple(100, 100)

    def __len__(self):
        return self.size

    def move(self):
        self.life_span += 1
        new_center_of_mass = Couple(0, 0)
        for particule in self.particules:
            particule.move()
            new_center_of_mass += particule.pos
            if particule.best_val > self.best_val:
                print("new best value from {0} to {1}".format(self.best_val, particule.best_val))
                self.best_pos = particule.best_pos
                self.best_val = particule.best_val
        new_center_of_mass /= self.size
        self.center_of_mass = new_center_of_mass.copy()
        # print("center of mass {0}".format(self.center_of_mass))


    def run(self):
        while 1:
            self.move()




class Boids():

    def __init__(self, size=20, largeur=200, hauteur=200):
        # super().__init__(master)
        self.master = tk.Tk()

        self.temps = 0
        self.dim = Couple(largeur, hauteur)
        self.vitesse = 1
        self.quitter = False
        self.essaim = Essaim(self.dim.x, self.dim.y)

        Images = namedtuple("Images", ['particules', 'mass_center', 'best_pos', 'heights'])
        self.images = Images([], [], [], [])
        self.threads = []

        self.create_widgets()
        self.threads.append(spawnthread(self.run))
        self.master.mainloop()


    def create_widgets(self):
        self.interface = dict()
        self.interface["Temps"] = tk.Label(self.master, text="Temps : "+str(self.temps), font="Arial 8", anchor='ne')
        self.interface["Temps"].pack()

        self.interface["Carte"] = tk.Canvas(self.master,width=self.dim.x,height=self.dim.y, borderwidth=0, background="#EECCAA", takefocus="1")
        self.interface["Carte"].pack()


        for i in range(0, self.dim.x * self.dim.y // (4 * 4)): # one step or ground is 4x4px
            x = (i * 4)  % self.dim.x + 2
            y = (i * 4) // self.dim.x * 4 + 2
            color_level = int((attractivity(Couple(x,y)) + 1) / 2 * 255)
            grey_level = '#%02x%02x%02x' % (color_level, color_level, color_level)
            image = self.interface["Carte"].create_rectangle(x, y, x+4, y+4, fill=grey_level, width=0)
            self.images.heights.append(image)


        self.interface["Quitter"] = tk.Button(self.master, text="Stopper la simulation", command=self.quit)
        self.interface["Quitter"].pack()
        self.interface["Vitesse"] = tk.Scale(self.master, orient="horizontal", from_=1, to=200, resolution=1, tickinterval=100, length=100, label="Vitesse")
        self.interface["Vitesse"].set(25)
        self.interface["Vitesse"].pack()

        self.zone_coeffs = tk.Canvas(self.master, width=80, height=40)
        self.zone_coeffs.pack()

        self.interface["inertie"] = tk.Scale(self.zone_coeffs, orient="vertical", from_=3, to=0, resolution=0.01, length=100, label="i")
        self.interface["inertie"].set(self.essaim.particules[0].coeffs.inertie)
        self.interface["inertie"].pack(side=tk.LEFT)

        self.interface["social"] = tk.Scale(self.zone_coeffs, orient="vertical", from_=2, to=0, resolution=0.01, length=100, label="s")
        self.interface["social"].set(self.essaim.particules[0].coeffs.social)
        self.interface["social"].pack(side=tk.TOP)

        self.interface["cognitif"] = tk.Scale(self.zone_coeffs, orient="vertical", from_=2, to=0, resolution=0.01, length=100, label="c")
        self.interface["cognitif"].set(self.essaim.particules[0].coeffs.cognitif)
        self.interface["cognitif"].pack(side=tk.RIGHT)

        for particule in self.essaim.particules:
            self.images.particules.append(self.interface["Carte"].create_oval(particule.pos.x-4,particule.pos.y-4, particule.pos.x+4,particule.pos.y+4, fill="Yellow", outline="Black", width="1"))

        self.images.mass_center.append(self.interface["Carte"].create_oval(self.essaim.center_of_mass.x-4,self.essaim.center_of_mass.y-4, self.essaim.center_of_mass.x+4,self.essaim.center_of_mass.y+4, fill="Red", outline="Black", width="1"))

        self.images.best_pos.append(self.interface["Carte"].create_oval(self.essaim.best_pos.x-4,self.essaim.best_pos.y-4, self.essaim.best_pos.x+4,self.essaim.best_pos.y+4, fill="Green", outline="Black", width="1"))


    def quit(self):
        self.quitter = True


    def run(self):
        while not self.quitter:
            self.essaim.move()
            for i, particule in enumerate(self.essaim.particules):
                self.interface["Carte"].coords(self.images.particules[i], particule.pos.x-4, particule.pos.y-4, particule.pos.x+4, particule.pos.y+4)

            self.interface["Carte"].coords(self.images.mass_center[0], self.essaim.center_of_mass.x-4, self.essaim.center_of_mass.y-4, self.essaim.center_of_mass.x+4, self.essaim.center_of_mass.y+4)

            self.interface["Carte"].coords(self.images.best_pos[0], self.essaim.best_pos.x-4, self.essaim.best_pos.y-4, self.essaim.best_pos.x+4, self.essaim.best_pos.y+4)
            self.vitesse = self.interface["Vitesse"].get()
            # print("SPEED {}".format(self.vitesse))
            sleep(1 / self.vitesse)
        self.master.destroy()





def test_couple():
    c1 = Couple(1, 1)
    c2 = Couple(2, 2)
    print(" ---- {} ---- ".format("c1 + c2"))
    print(c1 + c2)
    print(" ---- {} ---- ".format("c1 - c2"))
    print(c1 - c2)
    print(" ---- {} ---- ".format("c1 * c2"))
    print(c1 * c2)



# test_couple()

Boids()



