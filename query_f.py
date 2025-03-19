import numpy as np
import pandas as pd
import streamlit as st
from pandasql import sqldf
from pathlib import Path
import base64
import re

#functions in app

def random_(a):
    #not implemented
    rng = np.random.default_rng()
    return rng.choice(a, 4, replace=False)

def describe_team(team,descriptive_stats, details):
    #return summarized comparitive stats for input characters
    team_n=[details['h1'],details['h2'],details['h3'],details['h4']]
    team=team[(team['hero_name'].isin(team_n))]
    team_descriptive = team.describe()
    l = descriptive_stats.loc['25%']
    h = descriptive_stats.loc['75%']
    mean=team_descriptive.loc['mean']
    tags=[]
    lcomp=mean < l
    hcomp=mean > h
    for i in range(mean.shape[0]):
        if lcomp[i]==True:
            tags.append([round(mean[i],2),'low'])
        elif hcomp[i]==True:
            tags.append([round(mean[i],2),'high'])
        else:
            tags.append([round(mean[i],2),'avg'])
    stats_=pd.DataFrame(index=descriptive_stats.columns,data=tags,columns=['value','tag'])
    return stats_.T

def drop_cols(hero_skills, level_):
    if level_ == 'normal' or level_=='base':
        c = hero_skills.filter(like='upgraded').columns
        hero_skills = hero_skills.drop(columns=c)
        hero_skills.columns = [re.sub(r'^base_.*?', '', i) for i in hero_skills.columns]

    if level_ == 'mastery' or level_=='upgraded':
        c = hero_skills.filter(like='base').columns
        c = [i.replace(r'$_', '') for i in c]
        hero_skills = hero_skills.drop(columns=c)
        hero_skills.columns = [re.sub(r'^upgraded_.*?', '', i) for i in hero_skills.columns]
    else:
        hero_skills=hero_skills
    return hero_skills

def cleanup_n(tst):
    v=[]
    for i in tst:
        if len(i)>1:
            x=i.split('-')
            a=int(x[0])
            b=int(x[1])
            v.append((b+a)/2)
        else:
            v.append(float(i))
    return v

def handle_datasets(stats,skills,search_req):
    stats = stats.rename(columns={'name': 'hero_name'})
    search_dt = skills.merge(stats, on='hero_name')
    if search_req['exclude'][0]!='none':
        search_dt=search_dt[~(search_dt['hero_name'].isin(search_req['exclude']))]
    search_dt = drop_cols(search_dt, search_req['level'])
    search_dt['damage'] = cleanup_n(search_dt['damage'].fillna(0).astype(str))
    search_dt = pd.concat([search_dt, search_dt['self'].fillna('') + search_dt['effect'].fillna('')], axis=1)
    search_dt = search_dt.rename(columns={0: 'effect_str'})
    search_dt['effect_str'] = search_dt['effect_str'].str.lower()
    search_dt['skill_name']=search_dt['skill_name'].str.strip("'")
    search_dt=search_dt[search_dt['skill_name']!='Riposte Attack']
    return search_dt

def get_path(search_req,search_dt,pysqldf):
    q1="select * from search_dt where path_name='{}'".format(search_req['path'])
    df1=pysqldf(q1)
    return df1

def effect_get(result_a,pysqldf,search_req):
    df2=pd.DataFrame()
    for i in search_req['effect']:
        q2="select *, '{}' as token from result_a where effect_str like '%{}%'".format(i,i)
        df2=pd.concat([df2,pysqldf(q2)])
    return df2

def optimize_skills(search_req,result_b,pysqldf):
    x=search_req["res"]+search_req["damage"]
    X3= ', '.join("{}".format(item) for item in x if item!='' and item!='none')
    X2 = [item+' DESC' for item in x if item!='' and item!='none']
    X=', '.join("{}".format(item) for item in X2 if item!='' and item!='none')

    q4="""SELECT r.hero_name,r.skill_name,r.path_name,{}
    FROM
    (
        SELECT
            r.*,
            ROW_NUMBER() OVER(PARTITION BY r.hero_name,r.path_name,r.skill_name
                              ORDER BY {}) rn
        FROM result_b r
    ) r
    WHERE r.rn <= 4
    ORDER BY {},r.hero_name""".format(X3,X,X)
    df3=pysqldf(q4)
    df3=df3[df3['hero_name'].isin(df3['hero_name'].value_counts()[:4].index)]
    return df3

def add_remove(result_a,result_c,search_req,pysqldf):
    name_=result_c.hero_name.unique()
    x=search_req["res"]+search_req["damage"]
    X=', '.join("{}".format(item) for item in x if item!='' and item!='none')
    if X=='':
        X='hero_name'
    new_skill=pd.DataFrame()
    for i in name_:
        tmp=result_c[result_c['hero_name']==i]
        skill_=tmp['skill_name'].drop_duplicates().tolist()
        count_=tmp.shape[0]

        if len(skill_)>1:
           skill_=tuple(skill_)
        else:
            skill_=str('("'+skill_[0]+'")')
        q5="""select * 
        from(select hero_name, skill_name,path_name, {}
        from result_a
        where hero_name='{}' 
        order by {}) t
        where skill_name not in {}""".format(X,i,X,skill_)
        if count_<4:
            #simply get the next n skills in line that isnt already in list
            n=4-count_
            st.write(n,pysqldf(q5)[0:n])
            tmp=pd.concat([tmp,pysqldf(q5)[0:n]])
        elif count_>4:
            #drop lowest skill
            n=count_-4
            tmp=tmp.head(-n)
        else:
            #dont worry about it
            tmp=tmp
        new_skill=pd.concat([new_skill,tmp])
    return new_skill

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

def handle_error(search_req, exit_code=1):

    st.write("Error generating, probably you have selected incompatible tokens out of this list: {}".format(search_req))
    st.write(st.session_state['stat_req'])
    st.stop()