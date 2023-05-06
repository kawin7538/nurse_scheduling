#%% init library and user-defined variables
from pulp import *
from _utility_script import *

VAR_EPSILON=np.finfo(float).eps

N_DAYS=31
N_WORKING_DAY=20

LIST_DAYS=[*range(N_DAYS)]

N_SHIFT=3
# assign 0 for morning, 1 for evening, 2 for night
LIST_SHIFT=[*range(N_SHIFT)]

N_NURSE=30

LIST_NURSE=[*range(N_NURSE)]

#%% define basic model and some lpVariables

# define minization problem model
model=LpProblem(name="Nurse Scheduling",sense=LpMinimize)

# define regular workload for day t and shift k for nurse i
nurse_workload_regular=LpVariable.dicts("Nurse Workload at regular",(LIST_DAYS,LIST_SHIFT,LIST_NURSE),cat=LpBinary)

# define overtime workload for day t and shift k for nurse i
nurse_workload_overtime=LpVariable.dicts("Nurse Workload at overtime",(LIST_DAYS,LIST_SHIFT,LIST_NURSE),cat=LpBinary)

# define OFF for day t and shift k for nurse i
nurse_off=LpVariable.dicts("Nurse OFF",(LIST_DAYS,LIST_NURSE),cat=LpBinary)

#%% define objective function
# model += (700*lpSum(nurse_workload_overtime)+240*lpSum([nurse_workload_regular[t][k] for t in LIST_DAYS for k in range(1,3)]))
model += (700*lpSum(nurse_workload_overtime))

#%% constraint MUST 1
for t in LIST_DAYS:
    for k in LIST_SHIFT:
        for i in LIST_NURSE:
            model += (nurse_workload_regular[t][k][i]+nurse_workload_overtime[t][k][i]<=1)

#%% constraint MUST 2
for t in LIST_DAYS:
    for i in LIST_NURSE:
        model += (lpSum([nurse_workload_regular[t][k][i] for k in LIST_SHIFT])<=1)

#%% constraint MUST 3
for t in LIST_DAYS[:-1]:
    for i in LIST_NURSE:
        model += (nurse_workload_regular[t][2][i]+nurse_workload_overtime[t][2][i]+nurse_workload_regular[t+1][0][i]+nurse_workload_overtime[t+1][0][i]<=1)

#%% constraint MUST 4
for t in LIST_DAYS:
    for i in LIST_NURSE:
        model += (nurse_workload_regular[t][1][i]+nurse_workload_overtime[t][1][i]+nurse_workload_regular[t][2][i]+nurse_workload_overtime[t][2][i]<=1)

#%% constraint MUST 5
z_must5=LpVariable.dicts("additional variable for MUST 5",(LIST_DAYS,LIST_NURSE))

# iterate for logical AND
for t in LIST_DAYS:
    for i in LIST_NURSE:
        for k in LIST_SHIFT[:-1]:
            model += (z_must5[t][i]>=nurse_workload_regular[t][k][i])
            model += (z_must5[t][i]>=nurse_workload_overtime[t][k][i])
        model += (z_must5[t][i]<=lpSum([nurse_workload_regular[t][k][i] for k in LIST_SHIFT[:-1]])+lpSum([nurse_workload_overtime[t][k][i] for k in LIST_SHIFT[:-1]]))

# iterate for real constraint
for t in LIST_DAYS[:-3]:
    for i in LIST_NURSE:
        model += (lpSum([z_must5[t+l][i] for l in range(4)])<=3)

#%% constraint MUST 6
for t in LIST_DAYS[:-7]:
    for i in LIST_NURSE:
        model += (lpSum([nurse_off[t+l][i] for l in range(7) if t+l<N_DAYS])>=1)

#%% constraint MUST 7
for t in LIST_DAYS[:-1]:
    for i in LIST_NURSE:
        model += (nurse_workload_regular[t][2][i]+nurse_workload_regular[t+1][2][i]+nurse_workload_overtime[t][2][i]+nurse_workload_overtime[t+1][2][i]<=1)

#%% constraint FLEXIBLE 1
for t in LIST_DAYS:
    for k in LIST_SHIFT:
        c_lhs=[(nurse_workload_regular[t][k][i],1) for i in LIST_NURSE] + [(nurse_workload_overtime[t][k][i],1) for i in LIST_NURSE]
        c_lhs=LpAffineExpression(c_lhs)
        c_rhs=7
        c_pre=LpConstraint(e=c_lhs,sense=LpConstraintGE,name=f"MinimumNurseGE7_{t}_{k}",rhs=c_rhs)
        c_elastic=c_pre.makeElasticSubProblem(penalty=2000,proportionFreeBound=0)
        model.extend(c_elastic)

#%% constraint FLEXIBLE 2
for i in LIST_NURSE:
    c_lhs=[(nurse_workload_regular[t][k][i],1) for t in LIST_DAYS for k in LIST_SHIFT]
    c_lhs=LpAffineExpression(c_lhs)
    c_rhs=N_WORKING_DAY
    c_pre=LpConstraint(e=c_lhs,sense=LpConstraintEQ,name=f"MinimumWorkingDay_{i}",rhs=c_rhs)
    c_elastic=c_pre.makeElasticSubProblem(penalty=2000,proportionFreeBound=0)
    model.extend(c_elastic)

#%% constraint FLEXIBLE 3
for t in LIST_DAYS:
    for i in LIST_NURSE:
        c_lhs=[(nurse_workload_regular[t][k][i],1) for k in LIST_SHIFT]+[(nurse_workload_overtime[t][k][i],1) for k in LIST_SHIFT]
        c_lhs=LpAffineExpression(c_lhs)
        c_rhs=1
        c_pre=LpConstraint(e=c_lhs,sense=LpConstraintLE,name=f"LimitationShiftPerDay_{t}_{i}",rhs=c_rhs)
        c_elastic=c_pre.makeElasticSubProblem(penalty=0,proportionFreeBound=1)
        model.extend(c_elastic)

#%% constraint FLEXIBLE 4
z_flexible4=LpVariable.dicts("additional variable for flexible4",(LIST_DAYS,LIST_NURSE),cat=LpBinary)

for t in LIST_DAYS:
    for i in LIST_NURSE:
        for k in LIST_SHIFT:
            model += (z_flexible4[t][i]>=nurse_workload_regular[t][k][i])
            model += (z_flexible4[t][i]>=nurse_workload_overtime[t][k][i])
        model += (z_flexible4[t][i]<=lpSum([nurse_workload_regular[t][k][i] for k in LIST_SHIFT])+lpSum([nurse_workload_overtime[t][k][i] for k in LIST_SHIFT]))

for t in LIST_DAYS[:-2]:
    for i in LIST_NURSE:
        # model += (nurse_off[t][i]+z_flexible4[t+1][i]+nurse_off[t+2][i]<=2)
        c_lhs=[(nurse_off[t][i],1),(z_flexible4[t+1][i],1),(nurse_off[t+2][i],1)]
        c_lhs=LpAffineExpression(c_lhs)
        c_rhs=2
        c_pre=LpConstraint(e=c_lhs,sense=LpConstraintLE,name=f"LimitationOnBreakingType_{t}_{i}",rhs=c_rhs)
        c_elastic=c_pre.makeElasticSubProblem(penalty=2000,proportionFreeBound=0)
        model.extend(c_elastic)

#%% constraint FLEXIBLE 5
for t in LIST_DAYS[:-1]:
    for i in LIST_NURSE:
        c_lhs=[(nurse_workload_regular[t][2][i],1),(nurse_workload_overtime[t][2][i],1),(nurse_workload_regular[t+1][1][i],1),(nurse_workload_overtime[t+1][1][i],1)]
        c_lhs=LpAffineExpression(c_lhs)
        c_rhs=1
        c_pre=LpConstraint(e=c_lhs,sense=LpConstraintLE,name=f"LimitationOnNightThenEvening_{t}_{i}",rhs=c_rhs)
        c_elastic=c_pre.makeElasticSubProblem(penalty=500,proportionFreeBound=0)
        model.extend(c_elastic)

#%% constraint TECHNICAL 1
z_technical1=LpVariable.dicts("additional variable for technical1",(LIST_DAYS,LIST_NURSE),cat=LpBinary)

for t in LIST_DAYS:
    for i in LIST_NURSE:
        for k in LIST_SHIFT:
            model += (z_technical1[t][i]>=nurse_workload_regular[t][k][i])
            model += (z_technical1[t][i]>=nurse_workload_overtime[t][k][i])
        model += (z_technical1[t][i]<=lpSum([nurse_workload_regular[t][k][i] for k in LIST_SHIFT])+lpSum([nurse_workload_overtime[t][k][i] for k in LIST_SHIFT]))
        model += (z_technical1[t][i]+nurse_off[t][i]==1)

#%% solve and visualize

model.writeLP("output/model.lp")

path_cbc=r"D:\Kawin\nurse_scheduling\Cbc-2.10.5-win32-msvc15\bin\cbc.exe"
solver=COIN_CMD(path=path_cbc)
model.solve(solver)

with open("output/model.txt","w") as f:
    # custom_print_model_status(model,f)
    print(model,file=f)
    for var in model.variables():
        print(f"{var.name}: {var.value()}",file=f)
    # check constraint values
    for name, constraint in model.constraints.items():
        print(f"{name}: {constraint.value()}",file=f)

#%%
export_insight_and_plots(model)
#%%