import pyomo.environ as pyo
from pyomo.environ import *
from enum import IntEnum

model = pyo.ConcreteModel()


#       Model Parameters
nOils = 5
nMonths = 6

InitialStorage = 500 #[ton] 
FinalStorage = 500 #[ton]
StorageUB = 1000 #[ton]
MonthlyStorageCost = 5 #[pond/(ton.month)]
ProductPrice = 150 # 150 [pond/ton]
VegetableOilMonthlyRefiningLimit = 200 #[ton]
NonVegetableOilMonthlyRefiningLimit = 250 #[ton]

class OilCategory(IntEnum):
    VEGETABLE_OIL = 1
    NON_VEGETABLE_OIL = 2

OilsHardnessCoefficient = [8.8, 6.1, 2.0, 4.2, 5]
def GetHardnessCoeff(i):
    return OilsHardnessCoefficient[i-1]
ProductHardnessCoefficientLB = 3
ProductHardnessCoefficientUB = 6

model.I = pyo.RangeSet(1, nOils)
model.J = pyo.RangeSet(1, nMonths)
model.OilCategory = pyo.RangeSet(1, 2)

Oil1Prices = [110, 130, 110, 120, 100, 90]
Oil2Prices = [120, 130, 140, 110, 120, 100]
Oil3Prices = [130, 110, 130, 120, 150, 140]
Oil4Prices = [110, 90, 100, 120, 110, 80]
Oil5Prices = [115, 115, 95, 125, 105, 135]
OilPrices = [Oil1Prices, Oil2Prices, Oil3Prices, Oil4Prices, Oil5Prices]
def GetOilPrice(m, i, j):
    return OilPrices[i-1][j-1]
model.OilPrices = pyo.Param(model.I, model.J, initialize=GetOilPrice)


#       Variables
model.BV = pyo.Var(model.I, model.J, domain=pyo.NonNegativeReals)
model.UV = pyo.Var(model.I, model.J, domain=pyo.NonNegativeReals)
model.SV = pyo.Var(model.I, model.J, bounds=(0,StorageUB))
model.PV = pyo.Var(model.J, domain=pyo.NonNegativeReals)


#       Objective
def GetObjectiveExpression(m):    
    Income = sum(ProductPrice*m.PV[j] for j in m.J)
    OilPurchaseCost = 0
    OilStorageCost = 0
    for i in m.I:
        OilPurchaseCost += sum(m.OilPrices[i,j] * m.BV[i,j] for j in m.J)
        OilStorageCost += sum(MonthlyStorageCost * m.SV[i, j] for j in m.J)
    Cost = OilPurchaseCost + OilStorageCost
    Profit = Income - Cost
    return Profit    
model.OBJ = pyo.Objective(rule=GetObjectiveExpression, sense=pyo.maximize)


#       Constraints
# Inventory
def GetInventoryEq(m, i, j):
    dS = m.SV[i,j]
    if j==1:
        dS -= InitialStorage
    else:
        dS -= m.SV[i,j-1]
    return m.BV[i,j] - m.UV[i,j] == dS        
model.InventoryEqs = pyo.Constraint(model.I, model.J, rule=GetInventoryEq)

# Mass Balance:
def GetMassBalanceEq(m, j):
    return sum(m.UV[i,j] for i in m.I) == m.PV[j]
model.MassBalanceEqs = pyo.Constraint(model.J, rule=GetMassBalanceEq)

# Final Storage
def GetFinalStorageEq(m, i):
    return m.SV[i,nMonths]==FinalStorage
model.FinalStorageEqs = pyo.Constraint(model.I, rule=GetFinalStorageEq)

# Refining Limits:
def GetRefiningConstraint(m, type, j):
    if type==OilCategory.VEGETABLE_OIL:
        return m.UV[1,j]+m.UV[2,j]<=VegetableOilMonthlyRefiningLimit
    else:
        return m.UV[3,j]+m.UV[4,j]+m.UV[5,j]<=NonVegetableOilMonthlyRefiningLimit
model.RefiningConstraints = pyo.Constraint(model.OilCategory, model.J, rule=GetRefiningConstraint)

# Hardness:
def GetHardness(m, j):
    return sum(GetHardnessCoeff(i)*m.UV[i,j] for i in m.I)
def GetHardnessUBConstraint(m, j):
    return GetHardness(m, j) <= ProductHardnessCoefficientUB*m.PV[j]
def GetHardnessLBConstraint(m, j):
    return GetHardness(m, j) >= ProductHardnessCoefficientLB*m.PV[j]
model.HardnessUBConstraints = pyo.Constraint(model.J, rule=GetHardnessUBConstraint)
model.HardnessLBConstraints = pyo.Constraint(model.J, rule=GetHardnessLBConstraint)


#       Solve
solver = SolverFactory('highs')
solver.solve(model)


#       Write Model
model.write('C:/Users/AminSalimi/Documents/FM1.lp', format='lp', io_options={"symbolic_solver_labels": True})


#       Print Results
print("Objective value:", model.OBJ())
for v in model.component_objects(Var, active=True):
    varobject = getattr(model, str(v))
    for index in varobject:
        print(f"{varobject[index].name} = {varobject[index].value}")



#       Food Manufacture 2
# Binary Variables:
model.DUV = pyo.Var(model.I, model.J, domain=pyo.Binary)

# Indicator Constraints:
def GetIndicatorConstraintUB(m, i, j):
    IndicatorUB = 0
    if (i>2):
        IndicatorUB = VegetableOilMonthlyRefiningLimit
    else:
        IndicatorUB = NonVegetableOilMonthlyRefiningLimit
    return m.UV[i,j] - IndicatorUB*m.DUV[i,j] <= 0
model.IndicatorUBConstraint = pyo.Constraint(model.I, model.J, rule=GetIndicatorConstraintUB)

def GetIndicatorConstraintLB(m, i, j):
    IndicatorLB = 20 #[ton]
    return m.UV[i,j] - IndicatorLB*m.DUV[i,j] >= 0
model.IndicatorLBConstraint = pyo.Constraint(model.I, model.J, rule=GetIndicatorConstraintLB)

# Number of Oils Constraints:
def GetNumberOfOilsConstraint(m, j):
    return sum(m.DUV[i,j] for i in m.I) <= 3
model.NumberOfOilsConstraints = pyo.Constraint(model.J, rule=GetNumberOfOilsConstraint)

# Blending Consrtaints:
def GetBlendingConstraint(m, j):
    return m.DUV[1,j] + m.DUV[2,j] - 2*m.DUV[5,j] <= 0
model.BlendingConstraints = pyo.Constraint(model.J, rule=GetBlendingConstraint)


solver.solve(model)

print("Objective value:", model.OBJ())
for v in model.component_objects(Var, active=True):
    varobject = getattr(model, str(v))
    for index in varobject:
        print(f"{varobject[index].name} = {varobject[index].value}")