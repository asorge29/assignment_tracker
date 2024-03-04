import streamlit as st
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import extra_streamlit_components as stx
from streamlit_option_menu import option_menu
from streamlit_extras.let_it_rain import rain
from streamlit_card import card
import streamlit_antd_components as sac
#page config--------------------------------------------------
st.set_page_config(
    page_title='Assignment Tracker',
    layout='wide',
    page_icon='✏️',
    menu_items={
        'Report a Bug':'https://github.com/BassMaster629/assignment_tracker/issues',
        'Get Help':'https://assignment-tracker.streamlit.app/Tutorial',
        'About':'https://github.com/BassMaster629/assignment_tracker/blob/main/README.md'
    }
)

#session state------------------------------------------------
if 'classrooms' not in st.session_state:
    st.session_state.classrooms = {"Name":[], 'Late Work':[], 'Period':[], 'Count':[]}

if 'assignments' not in st.session_state:
    st.session_state.assignments = pd.DataFrame(columns=['title', 'priority', 'due_date', 'time_est', 'class', 'link', 'done', 'overdue', 'late_allowed'])

#constants----------------------------------------------------
COLUMN_CONFIG = {
    'title':st.column_config.TextColumn(
        'Title',
        max_chars=100,
        help='What is the name of the assignment?',
        width='medium'
    ),
    'priority': st.column_config.SelectboxColumn(
        'Priority',
        options=['High', 'Medium', 'Low'],
        help='How important is this assignment to complete?'
    ),
    'link': st.column_config.LinkColumn(
        'Link',
        help='Link to this assignment.',
        width='medium'
    ),
    'due_date': st.column_config.DateColumn(
        'Due Date',
        help='When is the assignment due?',
        max_value=(datetime.date.today()+relativedelta(months=6))
    ),
    'time_est': st.column_config.NumberColumn(
        'Time Estimate',
        help='How long do you think it will take you to complete?',
        step=5,
        format='%d minutes'
    ),
    'class': st.column_config.SelectboxColumn(
        'Class',
        options=st.session_state.classrooms['Name'],
        help='What class is this assignment for?'
    ),
    'done': st.column_config.CheckboxColumn(
        'Done',
        help='Is the assignment done?'
    ),
    'overdue': st.column_config.CheckboxColumn(
        'Overdue',
        help='Is the assignment past its due date?'
    )
}
COLUMN_ORDER = ['title', 'priority', 'link', 'due_date', 'time_est', 'class', 'done', 'overdue']

#operations---------------------------------------------------
#TODO update this
for assignment in st.session_state.assignments.iterrows():
    if assignment[1]['due_date'] < datetime.date.today():
        assignment[1]['overdue'] = True

#gui----------------------------------------------------------
st.sidebar.title('Configuration')
sidebar_tabs = st.sidebar.tabs(['Class', 'Assignment', 'Delete', 'Save/Load'])
with sidebar_tabs[0]:
    with st.form('class_form', clear_on_submit=True):
        new_class = st.text_input('Enter Class', max_chars=100, help='Enter the name of the class you want to add.')
        late_work = st.checkbox(
            'Late Work Allowed',
            help='Does this class accept late work?'
        )
        new_period = st.number_input('Period/Order:', min_value=0, max_value=25)
        if st.form_submit_button('Create!', help='Create a new class.'):
            if new_class not in st.session_state.classrooms['Name']:
                if new_period not in st.session_state.classrooms['Period']:
                    if len(new_class) > 0:
                        st.session_state.classrooms['Name'].append(new_class)
                        st.session_state.classrooms['Late Work'].append(late_work)
                        st.session_state.classrooms['Period'].append(new_period)
                        st.session_state.classrooms['Count'].append(0)
                        st.session_state.classrooms = pd.DataFrame(st.session_state.classrooms).sort_values(by='Period').to_dict(orient='list')
                    else:
                        st.error('Please enter a name.')
                else:
                    st.error('Please enter an original period.')
            else:
                st.error('Please enter an original name.')

    st.write('Classes:')
    if len(st.session_state.classrooms['Name']) > 0:
        for classroom in st.session_state.classrooms['Name']:
            count = 0
            class_index = st.session_state.classrooms['Name'].index(classroom)
            for assignment in st.session_state.assignments.iterrows():
                if assignment[1]['class'] == classroom and not assignment[1]['done']:
                    count += 1
            if st.session_state.classrooms == True:
                st.success(f'{classroom}: {count} Assignments')
            else:
                st.error(f'{classroom}: {count} Assignments')
    else:
        st.info('No classes yet.')

with sidebar_tabs[1]:
    with st.form('Assignment_form', clear_on_submit=True):
        new_title = st.text_input("Enter Title", max_chars=100, help='What is the assignment called?')
        new_priority = st.selectbox('Choose Priority:', ['High', 'Medium', 'Low'], help='How important is this assignment?')
        new_due_date = st.date_input('Enter Due Date:', min_value=(datetime.date.today()-relativedelta(weeks=1)), max_value=(datetime.date.today()+relativedelta(months=6)), help='When is this assignment due?')
        new_time_estimate = st.number_input('Enter Time Estimate:', step=5, help='How long do you think this assignment will take? (in minutes)', min_value=5, max_value=600, value=30)
        new_classroom = st.selectbox('Enter Class:', st.session_state.classrooms['Name'], help='Which class is this assignment for?')
        new_link = st.text_input('Link to assignment (Optional):')
        if st.form_submit_button('Create!', help='Create a new assignment.'):
            if new_title != '':
                if new_classroom != None:
                    new_assignment = {'title':new_title, 'priority':new_priority, 'due_date':new_due_date, 'time_est':new_time_estimate, 'class':new_classroom, 'link':new_link, 'done':False, 'overdue':False, 'late_allowed':False, 'period':0}
                    if new_due_date < datetime.date.today():
                        new_assignment['overdue'] = True
                    if st.session_state.classrooms['Late Work'][st.session_state.classrooms['Name'].index(new_classroom)] == True:
                        new_assignment['late_allowed'] = True
                    if len(new_link) < 2:
                        new_assignment['link'] = None
                    new_assignment['period'] = st.session_state.classrooms['Period'][st.session_state.classrooms['Name'].index(new_classroom)]
                    st.session_state.classrooms['Count'][st.session_state.classrooms['Name'].index(new_classroom)] += 1
#TODO replace append with concat
                    st.session_state.assignments = st.session_state.assignments.append(new_assignment, ignore_index=True)
                else:
                    st.error('Please enter a classroom.')
            else:
                st.error('Please enter a title.')

st.title('Assignments')

menu_list = [None] * (2 * len(st.session_state.classrooms['Name']))
menu_list[::2] = st.session_state.classrooms['Name']
menu_list[1::2] = st.session_state.classrooms['Count']
for i in range(len(menu_list)):
    if i % 2 == 0:
        menu_list[i] = f'{menu_list[i]}: {menu_list[i+1]}'
for i in menu_list:
    if isinstance(i, int):
        menu_list.remove(i)
    
class_filter = sac.segmented(items=['All', 'Edit'] + menu_list, divider=False, use_container_width=True, size='sm', radius='lg').split(':')[0]


if class_filter == 'All':
    st.dataframe(st.session_state.assignments, hide_index=True, use_container_width=True, column_order=COLUMN_ORDER, column_config=COLUMN_CONFIG)
elif class_filter == 'Edit':
    st.session_state.assignments = st.data_editor(st.session_state.assignments, hide_index=True, column_config=COLUMN_CONFIG, disabled=['overdue'], use_container_width=True, column_order=COLUMN_ORDER)
else:
    st.dataframe(st.session_state.assignments[st.session_state.assignments['class'] == class_filter], hide_index=True, use_container_width=True, column_order=COLUMN_ORDER, column_config=COLUMN_CONFIG)