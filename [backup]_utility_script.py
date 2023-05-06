from pulp import LpStatus
import numpy as np
import pandas as pd

def custom_print_model_status(model,file):
    # check environment
    print(model,file=file)
    # check status of model
    print(f"status: {LpStatus[model.status]}",file=file)
    #check optimal objective value
    print(f"Objective: {model.objective.value()}",file=file)
    # check optimal variables
    for var in model.variables():
        print(f"{var.name}: {var.value()}",file=file)
    # check constraint values
    for name, constraint in model.constraints.items():
        print(f"{name}: {constraint.value()}",file=file)

def visualize_nurse_model(model):
    # ans_list=[]
    ans_dict={
        'nurse_type':[],
        'work_type':[],
        't':[],
        'shift':[],
        'nurse_id':[],
        'value':[]
    }
    for var in model.variables():
        temp_ans_list=var.name.split("_")
        temp_ans_list=[temp_ans_list[0]]+temp_ans_list[2:6]+[var.value()]
        for idx, val in enumerate(['nurse_type','work_type','t','shift','nurse_id','value']):
            ans_dict[val].append(temp_ans_list[idx])
        
    ans_df=pd.DataFrame.from_dict(ans_dict)
    ans_df['value']=ans_df['value'].astype(int)
    ans_df['nurse_type_id']=ans_df['nurse_type']+"-"+ans_df['nurse_id']
    ans_df['nurse_type']=pd.Categorical(ans_df['nurse_type'],categories=['Senior','Adult','Junior'],ordered=True)
    ans_df['nurse_id']=ans_df['nurse_id'].astype(int)
    ans_df['shift']=pd.Categorical(ans_df['shift'].replace(['0','1','2'],['Morning','Evening','Night']),categories=['Morning','Evening','Night'],ordered=True)
    ans_df[['t','nurse_id']]=ans_df[['t','nurse_id']].astype(int)
    ans_df.loc[ans_df['value']==1,'value']=ans_df.loc[ans_df['value']==1,'work_type']
    ans_df.loc[ans_df['value']==0,'value']=None
    ans_df=ans_df.sort_values(by=['t','shift','nurse_type','nurse_id']).reset_index(drop=True)
    
    ans_df.to_csv("output/raw_results.csv")

    ans_df_wider=ans_df.pivot_table(index=['nurse_type','nurse_type_id'],columns=['t','shift'],values=['value'],aggfunc='first',dropna=True)
    
    ans_df_wider.to_excel("output/results.xlsx")

    # ans_df.groupby(['nurse_type_id','work_type','shift'],sort=False).agg({'value':'count'}).to_excel("output/summarise_results.xlsx")
    ans_df.pivot_table(index=['nurse_type_id'],columns=['work_type','shift'],values=['value'],aggfunc='count',sort=False).to_excel("output/summarise_results.xlsx")