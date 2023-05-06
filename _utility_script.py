from pulp import LpStatus
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def custom_print_model_status(model,file):
    # check environment
    # print(model,file=file)
    # check status of model
    # print(f"status: {LpStatus[model.status]}",file=file)
    #check optimal objective value
    # print(f"Objective: {model.objective.value()}",file=file)
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

def export_model_insight(model):
    ans_dict={
        'work_type':[],
        't':[],
        'shift':[],
        'nurse_id':[],
        'value':[]
    }
    for var in model.variables():
        if 'Nurse' not in var.name:
            continue;
        if 'OFF' in var.name:
            continue;
        if 'elastic' in var.name:
            continue;
        temp_ans_list=var.name.split("_")
        temp_ans_list=temp_ans_list[3:7]+[var.value()]
        for idx,val in enumerate(['work_type','t','shift','nurse_id','value']):
            ans_dict[val].append(temp_ans_list[idx])
    
    ans_df=pd.DataFrame.from_dict(ans_dict)
    ans_df[['t','nurse_id','value']]=ans_df[['t','nurse_id','value']].astype(int)
    ans_df['shift']=pd.Categorical(ans_df['shift'].replace(['0','1','2'],['Morning','Evening','Night']),categories=['Morning','Evening','Night'],ordered=True)
    ans_df['work_type']=pd.Categorical(ans_df['work_type'],categories=['regular','overtime'])
    ans_df=ans_df.sort_values(by=['t','shift','nurse_id']).reset_index(drop=True)

    ans_df.to_csv("output/raw_results.csv",index=False)

    ans_df_wider=ans_df.pivot_table(index=['nurse_id'],columns=['t','shift','work_type'],values=['value'],aggfunc='first',dropna=True)

    ans_df_wider.to_excel("output/results.xlsx")

    ans_df.pivot_table(index='nurse_id',columns=['work_type','shift'],values='value',aggfunc='sum').to_excel("output/summarise_per_nurse.xlsx")

    ans_df.pivot_table(columns=['t','shift'],values=['value'],aggfunc='sum').to_excel("output/summarise_per_shift.xlsx")

    return ans_df.copy()

def export_insight_and_plots(model):
    ans_df=export_model_insight(model)

    ans_df['shift_label']=ans_df['shift'].astype(str).map({
        'Morning':'M',
        'Evening':'E',
        'Night':'N'
    })
    ans_df['shift_label2']="R"
    ans_df.loc[ans_df['work_type']=='overtime','shift_label2']="OT"
    ans_df.loc[ans_df['value']==0,['shift_label','shift_label2']]=None

    ans_df_agg=ans_df.groupby(['t','nurse_id']).agg({'shift_label':list,'shift_label2':list})

    ans_df_agg['shift_label']=ans_df_agg['shift_label'].apply(lambda x: "/".join([i for i in x if i]))
    ans_df_agg.loc[ans_df_agg['shift_label']=="",'shift_label']=None

    ans_df_agg['shift_label2']=ans_df_agg['shift_label2'].apply(lambda x: "/".join([i for i in x if i]))
    ans_df_agg.loc[ans_df_agg['shift_label2']=="",'shift_label2']=None

    ans_df_agg_wide=ans_df_agg.pivot_table(values='shift_label',index='nurse_id',columns='t',aggfunc='first')

    ans_df_agg_wide.to_excel("output/pretty_results.xlsx")

    # sns.heatmap(ans_df_agg_wide)
    fig, ax = plt.subplots(1,figsize=(12,9))
    sns.relplot(ans_df_agg,x='t',y='nurse_id',hue='shift_label',hue_order=['M','E','N','M/E','M/N'])
    plt.gca().invert_yaxis()
    plt.savefig("output/results.png",dpi=320,bbox_inches='tight')

    # ans_df_agg_wide2=ans_df_agg.pivot_table(values='shift_label2',index='nurse_id',columns='t',aggfunc='first')

    fig, ax = plt.subplots(1,figsize=(12,9))
    sns.relplot(ans_df_agg,x='t',y='nurse_id',hue='shift_label2')
    plt.gca().invert_yaxis()
    plt.savefig("output/results_r_ot.png",dpi=320,bbox_inches='tight')