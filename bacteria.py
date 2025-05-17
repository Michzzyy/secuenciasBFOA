import copy
import math
from multiprocessing import Manager, Pool, managers
from pickle import FALSE, TRUE
from evaluadorBlosum import evaluadorBlosum
import numpy
from fastaReader import fastaReader
import random
from copy import copy
import copy
import concurrent.futures
#modificaciones por stephanie michelle venegas gaytan 

class bacteria():
    
    def __init__(self, numBacterias):
        manager = Manager()
        self.blosumScore = manager.list(range(numBacterias))
        self.tablaAtract = manager.list(range(numBacterias))
        self.tablaRepel = manager.list(range(numBacterias))
        self.tablaInteraction = manager.list(range(numBacterias))
        self.tablaFitness = manager.list(range(numBacterias))
        self.granListaPares = manager.list(range(numBacterias))
        self.NFE = manager.list(range(numBacterias))
        self.evaluador = evaluadorBlosum()  # Instancia única del evaluador

    def resetListas(self, numBacterias):
        manager = Manager()
        self.blosumScore = manager.list(range(numBacterias))
        self.tablaAtract = manager.list(range(numBacterias))
        self.tablaRepel = manager.list(range(numBacterias))
        self.tablaInteraction = manager.list(range(numBacterias))
        self.tablaFitness = manager.list(range(numBacterias))
        self.granListaPares = manager.list(range(numBacterias))
        self.NFE = manager.list(range(numBacterias))
        
    def calcularConservacion(self, poblacion):
        """Calcula la conservación por posición usando BLOSUM62."""
        # Asume que todas las secuencias en una bacteria tienen la misma longitud
        if len(poblacion) == 0 or len(poblacion[0]) == 0:
            return numpy.zeros(1)
            
        conservacion = numpy.zeros(len(poblacion[0][0]))
        
        for i in range(len(poblacion[0][0])):  # Para cada posición en el alineamiento
            for bacterium in poblacion:
                # Obtener los aminoácidos en la posición i para todas las secuencias
                columna = [bacterium[sec][i] for sec in range(len(bacterium)) if i < len(bacterium[sec])]
                # Calcular score de conservación
                score = 0
                for j in range(len(columna)):
                    for k in range(j+1, len(columna)):
                        score += self.evaluador.getScore(columna[j], columna[k])
                conservacion[i] += score
        return conservacion

    def tumbo(self, numSec, poblacion, numGaps):
        """Versión mejorada del tumbo que considera conservación de posiciones"""
        if len(poblacion) == 0:
            return
            
        # Calcular conservación una vez por iteración
        conservacion = self.calcularConservacion(poblacion)
        
        # Evitar división por cero si todos los valores son iguales
        if numpy.max(conservacion) == numpy.min(conservacion):
            probabilidades = numpy.ones(len(conservacion)) / len(conservacion)
        else:
            # Invertir la conservación (menos conservado = más probable)
            probabilidades = 1 - (conservacion / numpy.max(conservacion))
            probabilidades = probabilidades / numpy.sum(probabilidades)  # Normalizar
        
        for i in range(len(poblacion)):
            bacterTmp = list(poblacion[i])
            
            for _ in range(numGaps):
                # 80% de probabilidad de usar conservación, 20% aleatorio
                if random.random() < 0.8 and len(probabilidades) > 0:
                    pos = numpy.random.choice(len(probabilidades), p=probabilidades)
                else:
                    pos = random.randint(0, len(bacterTmp[0])-1) if len(bacterTmp[0]) > 0 else 0
                
                # Insertar gap en todas las secuencias en la posición seleccionada
                for seq in range(len(bacterTmp)):
                    if pos < len(bacterTmp[seq]):
                        bacterTmp[seq].insert(pos, "-")
                    else:
                        bacterTmp[seq].append("-")
            
            poblacion[i] = tuple(bacterTmp)

    # LOS DEMAS METODOS NO HAN SIDO MODIFICADOS 
    def cuadra(self, numSec, poblacion):
        for i in range(len(poblacion)):
            bacterTmp = poblacion[i]
            bacterTmp = list(bacterTmp)
            bacterTmp = bacterTmp[:numSec]
            maxLen = 0
            for j in range(numSec):
                if len(bacterTmp[j]) > maxLen:
                    maxLen = len(bacterTmp[j])
            for t in range(numSec):
                gap_count = maxLen - len(bacterTmp[t])
                if gap_count > 0:
                    bacterTmp[t].extend(["-"] * gap_count)
                    poblacion[i] = tuple(bacterTmp)
                    
    def creaGranListaPares(self, poblacion):   
        for i in range(len(poblacion)):
            pares = list()
            bacterTmp = poblacion[i]
            bacterTmp = list(bacterTmp)
            for j in range(len(bacterTmp[0])) if len(bacterTmp) > 0 else []:
                column = self.getColumn(bacterTmp, j)
                pares = pares + self.obtener_pares_unicos(column)
            self.granListaPares[i] = pares

    def evaluaFila(self, fila, num):
        score = 0
        for par in fila:
            score += self.evaluador.getScore(par[0], par[1])
        self.blosumScore[num] = score
    
    def evaluaBlosum(self):
        with Pool() as pool:
            args = [(copy.deepcopy(self.granListaPares[i]), i) for i in range(len(self.granListaPares))]
            pool.starmap(self.evaluaFila, args)

    def getColumn(self, bacterTmp, colNum):
        column = []
        for i in range(len(bacterTmp)):
            if colNum < len(bacterTmp[i]):
                column.append(bacterTmp[i][colNum])
            else:
                column.append("-")
        return column
            
    def obtener_pares_unicos(self, columna):
        pares_unicos = set()
        for i in range(len(columna)):
            for j in range(i+1, len(columna)):
                par = tuple(sorted([columna[i], columna[j]]))
                pares_unicos.add(par)
        return list(pares_unicos)  

    def compute_diff(self, args):
        indexBacteria, otherBlosumScore, blosumScore, d, w = args
        diff = (blosumScore[indexBacteria] - otherBlosumScore) ** 2.0
        self.NFE[indexBacteria] += 1
        return d * numpy.exp(w * diff)

    def compute_cell_interaction(self, indexBacteria, d, w, atracTrue):
        with Pool() as pool:
            args = [(indexBacteria, otherBlosumScore, self.blosumScore, d, w) for otherBlosumScore in self.blosumScore]
            results = pool.map(self.compute_diff, args)
            pool.close()
            pool.join()
    
        total = sum(results)
    
        if atracTrue:
            self.tablaAtract[indexBacteria] = total
        else:
            self.tablaRepel[indexBacteria] = total
        
    def creaTablaAtract(self, poblacion, d, w):
        for indexBacteria in range(len(poblacion)):
            self.compute_cell_interaction(indexBacteria,d, w, TRUE)

    def creaTablaRepel(self, poblacion, d, w):
        for indexBacteria in range(len(poblacion)):
            self.compute_cell_interaction(indexBacteria,d, w, FALSE)
    
    def creaTablasAtractRepel(self, poblacion, dAttr, wAttr, dRepel, wRepel):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(self.creaTablaAtract, poblacion, dAttr, wAttr)
            executor.submit(self.creaTablaRepel, poblacion, dRepel, wRepel)

    def creaTablaInteraction(self):
        for i in range(len(self.tablaAtract)):
            self.tablaInteraction[i] = self.tablaAtract[i] + self.tablaRepel[i]

    def creaTablaFitness(self):
        for i in range(len(self.tablaInteraction)):
            valorBlsm = self.blosumScore[i]
            valorInteract = self.tablaInteraction[i]
            valorFitness = valorBlsm + valorInteract
            self.tablaFitness[i] = valorFitness
    
    def getNFE(self):
        return sum(self.NFE)
        
    def obtieneBest(self, globalNFE):
        bestIdx = 0
        for i in range(len(self.tablaFitness)):
            if self.tablaFitness[i] > self.tablaFitness[bestIdx]:
                bestIdx = i
        print("-------------------   Best: ", bestIdx, " Fitness: ", self.tablaFitness[bestIdx], "BlosumScore ", self.blosumScore[bestIdx], "Interaction: ", self.tablaInteraction[bestIdx], "NFE: ", globalNFE)
        return bestIdx, self.tablaFitness[bestIdx]

    def replaceWorst(self, poblacion, best):
        worst = 0
        for i in range(len(self.tablaFitness)):
            if self.tablaFitness[i] < self.tablaFitness[worst]:
                worst = i
        poblacion[worst] = copy.deepcopy(poblacion[best])