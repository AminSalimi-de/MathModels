import pyomo.environ as pyo
from pyomo.environ import *

def SolveModel(m):
    solver = SolverFactory('highs')
    solver.solve(m)

def PrintModelResults(m):
    print("Objective value:", m.OBJ())
    for v in m.component_objects(Var, active=True):
        varobject = getattr(m, str(v))
        for index in varobject:
            print(f"{varobject[index].name} = {varobject[index].value}")
            
def WriteLP(m, name):
    m.write(f'C:/Users/AminSalimi/Documents/{name}.lp', format='lp', io_options={"symbolic_solver_labels": True})