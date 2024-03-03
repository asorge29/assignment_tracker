import streamlit as st
from streamlit_card import card

a = st.columns(4)
with a[0]:
    for i in range(10):
        card(title=str(i), text=['This is a card', "this is a subtext"], image='https://picsum.photos/800/300', url='https://www.google.com', styles={"card":{"width": "100%", "height": "200px", "border-radius": "60px", "background-color": "red"}, 'div':{"padding": "1px"}})
with a[1]:
    for i in range(10):
        card(title=str(i+10), text=['This is a card', "this is a subtext"], image='https://picsum.photos/800/300', url='https://www.google.com', styles={"card":{"width": "100%", "height": "200px", "border-radius": "60px", "background-color": "red"}, 'div':{"padding": "1px"}})
with a[2]:
    for i in range(10):
        card(title=str(i+20), text=['This is a card', "this is a subtext"], image='https://picsum.photos/800/300', url='https://www.google.com', styles={"card":{"width": "100%", "height": "200px", "border-radius": "60px", "background-color": "red"}, 'div':{"padding": "1px"}})
with a[3]:
    for i in range(10):
        card(title=str(i+30), text=['This is a card', "this is a subtext"], image='https://picsum.photos/800/300', url='https://www.google.com', styles={"card":{"width": "100%", "height": "200px", "border-radius": "60px", "background-color": "red"}, 'div':{"padding": "1px"}})