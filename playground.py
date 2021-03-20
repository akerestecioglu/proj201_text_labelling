
from project.models import User
from project import db
'''
users = ['fatihbeyhan', 'busecarik', 'reyyan']
for username in users:
    user = User.query.filter_by(username=username).first()
    db.session.delete(user)
    db.session.commit()
'''

with open('deneme.txt', 'w') as file:
    for i in range(3):
        file.write(str(i) + '\n')