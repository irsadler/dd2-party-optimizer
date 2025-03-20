import streamlit as st
import pandas as pd
import numpy as np
import os
from st_aggrid import AgGrid,GridOptionsBuilder
import query_f
from streamlit.components.v1 import html
from pandasql import sqldf
import xlsxwriter
import io


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


lookup={'none':'',
    'Bounty Hunter': 'BH',
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
token_lookup=['heal','crit','riposte','burn','dodge','block','guarded','strength','speed','stealth','daze','stun',
              'blind','weak','vuln','combo','consecration','bleed','blight','debuff','buff','none']
skill_lookup=['damage', 'crit','none']
path=['Wanderer','Best Available', 'Show All']
stat_lookup=['none','hp','speed','bleed','blight','burn','stun','move','debuff','disease','deathblow','forward', 'backward']
base_party=['Plague Doctor','Grave Robber','Runaway','Hellion']
hero_dat=pd.read_csv(dir+'/character_sheets/hero_data_march_2k25.csv').drop(columns='Unnamed: 0')
stat_dat=pd.read_csv(dir+'/character_sheets/stat_data_march_2k25_v2.csv').drop(columns='Unnamed: 0')

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

 rad=st.radio('level', key='sr',options=['base','upgraded','both'],index=0)

 bc1,bc2=st.columns(2)

 with bc1:
    b = st.button('search', key='sb')
 with bc2:
     bht = st.toggle(label='exclude bounty hunter', value=False, key='bht',
                     help='prevents BH from being included in calculations')
     if bht:
         st.session_state['bht_'] = 'on'
         lookup.pop('Bounty Hunter', None)
     else:
         st.session_state['bht_'] = 'off'

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
    result_ = query_f.describe_team(hero_dat_1,descriptive_stats_1, st.session_state['hero_req'])
    hero_st['result_0']=result_


    c={'high': '#5AE95A', 'low': '#EE4E4E', 'avg': '#C8B8B8'}
    result_.loc['party average']=result_.loc['party average'].map('{:,.2f}'.format)
    result_ = result_.reset_index()
    grid_0 = GridOptionsBuilder.from_dataframe(result_)
    grid_0.configure_auto_height(False)
    grid_0.configure_first_column_as_index(True)
    grid_0.configure_grid_options()
    g_0 = grid_0.build()
    AgGrid(result_, gridOptions=g_0, height=240,
           fit_columns_on_grid_load=False, suppressMovableColumns=True, suppressClickEdit=True,
      alwaysShowHorizontalScroll=True)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        result_.to_excel(writer, sheet_name='Sheet1')
        writer.close()
        st.session_state['buffer'] = buf
        db = st.download_button(
            label="Download as spreadsheet",
            data=st.session_state['buffer'],
            file_name="dd2-party-stats.xlsx",
            mime="application/vnd.ms-excel")

with tab2:
 st.markdown(query_f.read_markdown_file(dir + '/static/text_2.md'), unsafe_allow_html=True,
                help='expand to read more')
 search_5=st.multiselect('exclude heroes', options=lookup.keys(), default='Bounty Hunter',key='search5', help='')
 search_6=st.multiselect('resistances',options=stat_lookup,default=['blight', 'disease'],key='f5',help='the tool will optimize heros for the best average of these input values')
 search_7=st.multiselect('damage',options=skill_lookup,default='damage',key='search7', help='the tool will optimize skills for the best average of these input values')
 search_8=st.multiselect('require skill effect', options=token_lookup, default='bleed',key='search8', help='the tool will try to find skills to suggest that apply (or remove) these values')
 search_9=st.selectbox('filter paths', options=path, key='search9', index=0,help='this will return all paths for the selected heros, the best available path that matches the criteria entered, or wanderer path only')
 rad_2 = st.radio('level', key='slevel', options=['normal', 'mastery'], index=0, help='include mastery skill upgrades in calculation?')

 B=st.button('SEARCH!')
 if B:

  st.session_state['stat_req'] = {'level': rad_2, 'exclude':search_5, 'res': search_6, 'damage': search_7,
                                  'effect': search_8, 'path': search_9}
  search_req=st.session_state['stat_req']
  search_req=query_f.check_for_items(search_req)
  search_dt=query_f.handle_datasets(hero_dat, stat_dat, search_req )
  cols = [i for i in search_req['damage'] + search_req['res'] if i != 'none']
  pysqldf = lambda q: sqldf(q, globals())
  if search_req['path'] == 'Wanderer':
   result_a = query_f.get_path(search_req, search_dt, pysqldf)
  else:
   result_a = search_dt
  if search_req['effect'][0] != 'none':
   result_b = query_f.effect_get(result_a, pysqldf, search_req)
  else:
   result_b = result_a
   result_b['token']=np.repeat('any',result_b.shape[0])
  if search_req["res"][0] != "none" or search_req["damage"][0] != "none":
   result_c = query_f.optimize_skills(search_req, result_b, pysqldf).reset_index().drop_duplicates()
  else:
   result_c = result_b.reset_index().drop_duplicates()
  result_c=result_c[["hero_name","path_name","skill_name","rank","target","type","damage","crit","self","cooldown","target_restriction","uses","hp","speed","bleed","blight","burn","stun","move","debuff","disease","deathblow","forward","backward","token"]]
  if search_req['path'] == 'Best Available':
      result_x_c=query_f.add_remove(result_a,result_c,search_req,pysqldf).drop_duplicates().reset_index().drop(columns='index')
      result_x_c=result_x_c[["hero_name","path_name","skill_name","rank","target","type","damage","crit","self","cooldown","target_restriction","uses","hp","speed","bleed","blight","burn","stun","move","debuff","disease","deathblow","forward","backward","token","token_ct"]]
      xcbest=result_x_c.groupby(['hero_name','path_name']).max(numeric_only=True).sort_values(['token_ct']+cols,ascending=False).reset_index()
      result_cx=xcbest.drop_duplicates(subset=['hero_name']).head(4)
      result_c_x=result_cx[['hero_name','path_name']].merge(result_x_c, on=['path_name','hero_name'])
      result_d=result_c_x.rename(
          columns={'hero_name': 'hero name', 'path_name': 'path name', 'skill_name': 'skill name'})

  elif search_req['path'] == 'Show All':
      result_x_c=query_f.add_remove(result_a,result_c,search_req,pysqldf).drop_duplicates().reset_index().drop(columns='index')
      result_x_c = result_x_c[
          ["hero_name", "path_name", "skill_name", "rank", "target", "type", "damage", "crit", "self", "cooldown",
           "target_restriction", "uses", "hp", "speed", "bleed", "blight", "burn", "stun", "move", "debuff", "disease",
           "deathblow", "forward", "backward", "token", "token_ct"]]
      xcbest=result_x_c.groupby(['hero_name']).max(numeric_only=True).sort_values(['token_ct'] + cols,
                                                                              ascending=False).reset_index().head(4)
      result_c_x=xcbest[['hero_name']].merge(result_x_c, on=['hero_name'])
      result_d = result_c_x.rename(
          columns={'hero_name': 'hero name', 'path_name': 'path name', 'skill_name': 'skill name'})

  elif search_req['path']=='Wanderer':
      result_d = query_f.add_remove(result_a, result_c, search_req, pysqldf)
      result_d = result_d.rename(
          columns={'hero_name': 'hero name', 'path_name': 'path name', 'skill_name': 'skill name'})
  result_d=result_d.dropna(subset='skill name')
  result_d['uses']=result_d['uses'].astype(str)
  st.session_state['result_d'] =result_d[["hero name", "path name", "skill name", "rank", "target", "type", "damage", "crit", "cooldown",
           "target_restriction", "uses", "hp", "speed", "bleed", "blight", "burn", "stun", "move", "debuff", "disease",
           "deathblow", "forward", "backward"]]

  grid_1 = GridOptionsBuilder.from_dataframe(st.session_state['result_d'])
  grid_1.configure_column(field='hero name', header='hero name', editable=False, rowGroup=True, hide=True)
  grid_1.configure_column(field='path name', header='path name', editable=False, rowGroup=True, hide=True)
  grid_1.configure_column(field='index', hide=True)
  g_1 = grid_1.build()

  AgGrid(st.session_state['result_d'], gridOptions=g_1, height=200, fit_columns_on_grid_load=False,
         suppressMovableColumns=True, suppressClickEdit=True)
  buf = io.BytesIO()
  with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        st.session_state['result_d'].to_excel(writer, sheet_name='Sheet1')
        writer.close()
        st.session_state['buffer'] = buf
        db=st.download_button(
            label="Download as spreadsheet",
            data=st.session_state['buffer'],
            file_name="dd2-optimized-party.xlsx",
            mime="application/vnd.ms-excel")


st.markdown(query_f.read_markdown_file(dir+'/static/text_b.md'),unsafe_allow_html=True)