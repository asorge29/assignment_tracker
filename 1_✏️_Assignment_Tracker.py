import streamlit as st
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import extra_streamlit_components as stx
from streamlit_option_menu import option_menu
from streamlit_extras.let_it_rain import rain
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
    st.session_state.assignments = data.to_dict(orient='records')
    save_to_cookies(7,8)

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

def load_from_cookies():
    try:
        to_be_loaded = cookie_manager.get('assignments')
        for assignment in to_be_loaded:
            if isinstance(assignment['due_date'], str):
                assignment['due_date'] = datetime.datetime.strptime(assignment['due_date'], '%Y-%m-%d').date()
        st.session_state.assignments = to_be_loaded
        st.session_state.classrooms = cookie_manager.get('classes')
        st.rerun()
    except TypeError:
        st.toast('No assignments to load.')
        
def save_to_cookies(key1, key2):
    if len(st.session_state.assignments) > 0 or len(st.session_state.classrooms) > 0:
        to_be_saved = st.session_state.assignments.copy()
        for assignment in to_be_saved:
            if isinstance(assignment['due_date'], datetime.date):
                assignment['due_date'] = str(assignment['due_date'])
        if len(to_be_saved) > 0:
            cookie_manager.set('assignments', to_be_saved, key=key1, expires_at=datetime.datetime.now() + relativedelta(days=365))
        cookie_manager.set('classes', st.session_state.classrooms, key=key2, expires_at=datetime.datetime.now() + relativedelta(days=365))
    else:
        st.toast('No assignments to save.')

def check_saved_status():
    try:
        current_save = cookie_manager.get('assignments')
        for assignment in current_save:
            if isinstance(assignment['due_date'], str):
                assignment['due_date'] = datetime.datetime.strptime(assignment['due_date'], '%Y-%m-%d').date()
        if current_save == st.session_state.assignments:
            return True
        else:
            return False
    except TypeError:
        return False

def remove_classroom(classroom):
    index = st.session_state.classrooms['Name'].index(classroom)
    st.session_state.classrooms['Name'].pop(index)
    st.session_state.classrooms['Late Work'].pop(index)
    st.session_state.classrooms['Period'].pop(index)
    st.session_state.assignments = [assignment for assignment in st.session_state.assignments if assignment['class'] != classroom]
    cookie_manager.set('classes', st.session_state.classrooms, key=77, expires_at=datetime.datetime.now() + relativedelta(days=365))
    st.session_state.bypass_autoload = True
    st.rerun()

def easter_egg():
    if 'The Ian Function' in st.session_state.classrooms['Name']:
        rain(emoji='👺', font_size=54, falling_speed=10)
#session state------------------------------------------------
if 'classrooms' not in st.session_state:
    st.session_state.classrooms = {"Name":[], 'Late Work':[], 'Period':[]}

if 'assignments' not in st.session_state:
    st.session_state.assignments = []

if 'bypass_autoload' not in st.session_state:
    st.session_state.bypass_autoload = False

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

if not st.session_state.bypass_autoload:
    if len(st.session_state.assignments) == 0 and len(st.session_state.classrooms['Name']) == 0 and cookie_manager.get('assignments') is not None:
        if len(cookie_manager.get('assignments')) > 0 or len(cookie_manager.get('classes')) > 0:
            load_from_cookies()
else:
    save_to_cookies(13,14)
    st.session_state.bypass_autoload = False

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
                        st.session_state.classrooms = pd.DataFrame(st.session_state.classrooms).sort_values(by='Period').to_dict(orient='list')
                        save_to_cookies(9,10)
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
                    save_to_cookies(1,2)
                else:
                    st.error('Please enter a classroom.')
            else:
                st.error('Please enter a title.')

with sidebar_tabs[2]:
    to_be_deleted = st.selectbox('Delete Class', st.session_state.classrooms['Name'], help='Delete a class.')
    if st.button('Delete'):
        remove_classroom(to_be_deleted)
    if st.button('Clear All'):
        st.session_state.classrooms = {'Name':[], 'Late Work':[], 'Period':[]}
        st.session_state.assignments = []
        cookie_manager.delete('assignments',key=900)
        cookie_manager.delete('classes', key=901)
        st.session_state.bypass_autoload = True
    st.warning('This will delete all assignments and classes. Thic cannot be undone.', icon='⚠️')

with sidebar_tabs[3]:
    if st.button('Load Assignments'):
        load_from_cookies()
    if st.button('Save Assignments'):
        save_to_cookies(3,4)


st.title('Assignments')

if check_saved_status():
    st.write('Save status: :white_check_mark:')
else:
    st.write('Save status: :warning:')

classroom_list = [None] * 2 * len(st.session_state.classrooms['Name'])
classroom_list[::2] = st.session_state.classrooms['Name']
amount_of_assignments = []
for classroom in st.session_state.classrooms['Name']:
    count = 0
    for assignment in st.session_state.assignments:
        if assignment['class'] == classroom and not assignment['done']:
            count += 1
    amount_of_assignments.append(count)
classroom_list[1::2] = amount_of_assignments
for index in range(len(classroom_list)):
    if index % 2 == 0:
        classroom_list[index] = f'{classroom_list[index]}: {classroom_list[index+1]}'
for i in classroom_list:
    if isinstance(i, int):
        classroom_list.remove(i)
class_filter = option_menu('Select Class:', ['All', 'Edit'] + classroom_list, orientation='horizontal', menu_icon='filter', icons=['list-check', 'pencil']+['list-check']*(len(classroom_list)))
class_filter = class_filter.split(':')[0]

if class_filter == 'All' or 'Edit':
    if len(st.session_state.assignments) > 0:
        data = pd.DataFrame(st.session_state.assignments)

        if class_filter == 'Edit':
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
            update_assignments()

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

if len(st.session_state.assignments) > 0:
    save_to_cookies(5,6)
easter_egg()