import streamlit as st
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
#session state------------------------------------------------
if 'classrooms' not in st.session_state:
    st.session_state.classrooms = {"Name":[], 'Late Work':[]}

if 'assignments' not in st.session_state:
    st.session_state.assignments = []

#functions----------------------------------------------------
def add_class(name, late_work):
    if name not in st.session_state.classrooms['Name']:
        if len(name) > 0:
            st.session_state.classrooms['Name'].append(name)
            st.session_state.classrooms['Late Work'].append(late_work)
        else:
            st.error('Please enter a name.')
    else:
        st.error('Please enter an original name.')

def create_assignment():
    global new_title, new_priority, new_due_date, new_time_estimate, new_classroom
    if new_title != '':
        if new_classroom != None:
            if new_due_date < datetime.date.today():
                st.session_state.assignments.append({'title':new_title, 'priority':new_priority, 'due_date':new_due_date, 'time_est':new_time_estimate, 'class':new_classroom, 'done':False, 'overdue':True})
            else:
                st.session_state.assignments.append({'title':new_title, 'priority':new_priority, 'due_date':new_due_date, 'time_est':new_time_estimate, 'class':new_classroom, 'done':False, 'overdue':False})
        else:
            st.error('Please enter a classroom.')
    else:
        st.error('Please enter a title.')

def update_assignments():
    global data
    if editing:
        st.session_state.assignments = data.to_dict(orient='records')

def remove_completed():
    old_amount = len(st.session_state.assignments)
    st.session_state.assignments = [assignment for assignment in st.session_state.assignments if not assignment['done']]
    amount_removed = old_amount - len(st.session_state.assignments)
    if amount_removed > 0:
        st.toast(f'Removed {amount_removed} assignments.')
        st.balloons()
        if len(st.session_state.assignments) == 0:
            st.toast('Congradulations on completing all your assignments!')
    else:
        st.toast('No completed assignments to remove.')

#operations---------------------------------------------------
for assignment in st.session_state.assignments:
    if assignment['due_date'] < datetime.date.today():
        assignment['overdue'] = True

#page config--------------------------------------------------
st.set_page_config(
    page_title='Assignment Tracker',
    layout='wide',
    page_icon='✏️',
    menu_items={
        'Report a Bug':'https://github.com/BassMaster629/assignment_tracker/issues',
        'Get Help':'https://github.com/BassMaster629/assignment_tracker/issues',
        'About':'Simple web app to keep track of your assignments built as a learning project. Enjoy! :)'
    }
)
#gui----------------------------------------------------------
st.sidebar.title('Create')
sidebar_tabs = st.sidebar.tabs(['Class', 'Assignment'])
with sidebar_tabs[0]:
    new_class = st.text_input('Enter Class', max_chars=100, help='Enter the name of the class you want to add.')
    late_work = st.checkbox(
        'Late Work Allowed',
        help='Does this class accept late work?'
    )
    if st.button('Create!', help='Create a new class.'):
        add_class(new_class, late_work)

    st.write('Classes:')
    if len(st.session_state.classrooms['Name']) > 0:
        for classroom in st.session_state.classrooms['Name']:
            class_index = st.session_state.classrooms['Name'].index(classroom)
            if st.session_state.classrooms['Late Work'][class_index] == True:
                st.success(classroom)
            else:
                st.error(classroom)
    else:
        st.info('No classes yet.')

with sidebar_tabs[1]:
    new_title = st.text_input("Enter Title", max_chars=100, help='What is the assignment called?')
    new_priority = st.selectbox('Choose Priority:', ['High', 'Medium', 'Low'], help='How important is this assignment?')
    new_due_date = st.date_input('Enter Due Date:', min_value=(datetime.date.today()-relativedelta(weeks=1)), max_value=(datetime.date.today()+relativedelta(months=6)), help='When is this assignment due?')
    new_time_estimate = st.time_input('Enter Time Estimate:', step=300, help='How long do you think this assignment will take?')
    new_classroom = st.selectbox('Enter Class:', st.session_state.classrooms['Name'], help='Which class is this assignment for?')
    if st.button('Create!', key=1, help='Create a new assignment.'):
        create_assignment()

st.title('Assignments')
        
class_filter = st.selectbox('Filter by Class', [None]+st.session_state.classrooms['Name'], None)

if class_filter == None:
    if len(st.session_state.assignments) > 0:
        editing = st.toggle('Edit Mode', on_change=update_assignments, value=False)

        data = pd.DataFrame(st.session_state.assignments)

        if editing:
            data = st.data_editor(
                data,
                column_config={
                    'title':st.column_config.TextColumn(
                        'Title',
                        max_chars=100,
                        help='What is the name of the assignment?'
                    ),
                    'priority': st.column_config.SelectboxColumn(
                        'Priority',
                        options=['High', 'Medium', 'Low'],
                        help='How important is this assignment to complete?'
                    ),
                    'due_date': st.column_config.DateColumn(
                        'Due Date',
                        help='When is the assignment due?',
                        max_value=(datetime.date.today()+relativedelta(months=6))
                    ),
                    'time_est': st.column_config.TimeColumn(
                        'Time Estimate(Hrs)',
                        help='How long do you think it will take you to complete?',
                        step=300,
                        format="HH:mm"
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
                        help='How long do you think it will take you to complete?',
                        format="HH:mm"
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

            st.button('Remove Completed Assignments', on_click=remove_completed, help='Remove all assignments that are marked as done.')

            st.download_button(
                'Download Assignment Data',
                help='Download as a file to keep as a backup or for use in other apps.',
                data=data.to_csv(index=False).encode('utf-8'),
                file_name='assignments.csv'
            )

    else:
        st.write('Create some assignments to get started!')

else:
    class_index = (st.session_state.classrooms['Name'].index(class_filter))
    if st.session_state.classrooms['Late Work'][class_index] == True:
        st.success('Late Work Allowed!')
    else:
        st.error('Late Work Not Allowed!')

    has_assignments = False
    for assignment in st.session_state.assignments:
        if assignment['class'] == class_filter:
            has_assignments = True
            break
    if has_assignments:
        data = pd.DataFrame(st.session_state.assignments)
        filtered_data = data[data['class'] == class_filter]

        st.dataframe(
            filtered_data,
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
                    format="HH:mm"
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
        st.write('You have no active assignments in this class.')