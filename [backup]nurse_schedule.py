#%%
from pulp import *
from _utility_script import *

N_DAYS_IN_MONTH=30

LIST_DAYS=[*range(N_DAYS_IN_MONTH)]

N_NURSE_SENIOR=18
N_NURSE_ADULT=8
N_NURSE_JUNIOR=5

LIST_NURSE_SENIOR=[*range(N_NURSE_SENIOR)]
LIST_NURSE_ADULT=[*range(N_NURSE_ADULT)]
LIST_NURSE_JUNIOR=[*range(N_NURSE_JUNIOR)]

# define minization problem model
model=LpProblem(name="Nurse Scheduling",sense=LpMinimize)

# define workload variable for seniors
nurse_senior_morning=LpVariable.dicts("Senior workload at Morning",(LIST_DAYS,LIST_NURSE_SENIOR),cat=LpInteger,lowBound=0,upBound=1)
nurse_senior_evening=LpVariable.dicts("Senior workload at Evening",(LIST_DAYS,LIST_NURSE_SENIOR),cat=LpInteger,lowBound=0,upBound=1)
nurse_senior_night=LpVariable.dicts("Senior workload at Night",(LIST_DAYS,LIST_NURSE_SENIOR),cat=LpInteger,lowBound=0,upBound=1)
nurse_senior_off=LpVariable.dicts("Senior workload at OFF",(LIST_DAYS,LIST_NURSE_SENIOR),cat=LpInteger,lowBound=0,upBound=1)

# define workload variable for adults
nurse_adult_morning=LpVariable.dicts("Adult workload at Morning",(LIST_DAYS,LIST_NURSE_ADULT),cat=LpInteger,lowBound=0,upBound=1)
nurse_adult_evening=LpVariable.dicts("Adult workload at Evening",(LIST_DAYS,LIST_NURSE_ADULT),cat=LpInteger,lowBound=0,upBound=1)
nurse_adult_night=LpVariable.dicts("Adult workload at Night",(LIST_DAYS,LIST_NURSE_ADULT),cat=LpInteger,lowBound=0,upBound=1)
nurse_adult_off=LpVariable.dicts("Adult workload at OFF",(LIST_DAYS,LIST_NURSE_ADULT),cat=LpInteger,lowBound=0,upBound=1)

# define workload variable for juniors
nurse_junior_morning=LpVariable.dicts("Junior workload at Morning",(LIST_DAYS,LIST_NURSE_JUNIOR),cat=LpInteger,lowBound=0,upBound=1)
nurse_junior_evening=LpVariable.dicts("Junior workload at Evening",(LIST_DAYS,LIST_NURSE_JUNIOR),cat=LpInteger,lowBound=0,upBound=1)
nurse_junior_night=LpVariable.dicts("Junior workload at Night",(LIST_DAYS,LIST_NURSE_JUNIOR),cat=LpInteger,lowBound=0,upBound=1)
nurse_junior_off=LpVariable.dicts("Junior workload at OFF",(LIST_DAYS,LIST_NURSE_JUNIOR),cat=LpInteger,lowBound=0,upBound=1)

# define objective function, least work-person in a month
model += (lpSum(nurse_senior_morning)+lpSum(nurse_senior_evening)+lpSum(nurse_senior_night)+lpSum(nurse_adult_morning)+lpSum(nurse_adult_evening)+lpSum(nurse_adult_night)+lpSum(nurse_junior_morning)+lpSum(nurse_junior_evening)+lpSum(nurse_junior_night))

# constrant 1, no more than 1 junior and no more than 2 adults in shift
for t in LIST_DAYS:
    for nurse_junior, shift_label in zip([nurse_junior_morning,nurse_junior_evening,nurse_junior_night],["morning","evening","night"]):
        model += (lpSum(nurse_junior[t])<=1,f"limit count of junior in {shift_label} shift of day {t}")
    for nurse_adult, shift_label in zip([nurse_adult_morning,nurse_adult_evening,nurse_adult_night],["morning","evening","night"]):
        model += (lpSum(nurse_adult[t])<=2,f"upper limit count of adult in {shift_label} shift of day {t}")

# constraint 2, sum of nurse each shift not less than 7
for t in LIST_DAYS:
    model += (lpSum(nurse_junior_morning[t])+lpSum(nurse_adult_morning[t])+lpSum(nurse_senior_morning[t])>=7,f"require nurses in morning of day {t}")
    model += (lpSum(nurse_junior_evening[t])+lpSum(nurse_adult_evening[t])+lpSum(nurse_senior_evening[t])>=7,f"require nurses in evening of day {t}")
    model += (lpSum(nurse_junior_night[t])+lpSum(nurse_adult_night[t])+lpSum(nurse_senior_night[t])>=7,f"require nurses in night of day {t}")

# constraint 3, sum of work days is at least 20 days
# for i in LIST_NURSE_SENIOR:
#     model += (lpSum([nurse_senior_morning[t][i] for t in LIST_DAYS])+lpSum([nurse_senior_evening[t][i] for t in LIST_DAYS])+lpSum([nurse_senior_night[t][i] for t in LIST_DAYS])>=20,f"sum of work days for senior nurse {i} at least 20 days")
# for i in LIST_NURSE_ADULT:
#     model += (lpSum([nurse_adult_morning[t][i] for t in LIST_DAYS])+lpSum([nurse_adult_evening[t][i] for t in LIST_DAYS])+lpSum([nurse_adult_night[t][i] for t in LIST_DAYS])>=20,f"sum of work days for adult nurse {i} at least 20 days")
# for i in LIST_NURSE_JUNIOR:
#     model += (lpSum([nurse_junior_morning[t][i] for t in LIST_DAYS])+lpSum([nurse_junior_evening[t][i] for t in LIST_DAYS])+lpSum([nurse_junior_night[t][i] for t in LIST_DAYS])>=20,f"sum of work days for junior nurse {i} at least 20 days")

# constraint 4, sum of hour acquire at least 140 hours
for i in LIST_NURSE_SENIOR:
    model += (8*lpSum([nurse_senior_morning[t][i] for t in LIST_DAYS])+8*lpSum([nurse_senior_evening[t][i] for t in LIST_DAYS])+8*lpSum([nurse_senior_night[t][i] for t in LIST_DAYS])>=140,f"sum of hour acquire for senior nurse {i} at least 120 hours")
for i in LIST_NURSE_ADULT:
    model += (8*lpSum([nurse_adult_morning[t][i] for t in LIST_DAYS])+8*lpSum([nurse_adult_evening[t][i] for t in LIST_DAYS])+8*lpSum([nurse_adult_night[t][i] for t in LIST_DAYS])>=140,f"sum of hour acquire for adult nurse {i} at least 120 hours")
for i in LIST_NURSE_JUNIOR:
    model += (8*lpSum([nurse_junior_morning[t][i] for t in LIST_DAYS])+8*lpSum([nurse_junior_evening[t][i] for t in LIST_DAYS])+8*lpSum([nurse_junior_night[t][i] for t in LIST_DAYS])>=140,f"sum of hour acquire for junior nurse {i} at least 120 hours")

# constraint 5, only one shift for a day
for t in LIST_DAYS:
    for i in LIST_NURSE_SENIOR:
        model += (lpSum(nurse_senior_morning[t][i])+lpSum(nurse_senior_evening[t][i])+lpSum(nurse_senior_night[t][i])<=1,f"only one shift a day for senior nurse {i} at time {t}")
    for i in LIST_NURSE_ADULT:
        model += (lpSum(nurse_adult_morning[t][i])+lpSum(nurse_adult_evening[t][i])+lpSum(nurse_adult_night[t][i])<=1,f"only one shift a day for adult nurse {i} at time {t}")
    for i in LIST_NURSE_JUNIOR:
        model += (lpSum(nurse_junior_morning[t][i])+lpSum(nurse_junior_evening[t][i])+lpSum(nurse_junior_night[t][i])<=1,f"only one shift a day for junior nurse {i} at time {t}")

# constraint 14, nightshift limitation
for t in LIST_DAYS[:-1]:
    for i in LIST_NURSE_SENIOR:
        model += (nurse_senior_night[t][i]+nurse_senior_night[t+1][i]<=1,f"nightshift limitation from day {t} to {t+1} of senior nurse {i}")
    for i in LIST_NURSE_ADULT:
        model += (nurse_adult_night[t][i]+nurse_adult_night[t+1][i]<=1,f"nightshift limitation from day {t} to {t+1} of adult nurse {i}")
    for i in LIST_NURSE_JUNIOR:
        model += (nurse_junior_night[t][i]+nurse_junior_night[t+1][i]<=1,f"nightshift limitation from day {t} to {t+1} of junior nurse {i}")

# solve integer programming
model.solve()

# %%
visualize_nurse_model(model)