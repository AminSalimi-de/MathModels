import pyomo.environ as pyo
from pyomo.environ import *
from enum import IntEnum

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

def GetPowerBounds(m, i, j):
    if i < GeneratorType.GEN2:
        return (Pmin1, Pmax1)
    elif i < GeneratorType.GEN3:
        return (Pmin2, Pmax2)
    else:        
        return (Pmin3, Pmax3)

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
    
    #       Constraints
    
    return model

PowerGenerationModel = BuildPowerGenerationModel()

print("end")