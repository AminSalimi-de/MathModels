import highspy
import numpy as np
from enum import IntEnum

h = highspy.Highs()

nOils = 5
nMonths = 6

InitialStorage = 500 #[ton] 
JuneStorage = 500 #[ton]
StorageUB = 1000 #[ton]
MonthlyStorageCost = 5 #[pond/(ton.month)]
ProductPrice = 150 # 150 [pond/ton]
VegetableOilMonthlyRefiningLimit = 200
NonVegetableOilMonthlyRefiningLimit = 250

class OilType(IntEnum):
    VEGETABLE_OIL = 0
    NON_VEGETABLE_OIL = 1

OilsHardnessCoefficient = [8.8, 6.1, 2.0, 4.2, 5]
ProductHardnessCoefficientLB = 3
ProductHardnessCoefficientUB = 6

# [i][j] where i=Oil Type, j=Month index
def Create2DArray(n1, n2):
    return [[None for x2 in range(n2)] for x1 in range(n1)]

def Create1DArray(size):
    return [None for x1 in range(size)]

def GetOilPrices():
    Oil0Prices = [110, 130, 110, 120, 100, 90]
    Oil1Prices = [120, 130, 140, 110, 120, 100]
    Oil2Prices = [130, 110, 130, 120, 150, 140]
    Oil3Prices = [110, 90, 100, 120, 110, 80]
    Oil4Prices = [115, 115, 95, 125, 105, 135]
    return [Oil0Prices, Oil1Prices, Oil2Prices, Oil3Prices, Oil4Prices]

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

for j in range(nMonths):
    PV[j] = h.addVariable()


#       Objective
Income = 0
for monthlyProd in PV:    
    Income = ProductPrice*monthlyProd

OilPurchaseCost = 0
OilPrices = GetOilPrices()
for i in range(nOils):
    for j in range(nMonths):
        OilPurchaseCost += OilPrices[i][j] * BV[i][j]

OilStorageCost = 0
for i in range(nOils):
    for j in range(nMonths):
        OilPurchaseCost += MonthlyStorageCost * SV[i][j]

Cost = OilPurchaseCost + OilStorageCost

Profit = Income - Cost


#       Constraints
# Inventory
InventoryEqs = Create2DArray(nOils, nMonths)
for i in range(nOils):
    for j in range(nMonths):
        dS = SV[i][j]
        if j==0:
            dS -= InitialStorage
        else:
            dS -= SV[i][j-1]
        InventoryEqs[i][j] = h.addConstr(BV[i][j] - UV[i][j] == dS)

# Mass Balance:
MassBalamceEqs = Create1DArray(nMonths)
for j in range(nMonths):
    UsedOil = 0
    for i in range(nOils):
        UsedOil += UV[i][j]
    MassBalamceEqs[j] = h.addConstr(UsedOil == PV[j])

# Refining Limits:
RefiningConstraints = Create2DArray(2, nMonths)
for j in range(nMonths):
    RefiningConstraints[OilType.VEGETABLE_OIL][j] = h.addConstr(UV[0][j]+UV[1][j]<=VegetableOilMonthlyRefiningLimit)
    RefiningConstraints[OilType.NON_VEGETABLE_OIL][j] = h.addConstr(UV[2][j]+UV[3][j]+UV[4][j]<=NonVegetableOilMonthlyRefiningLimit)

# Hardness:
HardnessConstraints = Create1DArray(nMonths)
for j in range(nMonths):
    ProductHardness = 0
    for i in range(nOils):
        ProductHardness += OilsHardnessCoefficient[i] * UV[i][j]
    HardnessConstraints[j] = h.addConstr(ProductHardnessCoefficientLB*PV[j] <= ProductHardness <= ProductHardnessCoefficientUB*PV[j])


#       Optimize
h.maximize(Profit)

print("end")