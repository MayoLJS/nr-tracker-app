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
    title = 'Non Routine',
    icon = ':material/home:',
)      

pricebook_page = st.Page(
    './app/pricebook.py',
    title = 'Price Book',
    icon = ':material/payments:',
    ) 

vendor_pricebook_page = st.Page(
    './app/pricebook_pub.py',
    title = 'Price Book for Vendors',
    icon = ':material/payments:',
    ) 
selected_page = st.navigation ([nr_page, pricebook_page, vendor_pricebook_page])
selected_page.run()
