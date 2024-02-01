import streamlit as st
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import hashlib
import io
#session state------------------------------------------------
if 'classrooms' not in st.session_state:
    st.session_state.classrooms = {"Name":[], 'Late Work':[]}

if 'assignments' not in st.session_state:
    st.session_state.assignments = []

if 'upload_key' not in st.session_state:
    st.session_state.upload_key = 0

#functions----------------------------------------------------
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

def calculate_hash(data):
    sha256 = hashlib.sha256()
    sha256.update(data.encode('utf-8'))
    return sha256.hexdigest()

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
        'Get Help':'https://assignmenttracker.streamlit.app/tutorial',
        'About':'Simple web app to keep track of your assignments built as a learning project. Enjoy! :)'
    }
)
#gui----------------------------------------------------------
st.sidebar.title('Create')
sidebar_tabs = st.sidebar.tabs(['Class', 'Assignment', 'Import/Export'])
with sidebar_tabs[0]:
    new_class = st.text_input('Enter Class', max_chars=100, help='Enter the name of the class you want to add.')
    late_work = st.checkbox(
        'Late Work Allowed',
        help='Does this class accept late work?'
    )
    if st.button('Create!', help='Create a new class.'):
        if new_class not in st.session_state.classrooms['Name']:
            if len(new_class) > 0:
                st.session_state.classrooms['Name'].append(new_class)
                st.session_state.classrooms['Late Work'].append(late_work)
            else:
                st.error('Please enter a name.')
        else:
            st.error('Please enter an original name.')

    st.write('Classes:')
    if len(st.session_state.classrooms['Name']) > 0:
        for classroom in st.session_state.classrooms['Name']:
            count = 0
            class_index = st.session_state.classrooms['Name'].index(classroom)
            for assignment in st.session_state.assignments:
                if assignment['class'] == classroom:
                    count += 1 #add check to exclude completed
            if st.session_state.classrooms['Late Work'][class_index] == True:
                st.success(f'{classroom}: {count} Assignments')
            else:
                st.error(f'{classroom}: {count} Assignments')
    else:
        st.warning('No classes yet.')

with sidebar_tabs[1]:
    new_title = st.text_input("Enter Title", max_chars=100, help='What is the assignment called?')
    new_priority = st.selectbox('Choose Priority:', ['High', 'Medium', 'Low'], help='How important is this assignment?')
    new_due_date = st.date_input('Enter Due Date:', min_value=(datetime.date.today()-relativedelta(weeks=1)), max_value=(datetime.date.today()+relativedelta(months=6)), help='When is this assignment due?')
    new_time_estimate = st.number_input('Enter Time Estimate:', step=5, help='How long do you think this assignment will take? (in minutes)', min_value=5, max_value=600, value=30)
    new_classroom = st.selectbox('Enter Class:', st.session_state.classrooms['Name'], help='Which class is this assignment for?')
    if st.button('Create!', key=-1, help='Create a new assignment.'):
        if new_title != '':
            if new_classroom != None:
                new_assignment = {'title':new_title, 'priority':new_priority, 'due_date':new_due_date, 'time_est':new_time_estimate, 'class':new_classroom, 'done':False, 'overdue':False, 'late_allowed':False}
                if new_due_date < datetime.date.today():
                    new_assignment['overdue'] = True
                if st.session_state.classrooms['Late Work'][st.session_state.classrooms['Name'].index(new_classroom)] == True:
                    new_assignment['late_allowed'] = True
                st.session_state.assignments.append(new_assignment)
            else:
                st.error('Please enter a classroom.')
        else:
            st.error('Please enter a title.')

with sidebar_tabs[2]:
    data = pd.DataFrame(st.session_state.assignments)
    hash_before_export = calculate_hash(data.to_csv(index=False))
    csv_data_with_hash = data.to_csv(index=False) + f"\n# Hash: {hash_before_export}"
    st.download_button(
        'Download Assignment Data',
        help='Download as a file to keep as a backup or for use in other apps.',
        data=csv_data_with_hash.encode('utf-8'),
        file_name='assignments.csv'
    )

    file_import = st.file_uploader('Import Assignments from CSV', ['.csv'], False, help='Import a file containing your assignments.', key=st.session_state.upload_key)
    if file_import is not None:
        imported_lines = file_import.getvalue().decode('utf-8').split('\n')
        if len(imported_lines) > 1:
            hash_before_import = imported_lines[-1].replace('# Hash: ', '')
            modified_csv_data = '\n'.join(imported_lines[:-1])
            hash_after_import = calculate_hash(modified_csv_data)
            if hash_before_import is not None and hash_before_import == hash_after_import:
                try:
                    import_data = pd.read_csv(io.StringIO(modified_csv_data), comment='#')
                    st.session_state.assignments = import_data.to_dict(orient='records')
                    for assignment in st.session_state.assignments:
                        assignment['due_date'] = datetime.datetime.strptime(assignment['due_date'], '%Y-%m-%d').date()
                    st.session_state.upload_key += 1
                except pd.errors.EmptyDataError:
                    st.error('The CSV does not contain data.')
            else:
                st.error('Error: The imported CSV file has been tampered with or does not contain a valid hash.')
        else:
            None

st.title('Assignments')
        
class_filter = st.selectbox('Filter by Class', [None]+st.session_state.classrooms['Name'], None)

if class_filter == None:
    if len(st.session_state.assignments) > 0:
        editing = st.toggle('Edit Mode', on_change=update_assignments, value=False)

        data = pd.DataFrame(st.session_state.assignments)

        if editing:
            data = st.data_editor(
                data,
                column_order=(['title', 'priority', 'due_date', 'time_est', 'class', 'done', 'overdue']),
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
                },
                disabled=['overdue'],
                hide_index=True
            )

        else:
            st.dataframe(
                data,
                column_order=(['title', 'priority', 'due_date', 'time_est', 'class', 'done', 'overdue']),
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
                    ),
                },
                hide_index=True
            )

            st.button('Remove Completed Assignments', on_click=remove_completed, help='Remove all assignments that are marked as done.')

    else:
        st.warning('Create some assignments to get started!')

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
            column_order=(['title', 'priority', 'due_date', 'time_est', 'class', 'done', 'overdue']),
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
                ),
            },
            hide_index=True
        )

        st.button('Remove Completed Assignments', on_click=remove_completed)

    else:
        st.warning('You have no active assignments in this class.')