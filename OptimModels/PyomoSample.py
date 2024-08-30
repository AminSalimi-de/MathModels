from pyomo.environ import *

# Create a model
model = ConcreteModel()

# Define variables
model.x = Var(within=NonNegativeReals)  # x >= 0
model.y = Var(within=NonNegativeReals)  # y >= 0

# Objective function: Maximize 2x + 3y
model.obj = Objective(expr=2*model.x + 3*model.y, sense=maximize)

# Constraints
model.constraint1 = Constraint(expr=model.x + 2*model.y <= 20)
model.constraint2 = Constraint(expr=3*model.x + 4*model.y >= 18)

# Write the model to an LP file
model.write('C:/Users/AminSalimi/Documents/model.lp', format='lp', io_options={'symbolic_solver_labels': True})

# Solve the model using the default solver (e.g., GLPK, if installed)
solver = SolverFactory('highs')
solver.solve(model)

# Print results
print("Objective value:", model.obj())
print("x =", model.x())
print("y =", model.y())

