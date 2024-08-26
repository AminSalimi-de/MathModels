import highspy
import numpy as np

h = highspy.Highs()

nOils = 5
nMonths = 6

JuneStorage = 500 #[ton]
StorageUB = 1000 #[ton]

# [i][j] where i=Oil Type, j=Month index
def Create2DArray(n1, n2):
    return [[None for x in range(n2)] for y in range(n1)]
def Create1DArray(size):
    return [None for y in range(nMonths)]


#       Decision Variables
BV = Create2DArray(nOils, nMonths) # Buy Oils Variables 
UV = Create2DArray(nOils, nMonths) # Use Oils Variables
SV = Create2DArray(nOils, nMonths) # Storage Oils Variables
PV = Create1DArray(nMonths) # Product Variables

for i in range(nOils):
    for j in range(nMonths):
        BV[i][j] = h.addVariable()

for i in range(nOils):
    for j in range(nMonths):
        UV[i][j] = h.addVariable()

for i in range(nOils):
    for j in range(nMonths):
        if j != nMonths-1:
            SV[i][j] = h.addVariable(ub=StorageUB)
        else:
            SV[i][j] = JuneStorage

for i in range(nMonths):
    PV[i] = h.addVariable()


#       Objective
ProductPrice = 150 # 150 [pond/ton]
Income = 0
for monthlyProd in PV:    
    Income = ProductPrice*monthlyProd

print("end")