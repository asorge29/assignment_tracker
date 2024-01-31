import streamlit as st

#sidebar--------------------------------------------------
st.sidebar.title('Create')
st.sidebar.info('This is where you go to create new classes and assignments.')
sidebar_tabs = st.sidebar.tabs(['Class', 'Assignment', 'Import/Export'])
with sidebar_tabs[0]:
    st.info(':arrow_up: This tab is used to create new classes, which will help categorize your assignments.')
    new_class = st.text_input('Enter Class', help='Enter the name of the class you wish to create, for example, "Math"', value='Math')
    st.checkbox(
        'Late Work Allowed',
        help="Check this if this class accepts late work, leave it unchecked if it doesn't."
    )
    st.button('Create!', help='Create the new class.')
    st.info(':arrow_up: Press this to add the class to your list of classes. Note: this button will not function in this tutorial.')       
    st.error('Please enter a name.')
    st.info('This :arrow_up: will appear if you attempt to create a class with no name.')
    st.error('Please enter an original name.')
    st.info('This :arrow_up: will appear if you attempt to create a class with the same name as a class that already exists.')

    st.write('Classes:')
    st.info(' This :arrow_up: is your list of classes.')
    st.success('Math: 5 Assignments')
    st.info('This :arrow_up: is an example of a class called "Math" that accepts late work(signified by the green border) and has 5 active assignments.')
    st.error('Math: 5 Assignments')
    st.warning('No classes yet.')