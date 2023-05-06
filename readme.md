# Technical Notes on Nurse Scheduling sys
## from Burke's (2004) there were five criteria
- coverage, different of people scheduled and required
- quality, how fair schedules are
- stability, 
- flexibility,
- cost

## scheduling consists of 3 timeshifts, 8 hours each
- morning
- evening
- night

## two types of work
- regular
- ot

## cost in optimization
- ot, 700 per shift
- evening and night, 240 per shift
- unmeet the minimum workday requirements due to lack of management from chief, 2000 per nurse
- violate some flexible constraints, up to further decision.

> in this programming, the first day is always Sunday

## DEFINITION

$x_{tki}^{r}$ is workload on regular time at day $t$ on shift $k$ for nurse $i$. 

$x_{tki}^{ot}$ is workload on over time at day $t$ on shift $k$ for nurse $i$. 

$x_{ti}^{off}$ is OFF on workload at day $t$ for nurse $i$

## MUST constraints (cannot be resisted in any approaches)
1. only regular or overtime were selected at each timeshift each day
1. only 1 regular shift for a day.
1. cannot work in night then morning of the next day
1. cannot work in evening then night of the same day
1. able to work in morning then evening but not over than 3 consecutive days
1. nurses will receive off days at least once per week
1. cannot work at night for 2 consecutive days

## FLEXIBLE constraints (may be violated but must pay some extra costs)
1. sum of nurses in each shift should not less than 7 (elastic zones [-1,0], violation cost 9000 per event)
1. sum of regular workdays should total regular workday in month (elastic zones [0,0], violation cost 2000 per nurse (per penalitized days))
1. only 1 shift for a day (elastic zones [0,1], no violation cost)
1. avoid off-work-off pattern on 3-day pattern (elastic zones [0,1], no violation cost)
1. cannot work in night then evening of the next day (elastic zones [0,1], no violation cost)

## TECHNICAL constraints (not any description in main constraints but stil essential to fulfill the programming)
1. OFF must be 1 if not any workload appeared
$$
x_{ti}^{off}=
\begin{cases}
1 & \forall x_{t(\cdot) i}^{\cdot}=0 \\
0 & otherwise
\end{cases} 
$$
in this case (including with [this reference](https://math.stackexchange.com/a/2778110)), it may be convert into conditional constraint such that
$$
z_{ti}\le \Sigma_{k}\Sigma_{u\in\{regular,overtime\}}x_{tki}^{u} ;\forall z_{ti}\ge x_{tki}^{u} \\
z_{ti} + x_{ti}^{off}=1
$$
where $z$ is additional binary value.

## my objective function
- least sum cost of all nurses at overtime in a month, plus evening and night at regular shift