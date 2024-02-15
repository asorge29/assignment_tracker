import streamlit as st
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import os
import extra_streamlit_components as stx
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

#init cookie manager------------------------------------------
@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()
cookie_manager.get_all()

#functions----------------------------------------------------
def update_assignments():
    global data
    if editing:
        st.session_state.assignments = data.to_dict(orient='records')
        #save_to_cookies()

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

def get_documents_path():
    return os.path.join(os.path.expanduser('~'), 'Downloads')
    
def import_file():
    temp_df = pd.read_csv(os.path.join(get_documents_path(), 'assignments.csv'))
    st.session_state.assignments = temp_df.to_dict(orient='records')
    for assignment in st.session_state.assignments:
        assignment['due_date'] = datetime.datetime.strptime(assignment['due_date'], '%Y-%m-%d').date()
    st.rerun()

def load_from_cookies():
        to_be_loaded = cookie_manager.get('assignments')
        for assignment in to_be_loaded:
            if isinstance(assignment['due_date'], str):
                assignment['due_date'] = datetime.datetime.strptime(assignment['due_date'], '%Y-%m-%d').date()
        st.session_state.assignments = to_be_loaded
        st.session_state.classrooms = cookie_manager.get('classes')
        st.rerun()
    
def save_to_cookies():
    to_be_saved = st.session_state.assignments.copy()
    for assignment in to_be_saved:
        if isinstance(assignment['due_date'], datetime.date):
            assignment['due_date'] = str(assignment['due_date'])
    cookie_manager.set('assignments', to_be_saved, key='assignment')
    cookie_manager.set('classes', st.session_state.classrooms, key='classes')

def check_saved_status():
    to_be_loaded = cookie_manager.get('assignments')
    for assignment in to_be_loaded:
        if isinstance(assignment['due_date'], str):
            assignment['due_date'] = datetime.datetime.strptime(assignment['due_date'], '%Y-%m-%d').date()
    if to_be_loaded == st.session_state.assignments:
        return True
    else:
        return False

#session state------------------------------------------------
if 'classrooms' not in st.session_state:
    st.session_state.classrooms = {"Name":[], 'Late Work':[], 'Period':[]}

if 'assignments' not in st.session_state:
        st.session_state.assignments = []

if 'upload_key' not in st.session_state:
    st.session_state.upload_key = 0

#operations---------------------------------------------------
for assignment in st.session_state.assignments:
    if isinstance(assignment['due_date'], str):
        assignment['due_date'] = datetime.datetime.strptime(assignment['due_date'], '%Y-%m-%d').date()
    
for assignment in st.session_state.assignments:
    if assignment['due_date'] < datetime.date.today():
        assignment['overdue'] = True

for assignment in st.session_state.assignments:
    if assignment['class'] not in st.session_state.classrooms['Name']:
        st.session_state.classrooms['Name'].append(assignment['class'])
        st.session_state.classrooms['Late Work'].append(assignment['late_allowed'])
        st.session_state.classrooms['Period'].append(assignment['period'])

st.session_state.classrooms = pd.DataFrame(st.session_state.classrooms).sort_values(by='Period').to_dict(orient='list')

#gui----------------------------------------------------------
st.sidebar.title('Create')
sidebar_tabs = st.sidebar.tabs(['Class', 'Assignment'])
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
            for assignment in st.session_state.assignments:
                if assignment['class'] == classroom and not assignment['done']:
                    count += 1
            if st.session_state.classrooms['Late Work'][class_index] == True:
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
                    st.session_state.assignments.append(new_assignment)
                    save_to_cookies()
                else:
                    st.error('Please enter a classroom.')
            else:
                st.error('Please enter a title.')

st.title('Assignments')

columns = st.columns([0.85, 0.15])
with columns[0]:
    class_filter = st.selectbox('Filter by Class', [None]+st.session_state.classrooms['Name'], None)

    if class_filter == None:
        if len(st.session_state.assignments) > 0:
            editing = st.toggle('Edit Mode', on_change=update_assignments, value=False)

            data = pd.DataFrame(st.session_state.assignments)

            if editing:
                data = st.data_editor(
                    data,
                    column_order=(['title', 'priority', 'link', 'due_date', 'time_est', 'class', 'done', 'overdue']),
                    column_config={
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
                        'link': st.column_config.Column(
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
                    },
                    disabled=['overdue'],
                    hide_index=True
                )

            else:
                st.dataframe(
                    data,
                    column_order=(['title', 'priority', 'link', 'due_date', 'time_est', 'class', 'done', 'overdue']),
                    column_config={
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
            st.info('Create some assignments to get started!')

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
                column_order=(['title', 'priority', 'link', 'due_date', 'time_est', 'class', 'done', 'overdue']),
                    column_config={
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
            st.info('You have no active assignments in this class.')

with columns[1]:
#    if st.button('Load Asignments'):
#        try:
#            import_file()
#        except pd.errors.EmptyDataError:
#            st.error('You do not have any saved assignments.')
#    if st.button('Save Assignments'):
#        assignment_data = pd.DataFrame(st.session_state.assignments)
#        assignment_path = os.path.join(get_documents_path(), 'assignments.csv')
#        with open(assignment_path, 'w') as data_file:
#            data_file.write(assignment_data.to_csv(index=False))
#    with st.expander('Clear Assignments'):
#        st.warning('This will delete all assignments including the ones in your local file!', icon='⚠️')
#        if st.button('Clear Assignments'):
#            st.session_state.assignments = []
#            cookie_manager.delete('assignments')
    
    if check_saved_status():
        st.write('Save status: :white_check_mark:')
    else:
        st.write('Save status: :warning:')

    if st.button('Load Assignments'):
        load_from_cookies()
    if st.button('Save Assignments'):
        save_to_cookies()