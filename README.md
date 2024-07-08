# The Process Mining Question Forge

## Description
The Process Mining Question Forge (PMQF) is a tool that implements guidance for the crucial task of question design in process mining projects. We developed PMQF based on findings from research that highlight that (experienced) process mining analysts often rely on domain knowledge or analysis templates when confronted with a project without clear questions. However, especially less experienced analysts lack this knowledge and templates are not always available. Therefore PMQF leverages categorized example questions and a classification schema to help users in designing their own questions. It must be provided with a set of questions and a respective categorization schema. Based on it, PMQF provides structured access to these resources, guiding users to design their own questions in a structured manner.

## Installation
PMQF is implemented as a Python Flask application. Follow these steps to get it up and running on your local machine:

### Prerequisites
- Python 3.6 or higher
- pip (Python package installer)

### Setup
1. Clone the repository
2. Install all required dependencies (i.e., flask, pandas, numpy, matplotlib, seaborn, nltk, os, io, json, datetime)
3. Note that you need to install wordnet from the nltk library:  [https://www.nltk.org/data.html](https://www.nltk.org/data.html)
4. Run the application via python app.py. This will start the Flask server, typically running on [http://127.0.0.1:5000](http://127.0.0.1:5000), unless configured otherwise.
5. Visit this URL in your web browser to interact with the PMQF application.

### Customization - Required to run the application!
1. Add your classification schema (json - more specifications are added below) to the folder `data`
2. Add your list of categorized questions to the folder `data` (csv or xlsx file - you might need to modify the import slightly, depending on which type you use)
3. Make sure to use the correct file names in app.py
4. Feel free to update the explanations or guiding questions according to your personal classification schema in the app and template files. 

## Creating Your Classification Schema
To customize PMQF for your specific needs, you'll need to create your own classification schema in a json file. This file should be placed in the `data` folder. The classification schema is crucial for categorizing questions and guiding the question design process within PMQF.

### Structure of your json file
```json
[{
  "text": "Dimension Name",
  "description": "Definition for the Dimension",
        "nodes": [{
                "name": "Name of the category",
                "text": "1) Name of the category",
                "description": "Definition of the category",
                "example": "Example for the question"           
        },
        {Category 2}
        ...]
},
{
"text": "Dimension 2"...
}
...
]
```


## Accessing the Deployed Application
For those who prefer not to install PMQF locally, a deployed version of the application is available. You can access it by visiting the following URL: [http://130.82.168.60:5000/](http://130.82.168.60:5000/). This allows you to explore and use PMQF's features without the need for local setup.

 
## Contact
Lisa Zimmermann - lisa.zimmermann@unisg.ch

## Acknowledgements
- This project is funded as part of the **ProMiSE Project** by the Swiss National Science Foundation under Grant No.: 200021_197032.
- We would like to express my gratitude to all colleagues and friends who participated in the trial and provided valuable feedback.
- We would like to thank the individuals from the industry who participated in the assessment of the tool. 
