# The Process Mining Question Forge

## Description

The Process Mining Question Forge (PMQF) is a tool that implements guidance for the crucial task of question design in process mining projects. We developed PMQF based on findings from research that highlight that (experienced) process mining 
analysts often rely on domain knowledge or analysis templates when confronted with a project without clear questions. However, especially less-experienced analysts lack this knowledge and templates are not always available. Therefore PMQF 
leverages categorized example questions and a classification schema to help users in designing their own questions. It must be provided with a set of questions and a respective categorization schema. Based on it, PMQF
provides structured access to these resources, guiding users to design their own questions in a structured manner.

## Installation
PMQF is implemented as a Python Flask application. Follow these steps to get it up and running on your local machine:

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Setup

1. Clone the repository
2. Install all required dependencies (i.e., flask, pandas, numpy, matplotlib, seaborn, nltk, os, io, json, datetime)
3. Note that you need to install wordnet from the nltk library:  [https://www.nltk.org/data.html](https://www.nltk.org/data.html)
4. Run the application via python app.py. This will start the Fasl server, typically running on [http://127.0.0.1:5000](http://127.0.0.1:5000), unless configured otherwise.
5.Visit this URL in your web browser to interact with the PMQF application.

### Customization - Required to run the application!
1. Add your classification schema (json-file - more specifications are added below) to the folder `data`
2. Add your list of categorized questions as xlsx file to the folder `data`
3. Make sure to use the correct file names in app.py
4. Feel free to update any further explanaitions or gudining questions according to your pesonal classification schema in the app or template files. 

## Accessing the Deployed Application

For those who prefer not to install PMQF locally, a deployed version of the application is available. You can access it by visiting the following URL: [http://130.82.168.60:5000/](http://130.82.168.60:5000/). This allows you to explore and use PMQF's features without the need for local setup.

 
## Contact

Lisa Zimmermann - lisa.zimmermann@unisg.ch

## Acknowledgements
- This project is funded as part of the **ProMiSE Project** by the Swiss National Science Foundation under Grant No.: 200021_197032.
- Thank you to all friends and collegueas who tested the implementation and provided their feedback
- Thank you to the participants from industrie, who took part in the evaluation of the tool. 
