from flask import Flask, render_template, request, session, redirect, url_for, send_file
from functools import wraps
import auth, main, getProfile, getMail, getStorage
import uuid
import datetime
from flask_socketio import SocketIO, emit
import copy
from base64 import b64encode # For loading image binary objects
import avinit # Avatar generation for people without photos

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
        #if 'access_token' in session:
            #return render_template('/schedule/visualization.html')
        if 'state' not in session:
            #print("#########################New Session!#######################")
            session['state'] = str(uuid.uuid4())
        return render_template('home.html')

@app.route('/testing/enter_data')
def testing_enter_data():
    data_dict = {}
    return render_template('/testing/enter_data.html')

@app.route('/testing/process_data', methods=['POST'])
def testing_process_data():
    session['test_data'] = request.form
    return redirect(url_for('testing_view_data'))

@app.route('/testing/view_data')
def testing_view_data():
    data_dict = {}
    if 'test_data' in session:
        data_dict = session['test_data']
    return render_template('/testing/view_data.html',data_dict=data_dict)


@app.route('/about')
def about():
        return render_template('about.html')

@app.route('/login/authorized', methods=['POST'])
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


@app.route('/login/authorized_test', methods=['POST'])

def testing_postpoint():
        data_received = {}
        print("State: ")
        print(session['state'])
        print('\n')
        print("Received data: ")
        print(request.form.to_dict())
        print('\n')
        if 'state' in session:
            success = auth.handle_auth_response(request,session['state'])
            data_received['Success'] = success
        return render_template('/testing/post_endpoint.html', post_dict=data_received)

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
    photo = getProfile.get_photo(person_dict['mail'], session['access_token'])
    photo_b64 = b64encode(photo).decode("utf-8")
    # print(session['expires_at'])
    # profile_dict = {"Key":"Value","Key2":"Value2"}
    teams = getProfile.get_joined_teams(session['access_token'])
    return render_template('/me/me.html', profile_dict=person_dict, image=photo_b64, groups=teams)

@app.route('/me/storage', methods=['GET','POST'])
@login_required
def me_storage():
    # NEED TO SET PERMS FOR SHAREPOINT ACCESS
    if request.method == "POST": # First submission of group id
        #print(request.form.get('group_id'))
        group_id = request.form.get('group_id')
        folders = getStorage.get_root_folders(session['access_token'],group_id)  # Needs to get folders from site listed in GET request.
        session['group_id'] = group_id
        path_tuple_list = [(None, "Base Directory")]

    elif request.method == "GET":
        if request.args.get('folder') is not None and request.args.get('folder') != "None":
            folders = getStorage.get_child_folders(session['access_token'], session['group_id'], request.args.get('folder'))
            path_tuple_list = getStorage.get_path_tuples(session['access_token'], session['group_id'], request.args.get('folder'))
            current_folder = getStorage.get_item_name(session['access_token'], session['group_id'], request.args.get('folder'))
        else:
            return redirect('/me')
    person_dict = getProfile.get_profile(session['access_token'])
    photo = getProfile.get_photo(person_dict['mail'], session['access_token'])
    photo_b64 = b64encode(photo).decode("utf-8")
    return render_template('/me/storage.html', folder_list=folders, image=photo_b64, path_tuple_list=path_tuple_list)

@app.route('/me/enter_faculty', methods=['GET'])
@login_required
def enter_faculty():
    return render_template('/me/enter_faculty.html')

@app.route('/me/submit_faculty_persons', methods=['POST'])
@login_required
def me_submit_faculty_persons():
    persons_list = request.form.get('persons_list')
    person_faculty_list = []
    persons_list = persons_list.split("\n")
    print(str(persons_list))
    for line in persons_list:
        faculty = getMail.lookup_level_one_staff(session['access_token'],line.strip())
        person_faculty_list.append(line.strip() + "," + str(faculty))


    return_string = ''
    for item in person_faculty_list:
        return_string = return_string  + str(item) + "\n"
    return return_string


@app.route('/schedule/choose')
@login_required
def schedule_choose():
    coworkers = getProfile.get_coworker_emails(session['access_token'])
    coworker_string = ', '.join(coworkers)
    print(coworker_string)
    return render_template('/schedule/choose.html', default_emails=coworker_string)


@app.route('/schedule/visualisation')
@login_required
def schedule_visualization():
    av_settings_dict = {'height':'120','width':'120','font-size':'60'} # Some custom settings for avatar generation in avinit
    if 'schedules' not in session:
        return render_template('/schedule/choose.html')
    else:
        data = main.getSchedules(session['schedules'], session['access_token'], session['tz_offset'])
        photos = {}
        for user_email in data:
            data[user_email]['given_name'] = getProfile.get_given_name(user_email, session['access_token'])
            raw_photo = getProfile.get_photo(user_email, session['access_token'])
            if not raw_photo:
                print("No photo for ", user_email, "-  generating one")

                photo = avinit.get_avatar_data_url(getProfile.get_display_name(user_email, session['access_token']), **av_settings_dict)
            else:
                photo = "data:;base64," + b64encode(raw_photo).decode("utf-8")
            photos[user_email] = photo

    return render_template('/schedule/visualization.html', schedule_dict=data, photos=photos)


@app.route('/schedule/submit_choice', methods=['GET', 'POST'])
@login_required
def schedule_submit_choice():
    if request.method == "POST":
        schedules = request.form.get('schedules')
        tz_offset = request.form.get('timezone_offset')
        # print("OG DATA: " + str(request.form.to_dict()))
    elif request.method == "GET":
        schedules = request.args.get('schedules')
        tz_offset = request.args.get('timezone_offset')
    else:
        return render_template('/login/failure.html')
    session['tz_offset'] = tz_offset
    schedules_list = False
    if schedules is not None:
        schedules_list = main.verify_profiles(schedules, session['access_token'])
        # print("LISTIFIED: " + str(schedules_list))
    if schedules_list is not False:
        session['schedules'] = schedules_list

        # print(schedules_list)
        return redirect('/schedule/visualisation')
    return render_template('/schedule/choose.html')

@app.route('/mail/choose',methods=['GET'])
@login_required
def mail_choose():
    mail_folders = getMail.get_users_folders(session['access_token'])
    print(mail_folders)
    return render_template('/mail/choose.html',folders_list=mail_folders)

@app.route('/mail/submit_choice',methods=['POST'])
@login_required
def mail_submit_choice():
    choice_dict = request.form.to_dict()
    print(choice_dict)
    mail_stats = getMail.handle_choices(session['access_token'],choice_dict)
    #session['mail_stats'] = mail_stats
    # TESTING
    return render_template('/testing/post_endpoint.html',post_dict=mail_stats)
    #return redirect('/mail/stats', code=307)

@app.route('/mail/stats',methods=['GET','POST'])
@login_required
def mail_stats():
    if 'mail_stats' in session:
        return render_template('/testing/post_endpoint.html', post_dict=session['mail_stats'])
    elif request.form:
        mail_stats = request.form.to_dict()
        return render_template('/testing/post_endpoint.html',post_dict=mail_stats)
    else:
        return redirect('/mail/choose')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
    # socketio.run(app)
