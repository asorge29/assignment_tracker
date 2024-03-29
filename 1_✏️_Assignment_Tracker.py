import streamlit as st
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from streamlit_extras.let_it_rain import rain
from streamlit_card import card
import streamlit_antd_components as sac
from streamlit_cookies_manager import CookieManager
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

#functions----------------------------------------------------
def remove_completed():
    old_amount = len(st.session_state.assignments)
    for index, assignment in st.session_state.assignments.iterrows():
        if assignment['done']:
            st.session_state.assignments.drop(index, inplace=True)
    amount_removed = old_amount - len(st.session_state.assignments)
    if amount_removed > 0:
        st.toast(f'Removed {amount_removed} assignments.')
        st.balloons()
        if len(st.session_state.assignments) == 0:
            st.toast('Congradulations on completing all your assignments!')

def update_assignments():
    global class_filter
    if class_filter == 'Edit':
        if st.session_state.edited_df is not None:
            st.session_state.assignments = st.session_state.edited_df

def delete_classroom(classroom):
    index = st.session_state.classrooms['Name'].index(classroom)
    st.session_state.classrooms['Name'].pop(index)
    st.session_state.classrooms['Late Work'].pop(index)
    st.session_state.classrooms['Period'].pop(index)
    st.session_state.classrooms['Count'].pop(index)
    st.session_state.assignments = st.session_state.assignments[st.session_state.assignments['class'] != classroom]
    st.rerun()

def easter_egg():
    if 'The Ian Function' in st.session_state.classrooms['Name']:
        rain(emoji='👺', font_size=54, falling_speed=10)

#session state------------------------------------------------
if 'classrooms' not in st.session_state:
    st.session_state.classrooms = {'Name':[], 'Late Work':[], 'Period':[], 'Count':[]}

if 'assignments' not in st.session_state:
    st.session_state.assignments = pd.DataFrame(columns=['title', 'priority', 'due_date', 'time_est', 'class', 'link', 'done', 'overdue', 'late_allowed'])

if 'edited_df' not in st.session_state:
    st.session_state.edited_df = None

if 'bypass_autoload' not in st.session_state:
    st.session_state.bypass_autoload = False

if 'reruns' not in st.session_state:
    st.session_state.reruns = 0
st.session_state.reruns += 1
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
for i in st.session_state.classrooms['Name']:
    st.session_state.classrooms['Count'][st.session_state.classrooms['Name'].index(i)] = len(st.session_state.assignments[st.session_state.assignments['class'] == i])

for assignment in st.session_state.assignments.iterrows():
    if isinstance(assignment[1]['due_date'], str):
        assignment[1]['due_date'] = datetime.datetime.strptime(assignment[1]['due_date'], '%Y-%m-%d').date()
    
for index, assignment in st.session_state.assignments.iterrows():
    if assignment['due_date'] < datetime.date.today():
       st.session_state.assignments.loc[index, 'overdue'] = True

for index, assignment in st.session_state.assignments.iterrows():
    if assignment['done'] == False or 0 or 0.0:
        st.session_state.assignments.loc[index, 'done'] = False
    else:
        st.session_state.assignments.loc[index, 'done'] = True

for index, assignment in st.session_state.assignments.iterrows():
    if assignment['done'] == False or 0 or 0.0:
        st.session_state.assignments.loc[index, 'overdue'] = False
    else:
        st.session_state.assignments.loc[index, 'overdue'] = True

cookies = CookieManager()
if not cookies.ready():
    st.stop()

if st.session_state.reruns <=3 and not st.session_state.bypass_autoload and cookies.ready() and len(st.session_state.classrooms['Name']) == 0 and len(st.session_state.assignments) == 0:
    try:
        from_cookies = pd.read_json(cookies['assignments'])
        for index, row in from_cookies.iterrows():
            if type(row['due_date']) != datetime.date:
                from_cookies.loc[index, 'due_date'] = datetime.datetime.fromtimestamp(row['due_date']/1000, datetime.timezone.utc).date()
        from_cookies.fillna(value='about:blank', inplace=True)
        st.session_state.assignments = from_cookies
    except KeyError:
        pass
    try:
        st.session_state.classrooms = eval(cookies['classes'])
        st.session_state.bypass_autoload = True
    except KeyError:
        st.session_state.bypass_autoload = True
#gui----------------------------------------------------------
st.sidebar.title('Configuration')
sidebar_tabs = st.sidebar.tabs(['Class', 'Assignment', 'Delete'])
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

    st.subheader('Classes:')
    if len(st.session_state.classrooms['Name']) > 0:
        for classroom in st.session_state.classrooms['Name']:
            class_index = st.session_state.classrooms['Name'].index(classroom)
            count = st.session_state.classrooms['Count'][class_index]
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
                        new_assignment['link'] = ''
                    new_assignment['period'] = st.session_state.classrooms['Period'][st.session_state.classrooms['Name'].index(new_classroom)]
                    st.session_state.classrooms['Count'][st.session_state.classrooms['Name'].index(new_classroom)] += 1
                    new_assignment = pd.DataFrame(new_assignment, index=[0])
                    st.session_state.assignments = pd.concat([st.session_state.assignments, new_assignment], ignore_index=True)
                else:
                    st.error('Please enter a classroom.')
            else:
                st.error('Please enter a title.')

with sidebar_tabs[2]:
    with st.form('Delete_form', clear_on_submit=True):
        class_to_delete = st.selectbox('Choose a class to delete:', st.session_state.classrooms['Name'], help='Which class do you want to delete?', key=1234)
        if st.form_submit_button('Delete!', help='Delete a class.'):
            delete_classroom(class_to_delete)


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
    
class_filter = sac.segmented(items=['All', 'Edit'] + menu_list, divider=False, use_container_width=True, size='sm', radius='lg', on_change=update_assignments, key=6473).split(':')[0]

if class_filter == 'All':
    if len(st.session_state.assignments) > 0:
        remove_completed()
        st.dataframe(st.session_state.assignments, hide_index=True, use_container_width=True, column_order=COLUMN_ORDER, column_config=COLUMN_CONFIG)
    else:
        st.info('Create some assignments to get started!')

elif class_filter == 'Edit':
    if len(st.session_state.assignments) > 0:       
        st.session_state.edited_df = st.data_editor(st.session_state.assignments, hide_index=True, column_config=COLUMN_CONFIG, disabled=['overdue'], use_container_width=True, column_order=COLUMN_ORDER)
    else:
        st.info('Create some assignments to get started!')

else:
    remove_completed()
    class_index = (st.session_state.classrooms['Name'].index(class_filter))
    if st.session_state.classrooms['Late Work'][class_index] == True:
        st.success('Late Work Allowed!')
    else:
        st.error('Late Work Not Allowed!')
    if st.session_state.classrooms['Count'][class_index] > 0:
        st.dataframe(st.session_state.assignments[st.session_state.assignments['class'] == class_filter], hide_index=True, use_container_width=True, column_order=COLUMN_ORDER, column_config=COLUMN_CONFIG)
    else:
        st.info('No assignments for this class.')

if st.session_state.bypass_autoload:
    cookies['assignments'] = st.session_state.assignments.to_json()
    cookies['classes'] = str(st.session_state.classrooms)
    cookies.save()

easter_egg()