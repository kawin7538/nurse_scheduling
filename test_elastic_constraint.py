from pulp import *

model = LpProblem("FUCK1",LpMinimize)

a=LpVariable('a',lowBound=0,upBound=100)
b=LpVariable('b',lowBound=0,upBound=100)

model += (1000*a+1000*b)

model += (a>=10)
model += (b>=10)

# model += (a-b>=5)

c_lhs=LpAffineExpression([(a,1),(b,-1)])
c_rhs=5
c_pre=LpConstraint(e=c_lhs,sense=LpConstraintGE,name="ElasticCompare",rhs=c_rhs)
c_elastic=c_pre.makeElasticSubProblem(penalty=1000,proportionFreeBound=0.02)
model.extend(c_elastic)

model.solve()

print(model)
print(model.objective.value())

for var in model.variables():
    print(f"{var.name}: {var.value()}")
# check constraint values
for name, constraint in model.constraints.items():
    print(f"{name}: {constraint.value()}")