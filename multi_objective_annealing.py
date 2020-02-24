#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 * Implementation of simulated annealing for multi objective discrete problems.
 * 
 * Description : Graphically solve the problems contained in kp directory
 * Display the results continuously in the terminal.
 * Convert all the problems to 2 objectives problems in graphical mode.
 * So it can be ploted.
 * 
 * Author : Thibault Charmet
 * Creation date : 01/2020
"""

import os
import numpy as np
import json
import time
from random import random, randint
import math
from matplotlib import pyplot as plt
from operator import itemgetter

# does the program displays graĥical evolution of the results
# if true the number of objectives will be brought to 2
graphical = True
# if true generate a plot window for each solution
one_window_by_solution = False
# maximum number of problems to solve (-1 means everything)
max_files = -1

# directory where the problems can be found
# http://home.ku.edu.tr/~moolibrary/kp.zip
directory = "kp"

# algorithm parameters
alpha = 0.99
Tmax = 300
Tmin = 10e-5
equilibre = 20

# solve discete knapsack problems contained in the kp directory 
files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith(".dat")]
# limit the number of files
files = files[0:max_files]
print(files)


def read_file(filename):
    """
    read a file of format
    number of objectives
    number of objects to choose from
    capactity of the knapsack (max weight supported)
    values of the different objects to pick (one column by object)
    last line is the weights of the differents objects to pick
    """
    with open(filename, 'r') as stream:
        objectives = int(stream.readline().rstrip())    
        if graphical:
            # bring it to 2 dimentions for display purpose
            objectives = 2
        objects = int(stream.readline().rstrip())
        capacity = int(stream.readline().rstrip())
        lines = stream.readlines()
        weights = lines[-1]
        # using json to convert to list
        weights = json.loads(weights)
        del lines[-1]
        values = json.loads("".join(lines))
        if graphical:
            values = values[0:2]
    return objectives, objects, capacity, weights, values
  

def approximate_objective(X):
    """global objective function that approximate
    a value that consider all objectives functions"""
    somme = 0
    for xn in X:
        for i in range(objectives):
            somme += math.log(values[i][xn])
    return somme


def voisin(X):
    """Find all the neighbour of a point.
    Here a point is a knapsack configuration.
    Return a slightly modified version of the knapsack."""
    res = list(X)
    # either remove of add element
    if (len(X) == 0) or (randint(0, 1) == 0):
        # adding
        # if not exceding capacity
        if sum(map(lambda xn : weights[xn], X)) < capacity:
            sX = set(X)
            sX.add(randint(0, objects-1))
            res = list(sX)
    else:
        # removing
        if len(X) > 1:
            del res[randint(0, len(X)-1)]
    return res


def dominance(Xa, Xb):
    """
    X1 dominates X2 if
        - X1 is at least as good as X2 in all objectives
        - X1 is strictly better than X2 in, at least, one objective.
    """
    as_good = True
    superior = False
    for i in range(objectives):
        scoreA = sum(values[i][xa] for xa in Xa)
        scoreB = sum(values[i][xb] for xb in Xb)
        as_good = as_good and scoreA >= scoreB
        superior = superior or scoreA > scoreB
    return as_good and superior

# test it
# print(dominance([8, 4, 7], [8, 4, 7]))

def clean(domine, pareto_front):
    """remove all dominated elements from the pareto front"""
    for elt in domine:
        pareto_front.remove(elt)
    return pareto_front


def annealing(objectives, objects, capacity, weights, values, fig=None, line1=None, line2=None):
    """simulated annealing algorithm"""
    # X = (x1, x2, ...)
    X = [0]
    fX = approximate_objective(X)
    # all points that are not dominated
    pareto_front = [X]
    # list of the points previously in the pareto front
    archive_pareto = []
    T = Tmax

    # create a figure for the problem
    if graphical:
        abss = [sum(values[0][x] for x in point) for point in pareto_front]
        ordo = [sum(values[1][x] for x in point) for point in pareto_front]
        if not fig or not line2 or not line2:
            plt.ion()
            fig = fig or plt.figure()
            ax = fig.add_subplot(111)
            line2, = ax.plot(abss, ordo, 'go')
            line1, = ax.plot(abss, ordo, '-o')
        plt.xlim([0, 1.2 * max(abss)])
        plt.ylim([0, 1.2 * max(ordo)])

    while T > Tmin :
        # constant temperature
        for i in range(equilibre):
            voisin_X = voisin(X)
            voisin_fX = approximate_objective(voisin_X)
            # determine if we accept a (sometimes slightly worse) solution
            delta = voisin_fX - fX
            if (delta < 0) or (random() < math.exp(-delta/T)):
                X = voisin_X
                fX = approximate_objective(X)
            # check if the new solution have a dominance on something
            if X not in pareto_front:
                # list of all points dominated by the new one
                domine = []
                dominated = False
                for point in pareto_front:
                    if dominance(X, point):
                        domine.append(point)
                    if dominance(point, X):
                        dominated = True
                # if the new point was never dominated we add it to the pareto front
                if not dominated:
                    pareto_front = clean(domine, pareto_front)
                    pareto_front.append(X)
                    archive_pareto.append(X)

                    # update plot
                    if graphical:
                        # compute old pareto values
                        abss = [sum(values[0][x] for x in point) for point in pareto_front]
                        ordo = [sum(values[1][x] for x in point) for point in pareto_front]
                        # we sort so they appear in an order nice to see
                        # and the lines between each points are not a mess
                        abss, ordo = [list(x) for x in zip(*sorted(zip(abss, ordo), key=itemgetter(0)))]
                        # set the new limits of the window
                        plt.xlim([0, 1.2 * max(abss)])
                        plt.ylim([0, 1.2 * max(ordo)])
                        # compute old pareto values
                        old_abss = [sum(values[0][x] for x in point) for point in archive_pareto]
                        old_ordo = [sum(values[1][x] for x in point) for point in archive_pareto]
                        # plot new and old points
                        line2.set_xdata(old_abss)
                        line2.set_ydata(old_ordo)
                        line1.set_xdata(abss)
                        line1.set_ydata(ordo)
                        # update the plot and take care of window events (like resizing etc.)
                        fig.canvas.flush_events()
                        # wait for next loop iteration
                        time.sleep(0.01)

        # update temperature
        T *= alpha
    return pareto_front, fig, line1, line2



fig, line1, line2 = None, None, None
for i, filename in enumerate(files):
    if one_window_by_solution:
        fig, line1, line2 = None, None, None
    print("file {0} of {1}".format(i+1, len(files)))
    filename = os.path.join(directory, filename)
    objectives, objects, capacity, weights, values = read_file(filename)
    print("objectives", objectives)
    print("objects", objects)
    print("capacity", capacity)
    print("values", values)
    print("weights", weights)
    pareto_front, fig, line1, line2 = annealing(objectives, objects, capacity, weights, values, fig, line1, line2)
    print("pareto front : ", str(pareto_front))




