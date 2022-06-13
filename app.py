from distutils.command.clean import clean
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

from helper import *

### Loading Connection File
def main():
    ## Streamlit Page Config
    st.set_page_config(
        page_title = "LinkedIn Connection Visualizer-Streamlit Web App",
        page_icon = "🕸️",
        initial_sidebar_state='expanded',
    )
       # import bootstrap
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        # LinkedIn Connection Insights 🪄
        #### Get To Know Your Network Better Today!
        ##### Your Insights Are One Upload Away 🤩

        ##### Just, Upload Your Data 💾
        """
    )
    st.caption(
        """
        Don't Know Where To Find?
        [Click here](). Don't worry your data is in safe hands.
        """
    )
    
    ####### Upload Button #######
    fileobj = st.file_uploader('Upload / Drop your downloaded zip file 👇',type={"zip"})
    if fileobj is not None:
        df = get_data(file=fileobj)

        ########### [ VIEW DATA ] ##########
        st.markdown(
            """
            ---
            ### Take a Look At Your Data 👀
            ---
            """
        )

        if st.checkbox('Show Data'):
            st.write(df)
        
        ########## [ CLEANING ] #############
        clean_df = clean_data(df)

        ########## [ KEY INFORMATION ] ############
        top_position, top_company, second_company, total_connections, this_month_df, today_df = info(clean_df)
        first_conn_name,first_conn_date,first_conn_comp,gap,first_conn_comp,first_conn_pos = info_first_conn(clean_df)
        new_conn_name,new_conn_pos,new_conn_comp = info_newest_conn(clean_df)

        ###################### Adding Columns ::  Connections Based On Month Year, and week day's #########
        clean_df,max_people_connect_date,max_people_connect_count = add_cols_y_m_d(clean_df)

        ####################################################
        ################## Designing Sidebar ###############
        ####################################################
        st.sidebar.markdown("""#### Sliders To Plot More/Less Data""")

        #### Top Companies
        st.sidebar.markdown(""" ##### Companies """)
        cval = st.sidebar.slider('Top n',1,50,10)

        ##### Position
        st.sidebar.markdown(""" ##### Positions """)
        pval = st.sidebar.slider('Top n',1,30,10)

        #### Network Graph
        st.sidebar.markdown("""#### Network Graph """)
        st.sidebar.markdown("""###### Cutoff Points For Connection Graph (the smaller it is the larger the network)""")
        comcutoff = st.sidebar.slider('Company Network',2,50,3)
        poscutoff = st.sidebar.slider('Position Network',2,50,4)

        #############################################
        ############### Headlines ###################
        #############################################
        st.markdown(
            '''
            ---
            ### Top Highlights
            '''
        )
        pos,com = st.columns(2)
        pos.metric(
            "Top Position",f"{top_position}"
        )
        com.metric(
            "Top Company",f"{top_company}"
        )
        st.metric(
            "Total Connections", f"{total_connections}", f"{len(today_df)}"
        )
        ################################################        
        ################ Profile Summary ###############
        ################################################
        st.markdown(
            '''
            ---
            ### Profile Summary
            
            '''
        )
        st.markdown(
            f"""
            ---
            * You have **{len(this_month_df)}** new connections this month.
            * Most of Your Connections Work At **{top_company}** followed by **{second_company}**
            * You love connecting 👨‍ with people with the title -**{top_position}**.
            * Your first ever connection was **{first_conn_name}** connected on **{first_conn_date}** who work as a **{first_conn_pos}** at **{first_conn_comp}**, Its been **{gap}** days since you two connected!!
            * Your Newest connection is **{new_conn_name}** who work as a **{new_conn_pos}** at **{new_conn_comp}**
            * You Connect With Most People On **{clean_df['day_name'].value_counts().index[0]}**
            * On **{max_people_connect_date}** you connected with **{max_people_connect_count}** people, that is max connections in one day.
            """
        )

        ###################################################
        #################### TOP COMPANIES ################
        ###################################################
        st.markdown(
            f"""
            ---
            ### Top {cval} Companies
            """
        )
        col = "Company"
        build(col,clean_df,cval)

        ###################################################
        #################### TOP POSITIONS ################
        ###################################################
        st.markdown(
            f"""
            ---
            ### Top {pval} Positions
            """
        )
        col = "Position"
        build(col,clean_df,pval)

        ###################################################
        ###### CONNECTION ON DIFFERENT MONTHS #############
        ###################################################
        st.markdown(
            """
            ---
            #### Number of Connections On Different Months
            """
        )
        fig  = plot_connections_on_different_months(clean_df)        
        st.plotly_chart(fig,transparent=True,use_container_width=True)
        
        ###################################################
        ###### CONNECTION ON DIFFERENT WEEKDAYS ###########
        ###################################################
        st.markdown(
            """
            ---
            #### Number of Connections On Different Week Days
            """
        )
        fig = plot_connections_on_different_weekdays(clean_df)
        st.plotly_chart(fig,transparent=True,use_container_width=True)
        
        ###################################################
        ###### TIMELINE OF CONNECTIONS ####################
        ###################################################
        st.markdown(
            """
            ---
            ### Timeline of Connections
            """
        )
        fig = plot_timeline(clean_df)
        st.plotly_chart(fig,transparent=True,use_container_width=True)
        
        ###################################################
        ###### CONNECTIONS OVER TIME ######################
        ###################################################
        st.markdown(
            """
            ---
            ### Number of Connections Overtime
            """
        )
        fig = plot_connections_overtime(clean_df)
        st.plotly_chart(fig,transparent=True,use_container_width=True)
        
        ###################################################
        ###### COMPANY NETWORK ############################
        colors = ['#6B5B95','#B565A7','#955251',' #FF6F61','#F7CAC9','#e6e6fa','#34568B','#ff7373']
        ###################################################
        st.markdown(
            """
            ---
            ### Company Network
            """
        )
        gen_network(clean_df,comcutoff,col="Company",colors=colors)

        ###################################################
        ###### POSITION NETWORK ###########################
        ###################################################
        st.markdown(
            """
            ---
            ### Position Network
            """
        )

        gen_network(clean_df,poscutoff,col="Position",colors=colors)

        ###################################################
        ###### PEOPLE SHARING EMAILS ######################
        ###################################################
        st.markdown(
            """
            ---
            ### People Shares 📧 Email With You
            """
        )
        emails = df[df['Email Address'].notna()][['Name','Email Address','Position','Company','Connected_on']].reset_index().drop('index',axis=1)
        st.write(emails)


if __name__ == "__main__":
    main()   
