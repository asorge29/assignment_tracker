import streamlit as st
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
#session state------------------------------------------------
if 'classrooms' not in st.session_state:
    st.session_state.classrooms = {"Name":[], 'Late Work':[]}

if 'assignments' not in st.session_state:
    st.session_state.assignments = []

if 'temp' not in st.session_state:
    st.session_state.temp = []
#functions----------------------------------------------------
def add_class(name, late_work):
    if name not in st.session_state.classrooms:
        st.session_state.classrooms['Name'].append(name)
        st.session_state.classrooms['Late Work'].append(late_work)

def create_assignment():
    global new_title, new_priority, new_due_date, new_time_estimate, new_classroom
    #if new_title not in st.session_state.assignments['Title']:
    st.session_state.assignments.append({'title':new_title, 'priority':new_priority, 'due_date':new_due_date, 'time_est':new_time_estimate, 'class':new_classroom, 'done':False, 'overdue':False})

def update_assignments():
    global new_data
    if editing:
        st.session_state.assignments = new_data.to_dict(orient='records')

def remove_completed():
    st.session_state.assignments = [assignment for assignment in st.session_state.assignments if not assignment['done']]

#operations---------------------------------------------------
for assignment in st.session_state.assignments:
    if datetime.date(assignment['due_date']) < datetime.date.today():
        assignment['overdue'] = True

#gui----------------------------------------------------------
st.sidebar.title('Classes')
with st.sidebar.expander('New Class'):
    new_class = st.text_input('Enter Class')
    late_work = st.checkbox(
        'Late Work Allowed',
        help='Does this class accept late work?'
    )
    if st.button('Create Class'):
        add_class(new_class, late_work)

st.title("Assignments")

with st.sidebar.expander('New Assignment'):
    new_title = st.text_input("Enter Title")
    new_priority = st.selectbox('Choose Priority:', ['High', 'Medium', 'Low'])
    new_due_date = st.date_input('Enter Due Date:', min_value=datetime.date.today(), max_value=(datetime.date.today()+relativedelta(months=6)))
    new_time_estimate = st.time_input('Enter Time Estimate:', step=300)
    new_classroom = st.selectbox('Enter Class:', st.session_state.classrooms['Name'])
    if st.button('Create!'):
        create_assignment()

for classroom in st.session_state.classrooms['Name']:
    st.sidebar.button(classroom)

if len(st.session_state.assignments) > 0:
    editing = st.toggle('Edit Mode', on_change=update_assignments)

    data = pd.DataFrame(st.session_state.assignments)

    if editing:
        new_data = st.data_editor(
            data,
            column_config={
                'title':st.column_config.TextColumn(
                    'Title',
                    max_chars=50,
                    help='What is the name of the assignment?'
                ),
                'priority': st.column_config.SelectboxColumn(
                    'Priority',
                    options=['High', 'Medium', 'Low'],
                    help='How important is this assignment to complete?'
                ),
                'due_date': st.column_config.DateColumn(
                    'Due Date',
                    help='When is the assignment due?'
                ),
                'time_est': st.column_config.TimeColumn(
                    'Time Estimate(Hrs)',
                    help='How long do you think it will take you to complete?',
                    step=300
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
            },
            disabled=['overdue'],
            hide_index=True
        )

    else:
        st.dataframe(
            data,
            column_config={
                'title':st.column_config.TextColumn(
                    'Title',
                    max_chars=50,
                    help='What is the name of the assignment?'
                ),
                'priority': st.column_config.SelectboxColumn(
                    'Priority',
                    options=['High', 'Medium', 'Low'],
                    help='How important is this assignment to complete?'
                ),
                'due_date': st.column_config.DateColumn(
                    'Due Date',
                    help='When is the assignment due?'
                ),
                'time_est': st.column_config.TimeColumn(
                    'Time Estimate(Hrs)',
                    help='How long do you think it will take you to complete?'
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
                ),
            },
            hide_index=True
        )

        st.button('Remove Completed Assignments', on_click=remove_completed)

        st.download_button(
            'Download Assignment Data',
            help='Download as a file to keep as a backup or for use in other apps.',
            data=data.to_csv(index=False).encode('utf-8'),
            file_name='assignments.csv'
        )

else:
    st.write('Create some assignments to get started!')