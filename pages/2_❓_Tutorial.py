import streamlit as st
import pandas as pd
import datetime
from streamlit_option_menu import option_menu

if 'dummy_assignments' not in st.session_state:
    st.session_state.dummy_assignments = [
    {'title': 'Algebra Quiz', 'priority': 'High', 'due_date': '2024-02-10', 'time_est': 2, 'class': 'Math', 'done': True, 'overdue': False},
    {'title': 'Geometry Homework', 'priority': 'Medium', 'due_date': '2024-02-15', 'time_est': 3, 'class': 'Math', 'done': False, 'overdue': False},
    {'title': 'Literature Analysis', 'priority': 'High', 'due_date': '2024-02-12', 'time_est': 4, 'class': 'English', 'done': False, 'overdue': True},
    {'title': 'Grammar Exercise', 'priority': 'Low', 'due_date': '2024-02-20', 'time_est': 1, 'class': 'English', 'done': False, 'overdue': False},
    {'title': 'Ancient Civilizations Research', 'priority': 'Medium', 'due_date': '2024-02-18', 'time_est': 5, 'class': 'History', 'done': True, 'overdue': True},
    {'title': 'World War II Essay', 'priority': 'High', 'due_date': '2024-02-14', 'time_est': 6, 'class': 'History', 'done': True, 'overdue': False},
]

st.set_page_config(
    page_title='Assignment Tracker Tutorial',
    layout='wide',
    page_icon=':question:',
    menu_items={
        'Get Help': 'https://assignmenttracker.streamlit.app/tutorial',
        'Report a bug': 'https://github.com/BassMaster629/assignment_tracker/issues',
    }
)

def update_assignments():
    global assignment_df
    if editing:
        st.session_state.dummy_assignments = assignment_df.to_dict(orient='records')

def remove_completed():
    old_amount = len(st.session_state.dummy_assignments)
    st.session_state.dummy_assignments = [assignment for assignment in st.session_state.dummy_assignments if not assignment['done']]
    amount_removed = old_amount - len(st.session_state.dummy_assignments)
    if amount_removed > 0:
        st.toast(f'Removed {amount_removed} assignments.')
        st.balloons()
        if len(st.session_state.dummy_assignments) == 0:
            st.toast('Congradulations on completing all your assignments!')
    else:
        st.toast('No completed assignments to remove.')

#sidebar--------------------------------------------------
st.sidebar.title('Configuration')
st.sidebar.info('This is where you go to create new classes and assignments.')
sidebar_tabs = st.sidebar.tabs(['Class', 'Assignment'])
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
    st.info('This :arrow_up: is an example of a class called "Math" that accepts late work (signified by the green border) and has 5 active assignments.')
    st.error('Math: 5 Assignments')
    st.info('This :arrow_up: is an example of a class called "Math" that does not accept late work (signified by the red border) and has 5 active assignments.')
    st.warning('No classes yet.')
    st.info('This :arrow_up: is displayed if you have no classes added.')

with sidebar_tabs[1]:
    st.info(':arrow_up: This tab is used to create new assignments.')
    with st.form(key='create_assignment'):
        new_title = st.text_input("Enter Title", max_chars=100, help='What is the assignment called?', value='Unit Circle Practice')
        new_priority = st.selectbox('Choose Priority:', ['High', 'Medium', 'Low'], help='How important is this assignment?')
        new_due_date = st.date_input('Enter Due Date:', help='When is this assignment due?')
        new_time_estimate = st.number_input('Enter Time Estimate:', step=5, help='How long do you think this assignment will take? (in minutes)', min_value=5, max_value=600, value=30)
        new_classroom = st.selectbox('Enter Class:', ['Math', 'English', 'History'], help='Which class is this assignment for?')
        st.form_submit_button('Create!', help='Create a new assignment.')
    st.info(':arrow_up: Press this to add the class to your list of classes. Note: this button will not function in this tutorial.')
    st.error('Please enter a classroom.')
    st.info('This :arrow_up: will appear if you attempt to create an assignment without a classroom.')
    st.error('Please enter a title.')
    st.info('This :arrow_up: will appear if you attempt to create an assignment without a title.')

st.title('Tutorial')
st.info('This is a tutorial for the Assignment Tracker app. Look for blue boxes like this one for instructions. Also look for question mark symbols for tips and explanations.')

columns = st.columns([0.85, 0.15])
with columns[0]:
    classroom_list = [None] * 6
    classroom_list[::2] = ['Math', 'English', 'History']
    amount_of_assignments = []
    for classroom in ['Math', 'English', 'History']:
        count = 0
        for assignment in st.session_state.dummy_assignments:
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
    class_filter = option_menu('Select Class', [f"All: {str(len([assignment for assignment in st.session_state.dummy_assignments if not assignment['done']]))}"] + classroom_list, orientation='horizontal', menu_icon='filter', icons=['list-check']*4)
    st.info('This :arrow_up: is a menu that allows you to filter your assignments by class. You can choose to display all assignments, or only assignments for a specific class.')
    class_filter = class_filter.split(':')[0]
    
with columns[1]:
    if class_filter == 'All':
        if len(st.session_state.dummy_assignments) > 0:
            editing = st.toggle('Edit Mode', value=False, on_change=update_assignments)
            st.info('This :arrow_up: is a toggle that allows you to edit your assignments.')

with columns[0]:
    for assignment in st.session_state.dummy_assignments:
        if isinstance(assignment['due_date'], str):
            assignment['due_date'] = datetime.datetime.strptime(assignment['due_date'], '%Y-%m-%d').date()

    assignment_df = pd.DataFrame(st.session_state.dummy_assignments)

    if class_filter == 'All':
        if editing:
            assignment_df = st.data_editor(
                assignment_df,
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
                        options=['Math', 'English', 'History'],
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
            st.info('This :arrow_up: is a data editor that allows you to edit your assignments. Mark them as done if you would like to remove them. Edits will not be saved until you toggle out of edit mode.')

        else:
            st.dataframe(
                assignment_df,
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
                        options=['Math', 'English', 'History'],
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
                hide_index=True
            )
            st.info('This :arrow_up: is a table of assignments. You can edit the assignments by turning on the edit mode toggle.')
            st.button('Remove Completed Assignments', help='Remove all assignments that are marked as done.', on_click=remove_completed)
            st.info('This :arrow_up: is a button that allows you to remove all assignments that are marked as done.')
            st.warning('Create some assignments to get started!')
            st.info('This :arrow_up: is a message that displays when there are no assignments to display.')

    else:
        st.success('Late Work Allowed!')
        st.info('This :arrow_up: is a message that displays when late work is allowed for the selected class.')
        st.error('Late Work Not Allowed!')
        st.info('This :arrow_up: is a message that displays when late work is not allowed for the selected class.')

        has_assignments = False
        for assignment in st.session_state.dummy_assignments:
            if assignment['class'] == class_filter:
                has_assignments = True
                break
        if has_assignments:
            filtered_data = assignment_df[assignment_df['class'] == class_filter]

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
                        options=['Math', 'English', 'History'],
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
            st.info('This :arrow_up: is a table of assignments containing only assignments for the selected class.')
            st.button('Remove Completed Assignments', on_click=remove_completed, help='Remove all assignments that are marked as done.')
            st.info('This :arrow_up: is a button that allows you to remove all assignments that are marked as done.')
        
            st.warning('You have no active assignments in this class.')
            st.info('This :arrow_up: is a message that displays when there are no assignments to display.')

with columns[1]:
    st.write('Save status: :warning:')
    st.info('This :arrow_up: is a message that displays when the assignments have not been saved. :white_check_mark: indicates that the assignments have been saved. :warning: indicates that the assignments have not been saved.')
    st.button('Load Assignments')
    st.info("This button :arrow_up: is used to import your assignments from your browser's cookies.")
    st.button('Save Assignments')
    st.info("This button :arrow_up: is used to save your assignments to your browser's cookies.")