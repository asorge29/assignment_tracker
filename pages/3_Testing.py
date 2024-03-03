import streamlit as st
from streamlit_card import card

for i in range(10):
    card(title=str(i), text='This is a card', image='https://picsum.photos/200/300', url='https://www.google.com')