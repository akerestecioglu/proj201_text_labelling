import pandas as pd
from project.models import User
from project import db


# function to generate a password for student
def generate_password(name, su_id):
    return name + str(su_id % 10) + str(su_id % 7) + str(su_id % 4)


# function to add users in a file to db
# file_name should be csv
def add_users_to_db(file_name):
    df = pd.read_csv(file_name)
    # for each student
    for index, row in df.iterrows():
        # extract the username from email adress
        username = row['Email address'][:row['Email address'].index('@')]
        # check if user in db
        user_exist = User.query.filter_by(username=username).first()
        if not user_exist:
            # generate password
            password = generate_password(username, row['ID number'])
            # create new user instance
            user = User(email=row['Email address'],
                        username=username,
                        su_id=row['ID number'],
                        first_name=row['First name'],
                        surname=row['Surname'],
                        password=password)
            # add user to db
            db.session.add(user)
            db.session.commit()


# function to write the username-password pairs to a file
def output_credentials(input_file_name, out_file_name):
    with open(out_file_name, 'w') as out_file:
        df = pd.read_csv(input_file_name)
        for index, row in df.iterrows():
            # extract username from email adress
            username = row['Email address'][:row['Email address'].index('@')]
            # generate password
            password = generate_password(username, row['ID number'])
            # write credentials
            out_file.write(username + ' - ' + password + '\n')


# function to get the list of all usernames in a file
def get_usernames(file_name):
    df = pd.read_csv(file_name)
    usernames = []
    # add username of the student to the list of usernames
    for index, row in df.iterrows():
        # get username from email adress
        username = row['Email address'][:row['Email address'].index('@')]
        usernames.append(username)
    return usernames