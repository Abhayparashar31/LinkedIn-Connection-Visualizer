from zipfile import ZipFile
import pandas as pd
import streamlit as st
import numpy as np
import plotly
import plotly.express as px
from pathlib import Path
import datetime
from pyvis.network import Network
import networkx as nx
import streamlit.components.v1 as components
import random


####################################################
####### Extracts Data From Uploaded Zip File #######
####################################################
def get_data(file):
    if file is not None:
        with ZipFile(file,"r") as zipobj:
            zipobj.extractall("data")
        
        for p in Path("./data").glob("*.csv"):
            connections_csv = p.name

        df = pd.read_csv(f'data/{connections_csv}',skiprows=3)

        return df
    
#####################################################
########## Cleanes Data #############################
#####################################################

def clean_data(df):
    ## Concatination First Name and Last Name as Name
    df['Name'] = df['First Name']+ " "+df['Last Name']
    ## Renaming and Converting Connected On column into datetime
    df['Connected_on'] = pd.to_datetime(df['Connected On'])

    ## Dropping Unneccesary Columns
    df = df.drop(['First Name','Last Name','Connected On'],axis=1)
    return df


#######################################################
############# KEY INFO ################################
#######################################################
def info(df):
    top_position = df['Position'].value_counts().index[0]
    top_company = df['Company'].value_counts().index[0]
    second_company =  df['Company'].value_counts().index[1]
    total_connections = len(df)
    

    cur_month = datetime.datetime.now().month
    cur_year = datetime.datetime.now().year
    cur_day = datetime.datetime.now().day

    this_month_df = df[(df["Connected_on"].dt.month == cur_month) & (df["Connected_on"].dt.year == cur_year) ]
    today_df = df[(df["Connected_on"].dt.month == cur_month)& (df["Connected_on"].dt.year == cur_year)& (df['Connected_on'].dt.day==cur_day)]

    return top_position, top_company, second_company, total_connections, this_month_df, today_df


###################################################
### GENERATE INFORMATION ABOUT FIRST CONNECTION ###
###################################################    
def info_first_conn(df):

    first_conn_name = df['Name'][len(df)-1]
    first_conn_pos = df[df['Name']==first_conn_name]['Position'].values[0]
    first_conn_comp = df[df['Name']==first_conn_name]['Company'].values[0] 

    first_conn_date_ts = df['Connected_on'][len(df)-1]
    first_conn_date = first_conn_date_ts.strftime("%d-%m-%Y")
    today = datetime.datetime.today().strftime('%d-%m-%Y') 
    gap = datetime.datetime.now()-first_conn_date_ts
    gap = gap.days
    return first_conn_name,first_conn_date,first_conn_comp,gap,first_conn_comp,first_conn_pos

####################################################
### GENERATE INFORMATION ABOUT NEWEST CONNECTION ###
####################################################

def info_newest_conn(df):
    ################# Newest Connection #########################
    new_conn_name = df['Name'][0]
    new_conn_pos = df[df['Name']==new_conn_name]['Position'].values[0]
    new_conn_comp = df[df['Name']==new_conn_name]['Company'].values[0]
    return new_conn_name,new_conn_pos,new_conn_comp    

###################################################
#### ADDS NEW COLUMNS INSIDE CLEANED DATAFRAME ####
###################################################

def add_cols_y_m_d(df):
        df['connected_year'] = pd.to_datetime(df['Connected_on']).dt.year
        df['connected_month'] = pd.to_datetime(df['Connected_on']).dt.month
        df['connected_day'] = pd.to_datetime(df['Connected_on']).dt.day
        df['connected_date'] = pd.to_datetime(df['Connected_on'])
        df['day_name'] = pd.to_datetime(df['Connected_on']).dt.day_name()

        connected_data = df['Connected_on'].value_counts()
        max_people_connect_date = connected_data.index[0].strftime('%d %B %Y')
        max_people_connect_count = connected_data.values[0]
        return df,max_people_connect_date,max_people_connect_count

###################################################
######## PLOTS BAR GRAPH ##########################
###################################################

def plot_bar(df,col,val):
    top_companies = df[col].value_counts().iloc[:val]
    fig = px.bar(x=top_companies.index,y=top_companies.values,
            labels={
                'x':f'{col}',
                'y':'Number of Connections'
            })
    return fig

###################################################
######## GENERATE DATA FOR SELECTION ##############
###################################################

def generate_list(selection,df,col):
    comsecdf = df[df[col]==selection]
    comsecdf['Connected_on'] = comsecdf['Connected_on'].apply(lambda x:x.strftime('%d-%m-%Y'))
    comsecdf = comsecdf[['Name','Position','Connected_on','Email Address','Company']]

    return comsecdf

###################################################
######## GENERATE DATA FOR COLUMN VALUE COUNT #####
###################################################
def generate_data(df,col):
    temp = df[col].value_counts()
    temp = temp.reset_index()
    temp = temp.rename(columns={f"{col}":"Number of Connections"})
    temp = temp.set_index("index")
    return temp

###################################################
#### BUILD CHECKBOX AND GENERATE DATA FOR THEM ####
###################################################
def build(col,clean_df,val):
    fig = plot_bar(clean_df,col,val)
    st.plotly_chart(fig,transparent=True,use_container_width=True)

    ## It can be used to quickly know whether someone from a company you know or not. (for referral, etc.)
    cc1, cc2 = st.columns(2)
    with cc1:
        comDetail = st.checkbox('More Details',key=f'{col}')
    if comDetail:
        companies_lst = list(clean_df[col].unique())
        selection = st.selectbox(f'Choose a {col}',companies_lst)
        company_members_list = generate_list(selection,clean_df,col)
        st.write(company_members_list)

    with cc2:
        comData = st.checkbox(f'View Top {col} Data',key=f'{col}')
    if comData:
        data = generate_data(clean_df,col)
        st.write(data)


###################################################
######## PLOT CONNECTIONS ON DIFFERENT MONTHS #####
###################################################
def plot_connections_on_different_months(df):
    data = df['connected_month'].value_counts()
    fig = px.bar(x = data.index, y=data.values,labels={
        'x':'Month',
        'y':'Number of Connections'})

    fig.update_xaxes(tickvals=[1,2,3,4,5,6,7,8,9,10,11,12],
                    ticktext=['Jan','Feb','Mar','Apr','May','june','july','Aug','Sep','Oct','Nov','Dec'])

    return fig

###################################################
######## PLOT CONNECTIONS ON DIFFERENT WEEKDAYS ###
###################################################
def plot_connections_on_different_weekdays(df):
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    data = df['day_name'].value_counts()
    weekday_df = data.reset_index()
    weekday_df['index'] = pd.Categorical(weekday_df['index'],categories=day_names,ordered=True)
    weekday_df = weekday_df.sort_values('index')
    weekday_df = weekday_df.rename(columns = {
        "index":'week_day',
        "day_name":"count"
    })
    
    fig = px.bar(x = weekday_df['week_day'], y=weekday_df['count'],labels={
        'x':'Day',
        'y':'Number of Connections'
    })    
    return fig


###################################################
######## PLOTS TIMELINE OF CONNECTIONS ############
###################################################
def get_connectios_count_df(df):
    temp = df["Connected_on"].value_counts().reset_index()     
    temp.rename(columns={"index": "connected_on", "Connected_on": "count"}, inplace=True)
    temp['connected_on'] = pd.to_datetime(temp['connected_on'])
    temp = temp.sort_values(by="connected_on", ascending=True)
    return temp


def plot_timeline(df):
    temp = get_connectios_count_df(df)
    fig = px.line(temp, x="connected_on", y="count",
        labels={
            "connected_on":'Timeline',
            "count":'Number of Connections'
            })
    return fig

###################################################
######## PLOTS CONNECTIONS OVERTIME ###############
###################################################
def plot_connections_overtime(df):
    temp = get_connectios_count_df(df)
    temp["cum_sum"] = temp["count"].cumsum()
    fig = px.area(temp, x="connected_on", y="cum_sum",labels={
            "connected_on":'Date',
            "count":'Number of Connections'
        })
    return fig

###################################################
######## GENERATE COMPANY NETWORK #################
###################################################

def gen_network(df,cutoff,col,colors):

    color_root = random.choice(colors)
    color_nodes = random.choice(colors)

    g = nx.Graph()
    g.add_node("You",color=color_root)
    nt = Network(height="500px", width="650px", bgcolor="black", font_color="white")
    df_reduced = df[col].value_counts().reset_index().rename(columns={'index':col,col:'Count'})
    df_reduced = df_reduced[df_reduced['Count']>=cutoff]
    
    for _, row in df_reduced.iterrows():

        # store company name and count
        column = row[col]
        count = row['Count']
        
        ###### HOVER INFO #########
        title = f"{column} - {count}\n "
        position_lst = [x for x in df[df['Company']==f'{column}']['Position']]
        name = [x for x in df[df['Company']==f'{column}']['Name']]
        name_and_positions = list(zip(name,position_lst))
        name_and_positions_lst = [' - '.join(words) for words in name_and_positions] 
        context = "".join('{}\n'.format(x) for x in name_and_positions_lst)
        context = "".join('▪️ {}\n'.format(x) for x in name_and_positions_lst)
        hover_info = title + context
        
        g.add_node(column, size=count * 3, title=hover_info, color=color_nodes)
        g.add_edge("You",column, color="grey")

    # generate the graph
    nt.from_nx(g)
    nt.repulsion(node_distance=100, spring_length=200,central_gravity=1.0, spring_strength=0.09)
    nt.toggle_stabilization(True)

    # Save and read graph as HTML file (on Streamlit Sharing)
    try:
        path = "/tmp"
        nt.save_graph(f"{path}/network.html")
        HtmlFile = open(f"{path}/network.html", "r", encoding="utf-8")

    # Save and read graph as HTML file (locally)
    except:
        path = "data"
        nt.save_graph(f"{path}/network.html")
        HtmlFile = open(f"{path}/network.html", "r", encoding="utf-8")

    # Load HTML file in HTML component for display on Streamlit page
    components.html(HtmlFile.read(), height=550, width=700)

