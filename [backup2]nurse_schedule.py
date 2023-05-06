#%% init library and user-defined variables
from pulp import *
from _utility_script import *

VAR_EPSILON=np.finfo(float).eps

N_DAYS=31

LIST_DAYS=[*range(N_DAYS)]

N_SHIFT=3
# assign 0 for morning, 1 for evening, 2 for night
LIST_SHIFT=[*range(N_SHIFT)]

N_NURSE_SENIOR=14
N_NURSE_ADULT=8
N_NURSE_JUNIOR=5

LIST_NURSE_SENIOR=[*range(N_NURSE_SENIOR)]
LIST_NURSE_ADULT=[*range(N_NURSE_ADULT)]
LIST_NURSE_JUNIOR=[*range(N_NURSE_JUNIOR)]

#%% define basic model and some lpVariables

# define minization problem model
model=LpProblem(name="Nurse Scheduling",sense=LpMinimize)

# define regular workload for day t and shift k for nurse i
nurse_senior_regular=LpVariable.dicts("Senior workload regular",indices=(LIST_DAYS,LIST_SHIFT,LIST_NURSE_SENIOR),cat=LpBinary,lowBound=0,upBound=1)
nurse_adult_regular=LpVariable.dicts("Adult workload regular",(LIST_DAYS,LIST_SHIFT,LIST_NURSE_ADULT),cat=LpBinary,lowBound=0,upBound=1)
nurse_junior_regular=LpVariable.dicts("Junior workload regular",(LIST_DAYS,LIST_SHIFT,LIST_NURSE_JUNIOR),cat=LpBinary,lowBound=0,upBound=1)

# define overtime workload for day t and shift k for nurse i
nurse_senior_overtime=LpVariable.dicts("Senior workload overtime",(LIST_DAYS,LIST_SHIFT,LIST_NURSE_SENIOR),cat=LpBinary,lowBound=0,upBound=1)
nurse_adult_overtime=LpVariable.dicts("Adult workload overtime",(LIST_DAYS,LIST_SHIFT,LIST_NURSE_ADULT),cat=LpBinary,lowBound=0,upBound=1)
nurse_junior_overtime=LpVariable.dicts("Junior workload overtime",(LIST_DAYS,LIST_SHIFT,LIST_NURSE_JUNIOR),cat=LpBinary,lowBound=0,upBound=1)

#%% constraint 1, only regular or overtime were selected
for t in LIST_DAYS:
    for k in LIST_SHIFT:
        for i in LIST_NURSE_SENIOR:
            model += (nurse_senior_regular[t][k][i]+nurse_senior_overtime[t][k][i]<=1)
            # model += (nurse_senior_overtime[t][k][i]-nurse_senior_regular[t][k][i]>=VAR_EPSILON)
        for i in LIST_NURSE_ADULT:
            model += (nurse_adult_regular[t][k][i]+nurse_adult_overtime[t][k][i]<=1)
            # model += (nurse_adult_overtime[t][k][i]-nurse_adult_regular[t][k][i]>=VAR_EPSILON)
        for i in LIST_NURSE_JUNIOR:
            model += (nurse_junior_regular[t][k][i]+nurse_junior_overtime[t][k][i]<=1)
            # model += (nurse_junior_overtime[t][k][i]-nurse_junior_regular[t][k][i]>=VAR_EPSILON)

#%% constraint 2, each shift must consists of junior not more than 1, adult not more than 2, and otherwise seniors
for t in LIST_DAYS:
    for k in LIST_SHIFT:
        # criteria for junior
        model += (lpSum([nurse_junior_regular[t][k],nurse_junior_overtime[t][k]])<=1)
        # criteria for adult
        model += (lpSum([nurse_adult_regular[t][k],nurse_adult_overtime[t][k]])<=3)

#%% constraint 3, sum of nurses in each shift should not less than 7
for t in LIST_DAYS:
    for k in LIST_SHIFT:
        model += (lpSum([nurse_senior_regular[t][k],nurse_senior_overtime[t][k],nurse_adult_regular[t][k],nurse_adult_overtime[t][k],nurse_junior_regular[t][k],nurse_junior_overtime[t][k]])>=7)

#%% constraint 4, sum of work days on regular is only 20 days
# for i in LIST_NURSE_SENIOR:
#     model += (lpSum([nurse_senior_regular[t][k][i] for t in LIST_DAYS for k in LIST_SHIFT])+lpSum([nurse_senior_overtime[t][k][i] for t in LIST_DAYS for k in LIST_SHIFT])>=20)
# for i in LIST_NURSE_ADULT:
#     model += (lpSum([nurse_adult_regular[t][k][i] for t in LIST_DAYS for k in LIST_SHIFT])+lpSum([nurse_adult_overtime[t][k][i] for t in LIST_DAYS for k in LIST_SHIFT])>=20)
# for i in LIST_NURSE_JUNIOR:
#     model += (lpSum([nurse_junior_regular[t][k][i] for t in LIST_DAYS for k in LIST_SHIFT])+lpSum([nurse_junior_overtime[t][k][i] for t in LIST_DAYS for k in LIST_SHIFT])>=20)

# for i in LIST_NURSE_SENIOR:
#     model += (lpSum([nurse_senior_regular[t][k][i] for t in LIST_DAYS for k in LIST_SHIFT])>=20)
# for i in LIST_NURSE_ADULT:
#     model += (lpSum([nurse_adult_regular[t][k][i] for t in LIST_DAYS for k in LIST_SHIFT])>=20)
# for i in LIST_NURSE_JUNIOR:
#     model += (lpSum([nurse_junior_regular[t][k][i] for t in LIST_DAYS for k in LIST_SHIFT])>=20)

#%% constraint 5, sum of hours acquired should be at least 140 hours
for i in LIST_NURSE_SENIOR:
    model += (8*lpSum([nurse_senior_regular[t][k][i] for t in LIST_DAYS for k in LIST_SHIFT])>=140)
for i in LIST_NURSE_ADULT:
    model += (8*lpSum([nurse_adult_regular[t][k][i] for t in LIST_DAYS for k in LIST_SHIFT])>=140)
for i in LIST_NURSE_JUNIOR:
    model += (8*lpSum([nurse_junior_regular[t][k][i] for t in LIST_DAYS for k in LIST_SHIFT])>=140)

#%% constraint 6, only 1 regular shifts for a day
# for t in LIST_DAYS:
#     for i in LIST_NURSE_SENIOR:
#         model += (lpSum([nurse_senior_regular[t][k][i] for k in LIST_SHIFT])+lpSum([nurse_senior_overtime[t][k][i] for k in LIST_SHIFT])<=1)
#     for i in LIST_NURSE_ADULT:
#         model += (lpSum([nurse_adult_regular[t][k][i] for k in LIST_SHIFT])+lpSum([nurse_adult_overtime[t][k][i] for k in LIST_SHIFT])<=1)
#     for i in LIST_NURSE_JUNIOR:
#         model += (lpSum([nurse_junior_regular[t][k][i] for k in LIST_SHIFT])+lpSum([nurse_junior_overtime[t][k][i] for k in LIST_SHIFT])<=1)
for t in LIST_DAYS:
    for i in LIST_NURSE_SENIOR:
        model += (lpSum([nurse_senior_regular[t][k][i] for k in LIST_SHIFT])<=1)
    for i in LIST_NURSE_ADULT:
        model += (lpSum([nurse_adult_regular[t][k][i] for k in LIST_SHIFT])<=1)
    for i in LIST_NURSE_JUNIOR:
        model += (lpSum([nurse_junior_regular[t][k][i] for k in LIST_SHIFT])<=1)

#%% constraint 8, cannot work in night to morning of the next day
for t in LIST_DAYS[:-1]:
    for i in LIST_NURSE_SENIOR:
        model += (nurse_senior_regular[t][2][i]+nurse_senior_overtime[t][2][i]+nurse_senior_regular[t+1][0][i]+nurse_senior_overtime[t+1][0][i]<=1)
    for i in LIST_NURSE_ADULT:
        model += (nurse_adult_regular[t][2][i]+nurse_adult_overtime[t][2][i]+nurse_adult_regular[t+1][0][i]+nurse_adult_overtime[t+1][0][i]<=1)
    for i in LIST_NURSE_JUNIOR:
        model += (nurse_junior_regular[t][2][i]+nurse_junior_overtime[t][2][i]+nurse_junior_regular[t+1][0][i]+nurse_junior_overtime[t+1][0][i]<=1)

#%% constraint 9, cannot work in night then evening of the next day
for t in LIST_DAYS[:-1]:
    for i in LIST_NURSE_SENIOR:
        model += (nurse_senior_regular[t][2][i]+nurse_senior_overtime[t][2][i]+nurse_senior_regular[t+1][1][i]+nurse_senior_overtime[t+1][1][i]<=1)
    for i in LIST_NURSE_ADULT:
        model += (nurse_adult_regular[t][2][i]+nurse_adult_overtime[t][2][i]+nurse_adult_regular[t+1][1][i]+nurse_adult_overtime[t+1][1][i]<=1)
    for i in LIST_NURSE_JUNIOR:
        model += (nurse_junior_regular[t][2][i]+nurse_junior_overtime[t][2][i]+nurse_junior_regular[t+1][1][i]+nurse_junior_overtime[t+1][1][i]<=1)

#%% constraint 10, cannot work in evening then night of the next day
for t in LIST_DAYS[:-1]:
    for i in LIST_NURSE_SENIOR:
        model += (nurse_senior_regular[t][1][i]+nurse_senior_overtime[t][1][i]+nurse_senior_regular[t+1][2][i]+nurse_senior_overtime[t+1][2][i]<=1)
    for i in LIST_NURSE_ADULT:
        model += (nurse_adult_regular[t][1][i]+nurse_adult_overtime[t][1][i]+nurse_adult_regular[t+1][2][i]+nurse_adult_overtime[t+1][2][i]<=1)
    for i in LIST_NURSE_JUNIOR:
        model += (nurse_junior_regular[t][1][i]+nurse_junior_overtime[t][1][i]+nurse_junior_regular[t+1][2][i]+nurse_junior_overtime[t+1][2][i]<=1)

#%% constraint 11, able to work in morning then evening but not over than 3 consecutive days
for t in LIST_DAYS[:-2]:
    for i in LIST_NURSE_SENIOR:
        model += (lpSum([nurse_senior_regular[t+l][k][i] for l in range(3) for k in range(2)])+lpSum([nurse_senior_overtime[t+l][k][i] for l in range(3) for k in range(2)])<=5)
    for i in LIST_NURSE_ADULT:
        model += (lpSum([nurse_adult_regular[t+l][k][i] for l in range(3) for k in range(2)])+lpSum([nurse_adult_overtime[t+l][k][i] for l in range(3) for k in range(2)])<=5)
    for i in LIST_NURSE_JUNIOR:
        model += (lpSum([nurse_junior_regular[t+l][k][i] for l in range(3) for k in range(2)])+lpSum([nurse_junior_overtime[t+l][k][i] for l in range(3) for k in range(2)])<=5)

#%% constraint 12, nurses should work at morning between 7 to 9 days
# for i in LIST_NURSE_SENIOR:
#     model += (lpSum([nurse_senior_regular[t][0][i]])>=7)
#     model += (lpSum([nurse_senior_regular[t][0][i]])<=9)

#%% define objective function
model += (lpSum([nurse_senior_regular,nurse_senior_overtime,nurse_adult_regular,nurse_adult_overtime,nurse_junior_regular,nurse_junior_overtime]))

#%% solve and visualize

with open("output/model.txt","w") as f:
    print(model,file=f)
model.writeLP("output/model.lp")

path_cbc=r"D:\Kawin\nurse_scheduling\Cbc-2.10.5-win32-msvc15\bin\cbc.exe"
solver=COIN_CMD(path=path_cbc)
model.solve(solver)

visualize_nurse_model(model)
#%%