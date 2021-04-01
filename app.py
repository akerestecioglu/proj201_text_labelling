
from project import app, db
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from project.models import User
from project.forms import LoginForm
import os
import portpicker

# forgot password view
@app.route('/forgot_password')
def forgot_password():
    return render_template("forgot_password.html")


# logout view
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out!')
    return redirect(url_for('login'))


# this view will direct the user to prodigy
@app.route('/welcome')
@login_required
def welcome_user():
    # check if the user has an active prodigy process
    if current_user.has_active_process():
        return redirect('http://vpa-com16.ddns.sabanciuniv.edu:{}/?session={}'.format(current_user.used_port, current_user.username), code=302)
    os.environ['PRODIGY_HOST'] = "0.0.0.0"
    # pick an available port to start the prodigy process
    available_port = int(portpicker.pick_unused_port())
    os.environ['PRODIGY_PORT'] = str(available_port)

    # start prodigy
    os.system('prodigy ner.manual {}-ner-db-01 blank:en ./{}-ner-01.jsonl --label PERSON,ORG,PRODUCT,LOCATION &'.format(current_user.username, current_user.username))

    # save the port information to db
    current_user.update_last_process(available_port)
    db.session.commit()

    return redirect('http://vpa-com16.ddns.sabanciuniv.edu:{}/?session={}'.format(available_port, current_user.username), code=302)


# login view
@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # grab the user instance
        user = User.query.filter_by(username=form.username.data).first()

        # check if the user exists and the password is right
        if user is not None and user.check_password(form.password.data):
            # log in the user
            login_user(user)
            flash('Logged in successfully!')

            # if the user has tried to access a page that required login
            next_page = request.args.get('next')
            if next_page is None or not next_page[0] == '/':
                next_page = url_for('welcome_user')

            return redirect(next_page)
        # show an error message
        flash(u'Invalid Credentials!', 'error')
    # redirect to the login page if the form is not submitted correctly
    return render_template('login.html', form=form)


# main
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
