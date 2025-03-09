import streamlit as st
import pandas as pd
import os
from st_aggrid import AgGrid,GridOptionsBuilder
import query_f
from streamlit.components.v1 import html
from pandasql import sqldf
from streamlit_extras.badges import badge

dir=os.getcwd()
st.set_page_config( layout='wide')
img_1=query_f.img_to_bytes(dir+'/static/Radiant_torch_L1.png')
pg1="""<style>
    #content {{
        position: relative;
    }}
    #content img {{
        position: absolute;
        top: 0px;
        right: 0px;
    }}
</style>
<div id="content">
   <a href='https://darkestdungeon.wiki.gg/'> <img src='data:image/png;base64,{img}' class="ribbon" height="100",alt='DD Wiki'/></a>
</div>""".format(img=img_1)
title_container = st.container(key='title_cont')
tc1,tc2=st.columns(2)
with title_container:
    with tc1:
        st.title('Darkest Dungeon 2 Team Builder', anchor=None, help=None)
    with tc2:
        html(pg1,height=100)


lookup={'Bounty Hunter': 'BH',
 'Crusader': 'Cru',
 'Duelist': 'Duel',
 'Flagellant': 'Flag',
 'Grave Robber': 'GR',
 'Hellion': 'Hel',
 'Highwayman': 'Hwm',
 'Jester': 'Jest',
 'Leper': 'Lep',
 'Man-at-Arms': 'MAA',
 'Occultist': 'Occ',
 'Plague Doctor': 'PD',
 'Runaway': 'Run',
 'Vestal': 'Vest'}
column_config={'value': st.column_config.NumberColumn(format='{:.2f}')}
token_lookup=['heal','crit','riposte','dodge','block','guarded','strength','speed','stealth','daze','stun',
              'blind','weak','vuln','combo','consecration','bleed','blight','debuff','buff','']
skill_lookup=['damage', 'crit','']
path=['Wanderer','Best Available', 'Show All']
stat_lookup=['','hp','speed','bleed','blight','burn','stun','move','debuff','disease','deathblow','forward', 'backward']
base_party=['Plague Doctor','Grave Robber','Runaway','Hellion']
hero_dat=pd.read_csv(dir+'/character_sheets/hero_data_march_2k25.csv').drop(columns='Unnamed: 0')
stat_dat=pd.read_csv(dir+'/character_sheets/stat_data_march_2k25.csv').drop(columns='Unnamed: 0')

bht=st.toggle(label='exclude bounty hunter', value=False, key='bht', help='prevents BH from appearing in any results')
if bht:
 st.session_state['bht_']='on'
 lookup.pop('Bounty Hunter', None)
else:
 st.session_state['bht_']='off'

a=pd.DataFrame(columns=['name'])
tab1,tab2=st.tabs(['team rater','build team'])

with (tab1):

 st.markdown(query_f.read_markdown_file(dir+'/static/text_1.md'),unsafe_allow_html=True, help='expand to read more')
 hc4,hc3,hc2,hc1=st.columns(spec=4)
 a=list(lookup.keys())
 with hc1:
  select_1=st.selectbox(label='select hero', options=lookup.keys(),key='h1',index=a.index('Hellion'))
 with hc2:
  select_2=st.selectbox(label='select hero', options=lookup.keys(),key='h2',index=a.index('Runaway'))
 with hc3:
  select_3=st.selectbox(label='select hero', options=lookup.keys(),key='h3',index=a.index('Grave Robber'))
 with hc4:
  select_4=st.selectbox(label='select hero', options=lookup.keys(),key='h4',index=a.index('Plague Doctor'))

 b=st.button('search',key='sb')

 rad=st.radio('level', key='sr',options=['base','upgraded','both'],index=0)

 st.session_state['hero_req'] = {'bht': st.session_state['bht_'], 'rad': rad, 'h1': select_1, 'h2': select_2,
                                 'h3': select_3, 'h4': select_4}
 if b:
    hero_st=st.session_state['hero_req']
    hero_dat_1=query_f.drop_cols(hero_dat,hero_st['rad'])
    hero_dat_1=hero_dat_1.rename(columns={'name':'hero_name'})
    descriptive_stats_1 = query_f.drop_cols(hero_dat.describe(),hero_st['rad'])
    if hero_st['bht']=='on':
     hero_dat_1=hero_dat_1[hero_dat_1['hero_name']!='Bounty Hunter']
    h_desribe = hero_dat_1.describe()
    result_ = query_f.describe_team(h_desribe, descriptive_stats_1)
    hero_st['result_0']=result_
    result_.index=['stat', 'rating']

    c={'high': '#5AE95A', 'low': '#EE4E4E', 'avg': '#C8B8B8'}
    result_.loc['stat']=result_.loc['stat'].map('{:,.2f}'.format)
    result_ = result_.reset_index()
    grid_0 = GridOptionsBuilder.from_dataframe(result_)
    grid_0.configure_auto_height(False)
    grid_0.configure_first_column_as_index(True)
    grid_0.configure_grid_options()
    g_0 = grid_0.build()
    AgGrid(result_, gridOptions=g_0, height=110,
           fit_columns_on_grid_load=False, suppressMovableColumns=True, suppressClickEdit=True,
      alwaysShowHorizontalScroll=True)

with tab2:
 st.markdown(query_f.read_markdown_file(dir + '/static/text_2.md'), unsafe_allow_html=True,
                help='expand to read more')
 search_6=st.multiselect('resistances',options=stat_lookup,default=['blight', 'disease'],key='f5',help='the tool will optimize heros for the best average of these input values')
 search_7=st.multiselect('damage',options=skill_lookup,default='damage',key='search7', help='the tool will optimize skills for the best average of these input values')
 search_8=st.multiselect('require skill effect', options=token_lookup, default='',key='search8', help='the tool will try to find skills to suggest that apply (or remove) these values')
 search_9=st.selectbox('filter paths', options=path, key='search9', index=0,help='this will return all paths for the selected heros, the best available path that matches the criteria entered, or wanderer path only')
 rad_2 = st.radio('level', key='slevel', options=['base', 'upgraded'], index=0)

 B=st.button('SEARCH!')
 if B:
  st.session_state['stat_req'] = {'level': rad_2, 'res': search_6, 'damage': search_7,
                                  'effect': search_8, 'path': search_9}
  search_req=st.session_state['stat_req']

  search_dt=query_f.handle_datasets(hero_dat, stat_dat, search_req,st.session_state['bht'])

  pysqldf = lambda q: sqldf(q, globals())
  if search_req['path'] == 'Wanderer':
   result_a = query_f.get_path(search_req, search_dt, pysqldf)
  else:
   result_a = search_dt
  if search_req['effect'] != "":
   result_b = query_f.effect_get(result_a, pysqldf, search_req)
  else:
   result_b = result_a
  if search_req["res"][0] != "" or search_req["damage"][0] != "":
   result_c = query_f.optimize_skills(search_req, result_b, pysqldf).reset_index()
  else:
   result_c = result_b
  if search_req['path'] == 'Best Available':
   result_c_x = result_c.groupby(['hero_name', 'skill_name']).max(numeric_only=True).reset_index()
   result_c = result_c_x[['skill_name', 'index']].merge(result_c, on='index', how='left')
   result_c = result_c.drop(columns=['index', 'skill_name_x']).rename(columns={'skill_name_y': 'skill_name'})
  if search_req['path'] == 'Show All':
   result_d = result_c.drop(columns='index')
  else:
   result_d = query_f.add_remove(result_a, result_c, search_req, pysqldf)
   result_d=result_d.head(16).rename(columns={'hero_name':'hero name','path_name':'path name','skill_name':'skill name'})
  st.session_state['result_d']=result_d.dropna(subset='skill name')

  grid_1=GridOptionsBuilder.from_dataframe(st.session_state['result_d'])
  grid_1.configure_column(field='hero name',header='hero name', editable=False,rowGroup=True,hide=True)
  grid_1.configure_column(field='path name',header='path name', editable=False,rowGroup=True,hide=True)
  grid_1.configure_column(field='index',hide=True)
  g_1 = grid_1.build()

  AgGrid(st.session_state['result_d'].drop(columns='index'),gridOptions=g_1,height=200,fit_columns_on_grid_load=True,suppressMovableColumns=True,suppressClickEdit=True)


badge(type="github", name="irsadler/dd2-party-optimizer")