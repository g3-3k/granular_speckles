#! /usr/bin/python
# -*- coding: utf-8 -*-
# This file belongs to DWGranularSpeckles project.
# The software is realeased with MIT license.

import numpy as np
import math
import itertools
import multiprocessing
from functools import partial
from granular_speckles.utils import timeit


def coarsetool_time(matrix, L, t, pos):
    return np.array([np.mean(matrix[pos[0], pos[1], i:i+L])
                     for i in np.arange(t/L)])


@timeit
def coarseTime(timeserie, block_size):
    """
    coarsening over time of a time serie
    """
    h, w, t = timeserie.shape
    coupleiter = itertools.product(np.arange(h), np.arange(w))
    print("time coarsed matrix shape: {}, block size: {}"
          .format((h, w, t/block_size), block_size))
    pool = multiprocessing.Pool(processes=5)
    f = partial(coarsetool_time, timeserie, block_size, t)
    return np.stack(pool.map(f, coupleiter)).reshape(h, w, t/block_size)


def test_speed(self):
    second = self.parallelReducedTime()
    first = self.reducedTime()
    if (first == second).all():
        return first


@timeit
def coarseSpace(block_size, timeserie):
    '''
    coarsening over a time series matrix
    '''
    Coarser = CoarseMatrix(block_size, tuple(timeserie.shape[:-1]))
    pool = multiprocessing.Pool(processes=5)
    f = partial(coarsetool, Coarser)
    h, w, t = timeserie.shape
    matrix = pool.map(f, (timeserie[:, :, t] for t in np.arange(t)))
    h, w = matrix[0].shape
    timeserie = np.zeros((h, w, t))
    for count, mat in enumerate(matrix):
        timeserie[:, :, count] = mat
    timeserie = timeserie.reshape(h, w, t)
    print ("space coarse matrix shape {}".format(timeserie.shape))
    return timeserie


def coarsetool(coarser, matrix):
    return coarser.coarseMatrix(matrix)


def test_matrix():
    coarse = CoarseMatrix(2, (10, 10))
    a = np.zeros((10, 10, 10))
    a[0:2, 0:2, 0:2] = 3
    a[0:4, 0:4, 3:5] = 4
    a[:, :, 6] = a[:, :, 1]+a[:, :, 4]
    b = np.stack([coarse.coarseMatrix(a[:, :, i]) for i in range(10)])
    return a, b, coarse


class CoarseMatrix(object):
    def __init__(self, block_size, shape):
        self.matrix = None
        self.hnew = None
        self.wnew = None
        self.block_size = block_size
        self.shape = shape
        self.initResize()
        self.rightR = self.rightReducer(self.wnew*block_size, self.block_size)
        self.leftR = self.rightReducer(self.hnew*block_size,
                                       self.block_size).transpose()

    def initResize(self):
        '''
        reduce the matrix to multiple of block_size
        '''
        newsize = list(map((lambda x: math.floor(x/self.block_size)),
                           self.shape))
        # print "Attenzione le dimensione della matrice e' ridotta di {},
        # le nuove dimensioni sono {}".format([self.matrix.shape[0]-newsize[0]
        # *self.block_size for i in [0,1]], newsize)
        self.hnew = int(newsize[0])
        self.wnew = int(newsize[1])

    def resizeMatrix(self):
        self.matrix = self.matrix[:self.hnew *
                                  self.block_size, :self.wnew*self.block_size]

    def coarseMatrix(self, matrix):
        '''
        blocked matrix
        '''
        self.matrix = matrix
        if self.shape != matrix.shape:
            raise "not right dimension matrix!"
        return self.matrixReduction()

    @staticmethod
    def rightReducer(elems, L):
        a = np.zeros((elems, int(elems/L)), int)
        for i in range(elems):
            for j in range(int(elems/L)):
                if 0 <= -j*L+i <= L-1:
                    a[i, j] = 1.
        return a

    def matrixReduction(self):
        '''
        this function operates coarse graining as matrix product:
        B is original, resized, NxN matrix and C is the reducer:
        C^t B C is the coarse grained matrix, C is NxM matrix, where M is
        the size of final matrix
        '''

        self.resizeMatrix()
        return np.dot(np.dot(self.leftR, self.matrix),
                      self.rightR)/self.block_size/self.block_size

    def reduced(self):
        '''
        this function reduce the matrix, not userfriendly!
        '''
        self.resizeMatrix()

        def block_iterator(self):
            L = int(self.block_size)
            for i, j in itertools.product(range(self.hnew), range(self.wnew)):
                reduced = self.matrix[i*L:(i+1)*L, j*L:(j+1)*L]
                yield i, j, np.sum(reduced)/L/L
    # TimeSerie.variance(reduced)

        newarray = np.zeros((self.hnew, self.wnew))
        for i, j, submatrix in block_iterator(self):
            newarray[i, j] = submatrix
        self.newarray = newarray
        return newarray


test_matrix()
