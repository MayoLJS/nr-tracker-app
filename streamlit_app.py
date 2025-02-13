import streamlit as st
import pandas as pd


####################################################
######### SETUP
####################################################
st.set_page_config(                                                                     # Streamlit: setup page details
    page_title = 'Non Routine',
    page_icon = '👷🏽‍♂️',
    layout = 'wide',                                                                    # Page layput
    )

st.logo('./img/ieng.png')                                                     # Add photo above navigation

####################################################
######### NAVIGATION SETUP
####################################################
nr_page = st.Page(                                                                 # Navigation
    './app/nonroutine.py',
    title = 'Non Routine - IHS',
    icon = ':material/home:',
)      

pricebook_page = st.Page(
    './app/pricebook.py',
    title = 'Price Book - IHS',
    icon = ':material/payments:',
    ) 

vendor_pricebook_page = st.Page(
    './app/pricebook_pub.py',
    title = 'Approved Vendor Price',
    icon = ':material/payments:',
    ) 

atcnr_page = st.Page(                                                                 # Navigation
    './app/atcnonroutine.py',
    title = 'Non Routine - ATC',
    icon = ':material/home:',
)  

atcnrnew_page = st.Page(                                                                 # Navigation
    './app/atcnonroutine v2.py',
    title = 'Non Routine - ATC - New RMs',
    icon = ':material/home:',
) 

atcpo_page = st.Page(
    './app/atc_po_reader.py',
    title = 'ATC POs Reader ',
    icon = ':material/widget_small:',
    ) 


selected_page = st.navigation ([nr_page, pricebook_page, vendor_pricebook_page, atcnr_page, atcnrnew_page, atcpo_page])
selected_page.run()
