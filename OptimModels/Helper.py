import pyomo.environ as pyo
from pyomo.environ import *

def SolveModel(m):
    solver = SolverFactory('highs')
    solver.solve(m)

def fix_binary_variables(model):
    for v in model.component_objects(Var, active=True):
        for index in v:
            if v[index].domain is Binary:
                v[index].fix(round(v[index].value))

def PrintModelResults(m):
    print("Objective value:", m.OBJ())
    for v in m.component_objects(Var, active=True):
        varobject = getattr(m, str(v))
        for index in varobject:
            print(f"{varobject[index].name} = {varobject[index].value}")
            
def WriteLP(m, name):
    m.write(f'C:/Users/AminSalimi/Documents/{name}.lp', format='lp', io_options={"symbolic_solver_labels": True})