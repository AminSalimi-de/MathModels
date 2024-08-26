import highspy
import numpy as np

h = highspy.Highs()

x0 = h.addVariable(lb = 0, ub = 4)
x1 = h.addVariable(lb = 1, ub = 7)

h.addConstr(5 <=   x0 + 2*x1 <= 15)
h.addConstr(6 <= 3*x0 + 2*x1)

h.minimize(x0 + x1)

h.run()

solution = h.getSolution()
basis = h.getBasis()
info = h.getInfo()
model_status = h.getModelStatus()
print('Model status = ', h.modelStatusToString(model_status))
print()
print('Optimal objective = ', info.objective_function_value)
print('Iteration count = ', info.simplex_iteration_count)
print('Primal solution status = ', h.solutionStatusToString(info.primal_solution_status))
print('Dual solution status = ', h.solutionStatusToString(info.dual_solution_status))
print('Basis validity = ', h.basisValidityToString(info.basis_validity))