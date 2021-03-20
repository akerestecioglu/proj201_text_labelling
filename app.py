from project import app, db
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from project.models import User
from project.forms import LoginForm
import os
import portpicker


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
    # burada ogrencinin girecegi portu almak gerekiyor
    os.environ['PRODIGY_HOST'] = "0.0.0.0"
    # port 0 olursa otomatik olarak bos porta atabilir
    available_port = int(portpicker.pick_unused_port())
    os.environ['PRODIGY_PORT'] = str(available_port)

    # db isimleri $username-ner-db-01 okunacak dosya da $username-ner-01.jsonl
    os.system('prodigy ner.manual {}-ner-db-01 blank:en ./{}-ner-01.jsonl --label PERSON,ORG,PRODUCT,LOCATION &'.format(current_user.username, current_user.username))
    # os.system('prodigy ner.manual eagaev-ner-db-01 blank:en ./eagaev-ner-01.jsonl --label PERSON,ORG,PRODUCT,LOCATION &')

    os.system('echo {} >> out'.format(current_user.username))
    os.system('ps -u reyyan >> out')
    # prodigy.serve("ner.manual ner_news_headlines blank:en ./news_headlines.jsonl --label PERSON,ORG,PRODUCT,LOCATION", port=available_port)

    # save the port, process_id
    current_user.update_last_process(available_port)
    db.session.commit()

    return redirect('http://vpa-com16.ddns.sabanciuniv.edu:{}/?session={}'.format(available_port, current_user.username), code=302)
    # return render_template('welcome_user.html')


# user giris yaptiktan sonra ona ait active process varsa ona yonlendir, yoksa usttekini yap ve id yi ve time stampi db ye kaydet
# pythondan process id ye nasıl ulasilir bak
# 1 saati dolduran tum processleri oldur


# login view
@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # grab the user from our User Models table
        user = User.query.filter_by(username=form.username.data).first()

        # check that the user was supplied and the password is right
        # the check_password method comes from the User object
        if user is not None and user.check_password(form.password.data):
            # log in the user
            login_user(user)
            flash('Logged in successfully!')

            # if the user has tried to access a page that required login
            next_page = request.args.get('next')
            if next_page is None or not next_page[0] == '/':
                next_page = url_for('welcome_user')

            return redirect(next_page)
        flash(u'Invalid Credentials!', 'error')

    return render_template('login.html', form=form)


# main
if __name__ == '__main__':
    app.run(host='0.0.0.0')
