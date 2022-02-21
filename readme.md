# Multi-User Software for Prodigy

## Dependencies

For installing the required packages, go to the directory where "requirements.txt" is located and run the command below in terminal.

```bash
pip install -r requirements.txt
```

## Description

The web application is designed for multiple users to annotate a collection of documents with a tool named Prodigy (https://prodi.gy/).

The application is developed with Flask (Python) and the user interface is implemented with HTML.

The application involves features such as registering users, distributing examples in a collection to users, starting Prodigy processes for users, calculating average pairwise Cohen's Kappa scores for each user, and reporting users that did not annotate any examples.

Although Prodigy has many recipes such as Named Entity Recognition, Text Classification, Part of Speech Tagging, Dependency Parsing, etc., the application is only suitable for Named Entity Recognition and Text Classification tasks. 


## Usage

### Before Running the Application

Before you start the app, you should run the 'all_in_one.py' script.

In the main function of the script, there are several functions. The purposes of these functions can be understood from their names.

As you can see below, the last two lines/functions are commented out. The reason is that those functions are for Cohen's Kappa calculations. They should be uncommented when the annotations are done.
Also, the upper lines except for the 3rd and 4th lines (usernames, db_name assignments) should be commented out while calculating Kappa.

The second parameters of start_prodigy, find_average_kappa_per_student, find_not_annotated_example_counts functions are the task type. This parameter must be one of 'ner' (for named entity recognition) and 'text_classification'.


```python
add_users_to_db('example_students.csv')
output_credentials('example_students.csv', 'credentials.txt')
usernames = get_usernames('example_students.csv')
db_name = 'ner-db-01'
distribute_sentences('deprem.jsonl', db_name, usernames, 60, 2)
time.sleep(5)
start_prodigy(usernames, 'ner', db_name, 'ADANA,BURSA,CEYHAN,DENIZLI', 'process_ids.txt')
#find_average_kappa_per_student(db_name, 'ner', usernames, f'{db_name}-average.csv')
#find_not_annotated_example_counts(db_name, 'ner', f'no-annotation-counts-{db_name}.txt')
```

The parameters and variables can be adjusted according to the needs.

##### add_users_to_db(file_name)

This function has a single parameter, which is the path of the file that the user information is going to be read from.

The input file should be in CSV format. The first line should be attribute names, which are: Surname, First name, ID number, Email address.

An example file would be as follows:

```text
Surname,First name,ID number,Email address
Picasso,Pablo,12371,pablopicasso@sabanciuniv.edu
Cameron,James,23134,jamescameron@sabanciuniv.edu
Wonder,Stevie,23746,steviewonder@sabanciuniv.edu
```

The function creates user instances for each line in the input file, and adds them to the database.

##### output_credentials(input_file_name, out_file_name)

This function has two parameters, which are the path of the file that the user information is going to be read from and the path of the output file.

It writes the passwords generated for users in the input file to the output file.

##### get_usernames(file_name)

This function reads the input file that stores information on users and returns a list of usernames. The purpose of the function is to feed other functions, i.e. it does not have functionality alone.

##### distribute_sentences(file_name, db_name, usernames, sents_per_student, students_per_sent)
The function creates a JSONL file for each user which consists of the examples assigned to him/her.

_Parameters:_
    
file_name: The path of the file in which the examples are stored. It should be in JSONL format so that it is compatible with Prodigy.

db_name: The name of the database that will store the annotations.

usernames: List of all usernames.

sents_per_student: The number of examples that will be assigned to each student.

students_per_sent: The number of students that will annotate a single example.

_**Warning**:_ There should be enough examples in the input file so that sents_per_student and students_per_sent conditions are met.

##### start_prodigy(usernames, task_type, db_name, labels, process_file_name)

This function starts a Prodigy process for each user and stores the port that the process is active on, in the database. Thus, the app directs the user to the same port every time he/she logs in.

It also produces a file that involves the ids of the Prodigy and Python processes started for each user so that the processes can be terminated manually when the task is done.

_Parameters:_
    
usernames: List of all usernames.

task_type: The type of task to be completed. Must be 'ner' or 'text_classification'.

db_name: The name of the database that will store the annotations.

labels: The label options to be chosen by the user. It must be a string. Labels should be separated by a comma. An example would be:

```python
"PERSON,ORGANIZATION,TIME,LOCATION"
``` 

process_file_name: The path of the file in which the process ids are stored.

##### find_average_kappa_per_student(dataset, db_type, students, output_file_name)

This function calculates all pairwise Cohen's Kappa scores for each student and outputs the average score per student.

_Parameters:_

dataset: The name of the database that will store the annotations.

db_type: The type of task to be completed. Must be 'ner' or 'text_classification'.

students: List of all usernames.

output_file_name: The path of the file in which the average scores will be written.

##### find_not_annotated_example_counts(dataset, db_type, output_file_name)

This function finds the number of examples that are not annotated by each user and writes it to a file.

_Parameters:_

dataset: The name of the database that will store the annotations.

db_type: The type of task to be completed. Must be 'ner' or 'text_classification'.

output_file_name: The path of the file in which the average scores will be written.

### Running the Application

To start the application, you should run the "app.py" script. The following code line starts the app.
```python
app.run(host='0.0.0.0')
```
The default port for the application is 5000. You can specify it by setting the 'port' parameter to the port you want to start the application.

```python
app.run(host='0.0.0.0', port=8000)
```

## File Organization

Under the 'PROJ201-ReyyanYeniterzi' folder, there are several scripts, files and folders. 

The app.py script is for starting the application and the all_in_one.py script is for making the necessary setup before running the app and evaluating the results at the end. 

Other scripts are there because the all_in_one.py script imports necessary functions from them.

**project**

_\_\_init\_\_.py:_ Configurations for Flask app. When you see a code piece such as "from project import ...", it means from "project.\_\_init\_\_.py import ...".

_forms.py_: Involves the login form.

_models.py_: Involves the User model.

_data.sqlite:_ SQLite database that stores the User instances.

_templates:_ HTML files for the user interface.

## Authors

Thanks to Dr. Reyyan Yeniterzi and Alihan Kerestecioğlu for their contributions.
