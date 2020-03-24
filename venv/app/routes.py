from flask import Flask, render_template, request, session, redirect, url_for
from functools import wraps
import auth, main, getProfile
import uuid
import datetime
from flask_socketio import SocketIO, emit
import copy


app = Flask(__name__)
app.secret_key = 'XgHwOW8G73&2wAGN'
# socketio = SocketIO(app)


def login_required(f):
    @wraps(f)
    def check_logged_in_and_active(*args, **kwargs):
        # print("LOGIN REQUIRED")
        if "access_token" in session and "expires_at" in session:
            if session['expires_at'] > datetime.datetime.now():
                return f(*args, **kwargs)
                # print("Logged in, expires at: " + session["expires_at"])
            else:
                # print("Logged in, but needs a refresh")
                login_refresh()
                return f(*args, **kwargs)
        else:
            return redirect(url_for('login_timed_out'))
    return check_logged_in_and_active


@app.context_processor
def my_utility_processor():
        def authlink():
                if 'state' in session:
                    return main.get_auth_link(session['state'])
                else:
                    return "FAILURE"
        # For troubleshooting only
        def get_state():
            if 'state' in session:
                return session['state']
            else:
                return "No Current State"
        return dict(authlink=authlink(), state=get_state())






@app.route('/')
def home():
        if 'state' not in session:
            session['state'] = str(uuid.uuid4())
        return render_template('home.html')


@app.route('/about')
def about():
        return render_template('about.html')

@app.route('/login/authorized', methods=['GET','POST'])
def testing_postpoint():
        data_received = {}
        print("State: ")
        print(session['state'])
        print('\n')
        print("Received data: ")
        print(request.form)
        print('\n')
        if 'state' in session:
            success = auth.handle_auth_response(request,session['state'])
            data_received['Success'] = success
        return render_template('/testing/post_endpoint.html', post_dict=data_received)


@app.route('/login/authorized_test', methods=['POST'])
def login_authorized():
        if 'state' in session:
            if auth.handle_auth_response(request, session['state']):
                tokens = main.get_token_web(request)
                session['access_token'] = tokens['access_token']
                session['refresh_token'] = tokens['refresh_token']
                session['expires_at'] = datetime.datetime.now() + datetime.timedelta(0, tokens["expires_in"])
                return render_template('/login/success.html')
            else:
                return render_template('/login/failure.html')

        else:
            return render_template('/login/failure.html')

        # return render_template('logging_in.html')


@app.route('/login/refresh')
def login_refresh():
    new_token_dict = main.get_refreshed_token(session["refresh_token"])
    session['access_token'] = new_token_dict['access_token']
    session['refresh_token'] = new_token_dict['refresh_token']
    session['expires_at'] = datetime.datetime.now() + datetime.timedelta(0,new_token_dict["expires_in"])
    return render_template('/login/refresh.html')


@app.route('/login/timed_out')
def login_timed_out():
    session.clear()
    session['state'] = str(uuid.uuid4())
    return render_template('/login/timed_out.html')


@app.route('/login/sign_out')
def login_sign_out():
    session.clear()
    session['state'] = str(uuid.uuid4())
    return render_template('/login/sign_out.html')


@app.route('/me')
@login_required
def me():
    person_dict = getProfile.get_profile(session['access_token'])
    # print(session['expires_at'])
    # profile_dict = {"Key":"Value","Key2":"Value2"}
    return render_template('/me.html', profile_dict=person_dict)


@app.route('/schedule/choose')
@login_required
def schedule_choose():
    return render_template('/schedule/choose.html')


@app.route('/schedule/visualisation')
@login_required
def schedule_visualization():
    if 'schedules' not in session:
        return render_template('/schedule/choose.html')
    else:
        data = main.getSchedules(session['schedules'], session['access_token'])
    return render_template('/schedule/visualisation.html')


@app.route('/schedule/submit_choice', methods=['GET', 'POST'])
@login_required
def schedule_submit_choice():
    if request.method == "POST":
        schedules = request.form.get('schedules')
        # print("OG DATA: " + str(request.form.to_dict()))
    elif request.method == "GET":
        schedules = request.args.get('schedules')

    else:
        return render_template('/login/failure.html')
    schedules_list = False
    if schedules is not None:
        schedules_list = main.verify_profiles(schedules, session['access_token'])
        # print("LISTIFIED: " + str(schedules_list))
    if schedules_list is not False:
        session['schedules'] = schedules_list
        # print(schedules_list)
        return redirect('/schedule/visualisation')
    return render_template('/schedule/choose.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
    # socketio.run(app)
