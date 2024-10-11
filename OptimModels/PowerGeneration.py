import pyomo.environ as pyo
from pyomo.environ import *
from enum import IntEnum
import Helper

#       Parameters:
nGen1 = 12
nGen2 = 10
nGen3 = 5
nPeriod = 5        

Pmin1 = 850;  Pmax1=2000 #[MW]
Pmin2 = 1250; Pmax2=1750 #[MW]
Pmin3 = 1500; Pmax3=4000 #[MW]

class GeneratorType(IntEnum):
    GEN1 = 1
    GEN2 = nGen1+1
    GEN3 = nGen1+nGen2+1

PeriodDuarations = [6.0, 3.0, 6.0, 3.0, 6.0]
def GetPeriodDuration(j): #[hr]
    return PeriodDuarations[j-1]

def GetStartUpCost(i):
    if i < GeneratorType.GEN2:
        return 2000
    elif i < GeneratorType.GEN3:
        return 1000
    else:        
        return 500

def GetMinGenCost(i): #[cost/hr]
    if i < GeneratorType.GEN2:
        return 1000
    elif i < GeneratorType.GEN3:
        return 2600
    else:        
        return 3000

def GetVOMCost(i): #[cost/hr/MW]
    if i < GeneratorType.GEN2:
        return 2.0
    elif i < GeneratorType.GEN3:
        return 1.30
    else:        
        return 3

def GetPowerBounds(m, i, j):
    if i < GeneratorType.GEN2:
        return (Pmin1, Pmax1)
    elif i < GeneratorType.GEN3:
        return (Pmin2, Pmax2)
    else:        
        return (Pmin3, Pmax3)

def GetPmin(i):
    return GetPowerBounds(None,i,None)[0]

def GetPmax(i):
    return GetPowerBounds(None,i,None)[1]

Load = [15000, 30000, 25000, 40000, 27000]
def GetLoad(j): #[MW]    
    return Load[j-1]

def GetObjectiveExpression(m):
    StartUpCost = 0; MinimumGenerationCost = 0; VOMCost = 0
    for i in m.I:
        StartUpCost += sum(GetStartUpCost(i)*m.SU[i,j] for j in m.J)
        MinimumGenerationCost += sum(GetMinGenCost(i)*GetPeriodDuration(j)*m.UP[i,j] for j in m.J)
        VOMCost += sum(GetVOMCost(i)*GetPeriodDuration(j)*(m.P[i,j]-GetPmin(i)) for j in m.J)        
    return StartUpCost + MinimumGenerationCost + VOMCost

def GetPowerBalanceEq(m, j):
    Generation = sum(m.UP[i,j]*m.P[i,j] for i in m.I)
    return Generation == GetLoad(j)

def GetUpReserveEq(m, j):
    ExtraGenerationCapacity = sum(m.UP[i,j]*(GetPmax(i)-m.P[i,j]) for i in m.I)
    return ExtraGenerationCapacity >= 0.15*GetLoad(j)

def GetUP_SU_Relation(m, i, j):
    if j==1:
        return m.UP[i,j]-m.UP[i,nPeriod] <= m.SU[i,j]    
    else:
        return m.UP[i,j]-m.UP[i,j-1] <= m.SU[i,j]

def BuildPowerGenerationModel():
    model = pyo.ConcreteModel()
    #       Parameters:
    model.I = pyo.RangeSet(nGen1+nGen2+nGen3)
    model.J = pyo.RangeSet(nPeriod)
    #       Variables:
    model.P = pyo.Var(model.I, model.J, bounds=GetPowerBounds)
    model.UP = pyo.Var(model.I, model.J, domain=pyo.Binary)
    model.SU = pyo.Var(model.I, model.J, domain=pyo.Binary)
    #       Objective:
    model.OBJ = pyo.Objective(rule=GetObjectiveExpression, sense=pyo.minimize)
    #       Constraints
    model.PB = pyo.Constraint(model.J, rule=GetPowerBalanceEq)
    model.UP_RES = pyo.Constraint(model.J, rule=GetUpReserveEq)
    model.StartUp = pyo.Constraint(model.I, model.J, rule=GetUP_SU_Relation)
    return model

PowerGenerationModel = BuildPowerGenerationModel()

Helper.WriteLP(PowerGenerationModel, "PowerGeneration")
Helper.SolveModel(PowerGenerationModel)
Helper.PrintModelResults(PowerGenerationModel)