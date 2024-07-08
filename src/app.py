from flask import Flask, render_template, request, session,jsonify,send_file, Response, redirect, url_for
import pandas as pd
from pandas import read_json
import numpy as np
from nltk.corpus import wordnet #note that you might need to install wordnet: https://www.nltk.org/data.html

import matplotlib
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

import seaborn as sns
import os
from io import StringIO #, BytesIO
import csv
import json
from datetime import datetime
import sys
import logging

matplotlib.use('Agg')

app = Flask(__name__)
#app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.secret_key = "ABCD"


def load_and_prepare_question_bank(filename):
    """
    Load the question bank from an Excel file that is stored in the 'data' directory.
    """
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Move up to the parent directory (where 'data' is located)
    parent_dir = os.path.dirname(script_dir)
    file_path = os.path.join(parent_dir, "data", filename)
    data = pd.read_excel(file_path)
    # Drop rows where 'Question' is NaN and add a unique identifier
    data = data.dropna(subset=['Question'])
    data['unique_id'] = data.index
    
    return data

def load_taxonomy(filename):
    """
    Load taxonomy data from a JSON file that is stored in the 'data' directory..
    """
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Move up to the parent directory (where 'data' is located)
    parent_dir = os.path.dirname(script_dir)
    file_path = os.path.join(parent_dir, "data", filename)
    
    try:
        with open(file_path, 'r') as f:
            taxonomy = json.load(f)
        return taxonomy
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: The file {filename} contains invalid JSON.")
        return {}


#load data
raw_data = load_and_prepare_question_bank("QuestionBank_v3.xlsx")
taxonomy = load_taxonomy("taxonomy.json")

def getSynoyms(word):
    """Fetch synonyms for a given word."""
    synonyms = []
    word = str(word)
    for syn in wordnet.synsets(word):
        for i in syn.lemmas():
            synonyms.append(i.name())
    synonyms.append(word)
    return list(set(synonyms))

def filter_data(data, keywords):
    """Filter Data based on Question or Concept of Interest column based on keywords."""
    query = '|'.join(keywords)
    return data[
        data['Question'].str.lower().str.contains(query, na=False) |
        data['Concept of Interest'].str.lower().str.contains(query, na=False)
    ]
    
    

######################  In this app, some 'session' variables are set and used!   ######################  
'''
filtered_keywords - List of categorized that have been selected during the question design process
selectedQuestions - list of questions that have been entered or edited during the question refinement process
num_selected_questions - number of selected questions (used in the question design results page)
new_questions - list of questions that have been entered during the question refinement process
refinementQuestionsCategorized - dictionary of questions that have been categorized during the question refinement process  
'''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clear_session')
def clear_session():
    session.clear()
    return "Session cleared"

@app.route('/view_categorization')
def view_categorization():    
    return render_template('view_categorization.html', taxonomy_data = taxonomy)

@app.route('/search', methods=['GET', 'POST'])
def search():
    global raw_data
    data = raw_data

    if request.method == 'POST':
        keyword = request.form['keyword'].lower()
        synonyms = getSynoyms(keyword)
        # Filter the DataFrame based on the keyword
        filtered_df = filter_data(data, synonyms)
        number_of_results = len(filtered_df)
        data = filtered_df.to_dict('records')
    else:
        # If it's a GET request, display the full DataFrame
        data = data.to_dict('records')        
        number_of_results = len(data)        
        synonyms = []
    return render_template('search.html', data=data, synonyms=synonyms, taxonomy=taxonomy, number_of_results= number_of_results)


@app.route('/question_design')
def question_design():
    #to retrieve buttons that were previously selected
    previouslySelectedButtons = session.get('filtered_keywords', [])   
    return render_template('question_design.html', previouslySelectedButtons=previouslySelectedButtons)

def handle_subcategories(selected_values, request):
    """Handle subcategories for 'Describe' and 'Predict'."""
    subcategory_map = {
        'Describe': 'describe-subcategory',
        'Predict': 'predict-subcategory',
    }
    for key, value in subcategory_map.items():
        if key in selected_values:
            selected_values= list(selected_values)
            selected_values.remove(key)
            selected_values.extend(request.form.getlist(value))
    return selected_values

def update_filters(data, column_name, selected_values, filtered_keywords, filtered_dimensions, filtered_dict):
    """Update filters based on selected values."""
    data = data[data[column_name].isin(selected_values)]
    filtered_keywords.extend(selected_values)
    filtered_dimensions.append(column_name)
    filtered_dict.setdefault(column_name, []).extend(selected_values)
    return data

@app.route('/question_design_results', methods=['GET', 'POST'])
def results():        
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        checked_questions = request.form.getlist('questionCheckbox')
        previously_selected_questions = session.get('selectedQuestions', [])        
        checked_questions.extend(previously_selected_questions)
        num_selected_questions = len(checked_questions)
        session['selectedQuestions'] = checked_questions
        session['num_selected_questions'] = num_selected_questions       
        return jsonify(success=True)
    else:
        #reset data for every request of this page to always filter dataset from scratch
        global raw_data
        data = raw_data

        filtered_keywords = [] #filtered_keywords = session.get('filtered_keywords', [])
        filtered_dimensions = [] #filtered_dimensions = session.get('filtered_dimensions', [])
        filtered_dict = {}

        # Create a dictionary that maps the names used in the html form to the DataFrame column names
        form_to_column = {
            'UseCaseDimension': 'Use Case',
            'PrimaryGoalDimension': 'Primary Goal',
            'PerspectiveDimension': 'Perspective',
            'CognitiveStepDimension': 'Cognitive Step',
            'DataLevelDimension': 'Data Level'
        }

        # Loop over the dictionary
        for form_name, column_name in form_to_column.items():
            if form_name in request.form:
                selected_values = set(request.form.getlist(form_name))

                # If "Describe" or "Predict" is selected, handle the subcategories
                if column_name == 'Primary Goal':
                    selected_values = handle_subcategories(selected_values, request)

                # If any values are selected, filter the DataFrame and update the keywords and dimensions
                if len(selected_values) > 0:
                    data = update_filters(data, column_name, selected_values, filtered_keywords, filtered_dimensions, filtered_dict)

        num_questions = len(data)
        data_dict = data.to_dict(orient='records')

        #update session variables        
        session['filtered_keywords'] = filtered_keywords
        num_selected_questions = session.get('num_selected_questions', 0) 

        return render_template('question_design_results.html', data=data_dict,num_questions=num_questions, filtered_keywords=filtered_keywords, filtered_dimensions=filtered_dimensions, filtered_dict=filtered_dict, num_selected_questions=num_selected_questions)


@app.route('/handle_bulk_reformulation', methods=['POST'])
def handle_bulk_reformulation():
    data = read_json(StringIO(session.get('dataSubset', '[]')), orient='records')    
    if 'delete_question' in request.form:
        # Handle deletion
        question_id_to_delete = int(request.form['delete_question'])
        data = data[data['unique_id'] != question_id_to_delete]
        
        #remove question from selectedQuestionsIDList
        selectedRows = list(set(session.get('selectedQuestions', [])))
        selectedRows = [int(i) for i in selectedRows]        
        if question_id_to_delete in selectedRows:
            selectedRows.remove(question_id_to_delete)
            session['selectedQuestions'] = selectedRows
        
    else:
        reformulations = request.form.getlist('reformulation[]')
        question_ids = request.form.getlist('question_id[]')

        for question_id, reformulation in zip(question_ids, reformulations):
            if reformulation:  # Only update if there's a reformulation provided
                question_id = int(question_id)
                data.loc[data['unique_id'] == question_id, 'Question'] = reformulation
                data.loc[data['unique_id'] == question_id, 'Source'] = 'Reformulated'

    session['dataSubset'] = data.to_json(orient='records')
    return redirect(url_for('getSelectedQuestions'))

@app.route('/getSelectedQuestions', methods=['POST','GET'])
def getSelectedQuestions():
        
    #reload questionBank 
    global raw_data
    data = raw_data      

    selectedRows = list(set(session.get('selectedQuestions', [])))
    selectedRows = [int(i) for i in selectedRows]

    # filter rows based on list values
    selectedQuestions = data[data['unique_id'].isin(selectedRows)]

    #if question have been reformulated their content will be replaced with the formulation from the one in the dataframe:
    potentially_reformulated = read_json(StringIO(session.get('dataSubset','[]')), orient='records')
    if not potentially_reformulated.empty:
        selectedQuestions.set_index('unique_id', inplace=True)
        potentially_reformulated.set_index('unique_id', inplace=True)
        selectedQuestions.update(potentially_reformulated[['Question','Source']])
        selectedQuestions.reset_index(inplace=True)

    num_selected_questions = len(selectedQuestions)
    viz_path= generateHeatmap(selectedQuestions)
    QuestionsSelected = selectedQuestions.to_dict(orient='records')
    #to allow for the export of the selected questions
    session['dataSubset'] = selectedQuestions.to_json(orient='records')

    return render_template('display_questions_for_design.html', QuestionsSelected=QuestionsSelected, heatpmap_path = viz_path, num_selected_questions=num_selected_questions)

@app.route('/export', methods=['GET'])
def export():    
    data = read_json(StringIO(session.get('dataSubset','[]')), orient='records')
    if not data.empty: 
        data = data[['Question', 'Use Case','Perspective','Primary Goal','Cognitive Step','Data Level', 'Context']]   
        csv_string = data.to_csv(index=False)
        response = Response(csv_string, mimetype='text/csv')
        response.headers.set('Content-Disposition', 'attachment', filename='export.csv')
    else: 
        response = Response("No data to export", mimetype='text/plain')
    return response



@app.route('/question_refinement', methods=['GET', 'POST'])
def question_refinement():
    return render_template('question_refinement.html')


@app.route('/submit_all_questions', methods=['POST'])
def submit_all_questions():
    questions = request.json.get('questions')
    session['new_questions'] = questions
    questions_for_categorization = {question: {} for question in questions} #transform questions into dictionary for categorization
    session['refinementQuestionsCategorized'] = questions_for_categorization
    return redirect(url_for('question_refinement_assessment'))

@app.route('/question_refinement_assessment', methods=['GET', 'POST'])
def question_refinement_assessment():

    questions_for_categorization = session.get('refinementQuestionsCategorized', {})
    
    if request.method == 'POST':
        selections = request.form
        for question, selection in selections.items():
            selectionvalue=question.split('_')
            questionText=selectionvalue[0]
            dimension=selectionvalue[1]
            # If the question is not already in the dictionary, add it
            if questionText not in questions_for_categorization:
                questions_for_categorization[questionText] = {}
            # Add the selection for the dimension to the question's dictionary
            questions_for_categorization[questionText][dimension] = selection
        
        session['refinementQuestionsCategorized'] = questions_for_categorization
    return render_template('display_questions_for_refinement.html', questions=list(questions_for_categorization.keys()), taxonomy = taxonomy, questions_for_categorization=questions_for_categorization)


@app.route('/update_question_from_refinement', methods=['POST'])
def update_question():
    index = int(request.form.get('index')) -1
    all_questions = session.get('refinementQuestionsCategorized', {})
    questions = list(session['refinementQuestionsCategorized'].items())
    questions[index] = (request.form.get('question'), questions[index][1])
    session['refinementQuestionsCategorized'] = dict(questions)
    return redirect(url_for('question_refinement_assessment'))

@app.route('/add_question_from_refinement', methods=['POST'])
def add_question():
    new_questions = session.get('refinementQuestionsCategorized', {})
    question = request.form.get('add_question')  
    if question not in new_questions:
        new_questions[question] = {}
    session['refinementQuestionsCategorized'] = new_questions
    return redirect(url_for('question_refinement_assessment'))



@app.route('/export_refinedQuestions', methods=['GET'])
def export_refinedQuestions(): 
    refinedquestions = session.get('refinementQuestionsCategorized', {})
    if refinedquestions:
        df = pd.DataFrame(refinedquestions) 
         # Generate a unique filename using a timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f'export_{timestamp}.csv'
        # Save the DataFrame to a CSV file in the backend        
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir) # Move up to the parent directory (where 'data' is located)
        save_path = os.path.join(parent_dir, "data", "categorized_user_questions", filename)
        df.to_csv(save_path, index=True, sep=';')
        
        # Generate the CSV string for user download
        csv_string = df.to_csv(index=True, sep=';')
        response = Response(csv_string, mimetype='text/csv')
        response.headers.set('Content-Disposition', 'attachment', filename='export.csv')
    else:
        response = Response("No data to export", mimetype='text/plain')
    return response


def generateHeatmap(df, path=None):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path= os.path.join(script_dir, 'static', 'heatmapAnalytics.png')
    
    relevant_columns = ['Use Case','Perspective','Primary Goal','Cognitive Step','Data Level', 'Context']
    
    taxonomyCategories = {        
        'Context': ['Domain-specific', 'Domain-agnostic'],
        'Use Case': ['Transparency', 'Performance', 'Compliance', 'Automation'],
        'Perspective': ['Control-Flow', 'Time', 'Data', 'Resources', 'Costs', 'Unspecific'],
        'Primary Goal': ['Describe: Qualitative', 'Describe: Quantitative', 'Explain', 'Confirm', 'Predict: P. Execution', 'Predict: What-If', 'Prescribe'],
        'Cognitive Step': ['Identify', 'Compare', 'Summarize'],
        'Data Level': ['Log', 'Trace', 'Event', 'Unspecific']
    }
                 
    reduced_data = df[relevant_columns]
    freq_dfs = [pd.DataFrame({
    'normalized': reduced_data[col].value_counts(normalize=True),
    'non_normalized': reduced_data[col].value_counts(normalize=False)
}) for col in reduced_data.columns]
    
    fig, axs = plt.subplots(len(freq_dfs), 1, figsize=(10, len(freq_dfs)))

    for i, df in enumerate(freq_dfs):
        df = df.T  # Convert Series to DataFrame
        # add missing values to the dataframe
        for value in taxonomyCategories[relevant_columns[i]]:
            if value not in df.columns:
                df[value] = 0

        # Create an array of labels with the category names and percentages
        #labels = [f"{col[:10]}\n{col[10:]}\n{value[0]*100:.1f}%" if len(col) > 10 else f"{col}\n{value[0]*100:.1f}%" for col, value in df.items()]
        labels = [f"{col}\n{int(value['non_normalized'])}" for col, value in df.items()]

        # Create the heatmap with the labels
        #axs[i] = plt.subplot(gs[i, :len(df.columns)])  # Create a subplot in the grid
        sns.heatmap(df.loc[["normalized"]], annot=np.array([labels]), fmt='', cmap='Greens',annot_kws={"size": 6}, ax=axs[i], cbar=False, linewidths=0.5, linecolor='#005C20')
        
        axs[i].set_ylim(-0.5, 1)  # Adjust y-axis limits to show all cell borders
        #axs[i].set_xlim(-0.5, len(df.columns) + 0.5)  # Adjust y-axis limits to show all cell borders

        axs[i].set_title(freq_dfs[i].index.name)  # Set title to the name of the column
        axs[i].set_xticks([])  # Remove x-ticks
        axs[i].set_xlabel('')  # Remove x-axis label
        axs[i].set_yticks([])  # Remove y-ticks
        axs[i].set_ylabel('')  # Remove y-axis label

        axs[i].axvline(x=len(df.columns), ymin= 0.35, ymax=1, color='#005C20', linewidth=0.5)

        fig.savefig(path, bbox_inches='tight', dpi=300)    
    return 'heatmapAnalytics.png'



if __name__ == '__main__':
    app.run(debug=True)


