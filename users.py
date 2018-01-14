import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
import datetime

import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'chenxu321'  # CHANGE THIS TO YOUR MYSQL PASSWORD
app.config['MYSQL_DATABASE_DB'] = 'project'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# begin code used for login*****************************************************************************
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email from Users")
    return cursor.fetchall()


def getUserIdList():
    cursor = conn.cursor()
    cursor.execute("SELECT user_id from Users")
    return cursor.fetchall()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
    # The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    # check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user
            return flask.redirect(flask.url_for('protected'))  # protected is a function defined in this file

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register/", methods=['GET'])
def register():
    return render_template('improved_register.html', supress='True', message="register for new account")


@app.route("/register/", methods=['POST'])
def register_user():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        hometown = request.form.get('hometown')
        gender = request.form.get('gender')
        date_of_birth = request.form.get('date_of_birth')

        # print credentials out
        print(email, password, first_name, last_name, hometown, gender)

    except:
        print "account already exist"  # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))

    cursor = conn.cursor()
    test = isEmailUnique(email)

    if test:
        print cursor.execute(
            "INSERT INTO Users (email, password, first_name,last_name,hometown,gender,date_of_birth) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}')".format( \
                email, password, first_name, last_name, hometown, gender, date_of_birth))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        user.name = (first_name + " " + last_name)
        flask_login.login_user(user)
        return render_template('hello.html', name=flask_login.current_user.name, message='Account Created!')
    else:
        print "couldn't find all tokens"
        return flask.redirect(flask.url_for('register'))


# *********************************************************************************************************************
def getUserAlbums(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Albums WHERE user_id = '{0}'".format(uid))
    result = [[col.encode('utf8') if isinstance(col, unicode) else col for col in row] for row in cursor.fetchall()]
    result = [i[0] for i in result]
    return result  # NOTE list of tuples, [(imgdata, pid), ...]


def getUsersPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT p.data, a.name, p.caption, p.photo_id from photos p, albums a \
			WHERE a.user_id = '{0}' AND p.album_id = a.album_id".format(uid))
    return cursor.fetchall()


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]


def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email FROM Users WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True


def getAlbumsPhotos(name, uid):
    cursor = conn.cursor()
    cursor.execute("SELECT p.data, a.name, p.caption, p.photo_id from photos p, albums a \
    		WHERE a.user_id = '{0}' AND a.name = '{1}' AND p.album_id = a.album_id".format(uid, name))
    return cursor.fetchall()


def getTagId(text):
    cursor = conn.cursor()
    cursor.execute("SELECT tag_id FROM Tags WHERE text = '{0}'".format(text))
    return cursor.fetchall()


def getAlbumId(name):
    cursor = conn.cursor()
    cursor.execute("SELECT album_id FROM Albums WHERE name = '{0}'".format(name))
    return cursor.fetchall()


# *********end login code*********************************************************************************************
@app.route('/profile')
@flask_login.login_required
def protected():
    email = flask_login.current_user.id
    uid = getUserIdFromEmail(email)
    cursor.execute(
        "SELECT first_name, last_name, user_id, email, date_of_birth, hometown, gender FROM Users WHERE email = '{0}'".format(
            email))
    name = [[col.encode('utf8') if isinstance(col, unicode) else col for col in row] for row in cursor.fetchall()]
    # user can access profile after logging in

    profile = [["user ID:", int(name[0][2])], ["firstname:", name[0][0]], ["lastname:", name[0][1]], \
               ["email:", name[0][3]], ["date of birth:", name[0][4]], ["hometown:", name[0][5]],
               ["gender:", name[0][6]]]

    return render_template('hello.html', name=(name[0][0] + " " + name[0][1]),
                           message=("Here's your profile" + "\n" + str(profile)), \
                           photos=getUsersPhotos(uid), viewAlbum=getUserAlbums(uid))


@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welecome to Photoshare')


# begin album creation code**********************************************************************************************
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/createAlbum', methods=['GET'])
@flask_login.login_required
def upload():
    return render_template('upload.html', createAlbum='create new album')


@app.route('/createAlbum', methods=['GET', 'POST'])
@flask_login.login_required
def createAlbum():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        album_name = request.form.get('album_name')

        # convert date format of python to mysql
        ts = '2013-01-12'
        f = '%Y-%m-%d'
        date_of_creation = datetime.date.today()
        date_of_creation = date_of_creation.strftime(f)
        tag = request.form.get('tag')

        print(album_name, date_of_creation, int(uid))

        cursor = conn.cursor()
        cursor.execute("SELECT first_name, last_name FROM Users WHERE user_id = '{0}'".format(int(uid)))
        name = [[col.encode('utf8') if isinstance(col, unicode) else col for col in row] for row in cursor.fetchall()]

        cursor.execute("INSERT INTO Albums (name, date_of_creation, user_id) VALUES ('{0}','{1}','{2}')". \
                       format(album_name, date_of_creation, int(uid)))

        conn.commit()

        return render_template('hello.html', name=name[0][0] + " " + name[0][1], message='album created!')
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return flask.redirect(flask.url_for('createAlbum'))


# end album creation code**********************************************************************************************

# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET'])
def upload_photo():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    return render_template('upload.html', uploadPhoto="lets upload photo", viewAlbum=getUserAlbums(uid))


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        imgfile = request.files['photo']
        photo_data = base64.standard_b64encode(imgfile.read())
        caption = request.form.get('caption')
        album = request.form.get('select_album')
        tag = request.form.get('tag')
        print "user_id: ", uid, ",binary data: ", imgfile, ",caption: ", caption, ",album_select:", album, "tag: ", tag

        cursor = conn.cursor()
        cursor.execute("SELECT album_ID FROM albums WHERE name = '{0}'".format(album))

        album_id = cursor.fetchall()[0][0]
        album_id = int(album_id)

        print("start to upload photos")
        cursor.execute(
            "INSERT INTO Photos (data, caption, album_ID) VALUES ('{0}', '{1}', '{2}')".format(photo_data, caption,
                                                                                               album_id))
        conn.commit()
        print("success!")

        cursor.execute("SELECT photo_ID FROM photos WHERE data = '{0}' AND caption='{1}'".format(photo_data, caption))
        photo_id = int(cursor.fetchall()[0][0])

        if len(tag) != 0:
            tag = tag.split(",")

            for x in tag:
                tag_id = getTagId(x)

                if not tag_id:
                    cursor.execute("INSERT INTO tags (text) VALUES ('{0}')".format(x))

                tag_id = getTagId(x)[0][0]

                print(tag_id)

                cursor.execute(
                    "INSERT INTO photo_tag (photo_id, tag_id) VALUES ('{0}', '{1}')".format(photo_id, tag_id))
                conn.commit()

        return render_template('hello.html', name=uid, message='Photo uploaded!', photos=getUsersPhotos(uid))
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return flask.redirect(flask.url_for('upload'))


# end photo uploading code
def delete_tag(photo_id):
    cursor = conn.cursor()
    cursor.execute("delete from photo_tag where photo_id = '{}'".format(photo_id))
    conn.commit()


def delete_photo_in_album(album_id):
    cursor = conn.cursor()
    cursor.execute("delete from photos where album_id = '{0}'".format(album_id))
    conn.commit()


@app.route('/delete', methods=['GET', 'POST'])
@flask_login.login_required
def delete_file():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    delete_id = request.form.get('deleteObject')
    select_album = request.form.get('select_album')
    button_click = request.form.get('method')
    message = ""

    if select_album != "view_all":
        photos = None
        if button_click == "View By Album":
            print("view by album")
            photos = getAlbumsPhotos(select_album, uid)

        elif button_click == "Delete by Album":
            print("delete by album")

            album_delete_id = int(getAlbumId(select_album)[0][0])

            cursor = conn.cursor()
            cursor.execute("select photo_id from photos where album_id='{}'".format(album_delete_id))
            photoss = cursor.fetchall()

            if len(photoss) != 0:
                photo_id_list = []
                for id in photoss:
                    photo_id_list.append(int(id[0]))
                print(photo_id_list)

                for x in photo_id_list:
                    delete_tag(x)

            delete_photo_in_album(album_delete_id)
            cursor.execute("delete from albums where album_id='{}'".format(album_delete_id))
            conn.commit()
            print("every is delete successfully!")

            message = "delete successfully"

        # cursor.execute("delete from albums where album_id = '{0}'".format(album_delete_id))
        # print("i will delete album ",album_delete_id)
        # conn.commit()

        return render_template('hello.html', name=flask_login.current_user.id, message=message, photos=photos, \
                               viewAlbum=getUserAlbums(uid))

    cursor = conn.cursor()
    find_tag = int(cursor.execute("select * from photo_tag where photo_id='{0}'".format(delete_id)))
    if (find_tag != 0):
        print("this album have tags!")
        cursor.execute("delete from photo_tag where photo_id = '{0}'".format(delete_id))

    cursor.execute("delete from photos where photo_id = '{0}'".format(delete_id))

    conn.commit()

    if delete_id != None:
        message = ("remove phone " + str(int(delete_id)) + " successfully!")

    return render_template('hello.html', name=flask_login.current_user.id, message=message, photos=getUsersPhotos(uid), \
                           viewAlbum=getUserAlbums(uid))


# ***********GET FRIENDS LIST ******************************************************************************************
def getFriendList(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id2 FROM friends where user_id = '{0}'".format(user_id))
    return cursor.fetchall()


def getUserName(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, last_name FROM users where user_id = '{0}'".format(user_id))
    return [[col.encode('utf8') if isinstance(col, unicode) else col for col in row] for row in cursor.fetchall()]


@app.route('/friends', methods=['GET', 'POST'])
@flask_login.login_required
def view_friends():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    print("I go user id ", uid)
    friendList = getFriendList(int(uid))
    message = 'lets view your friends'  # send as a part of render
    # uid = 0

    friendList = [int(x[0]) for x in friendList]

    friend_name_list = [getUserName(friend) for friend in friendList]
    if len(friend_name_list) == 0:
        friend_name_list = [" "]
    else:
        friend_name_list = [friend[0][0] + " " + friend[0][1] for friend in friend_name_list]

    print(friend_name_list)

    new_friend_email = request.form.get('new email')

    if new_friend_email:

        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM Users WHERE email = '{0}'".format(new_friend_email))
        result = cursor.fetchall()

        print(len(result))

        if len(result) == 0 or int(result[0][0]) == int(uid):
            print("user not found")
            return render_template('viewInfo.html', message="user not found", viewFriends=friend_name_list)

        new_friend_id = int(result[0][0])
        print("new friend's id is ", new_friend_id)

        cursor = conn.cursor()
        cursor.execute("INSERT INTO friends (user_id, user_id2) VALUE ('{0}','{1}')".format(int(uid), new_friend_id))
        conn.commit()

        print("add successful")
        message = ("successfully add ", getUserName(new_friend_id)[0])

    return render_template('viewInfo.html', message=message, viewFriends=friend_name_list)


def find_comment(photo_id):
    cursor = conn.cursor()
    cursor.execute("select text, user_id, date from comments where photo_id = '{0}'".format(photo_id))
    return [[col.encode('utf8') if isinstance(col, unicode) else col for col in row] for row in cursor.fetchall()]


def find_total_score(uid):
    cursor = conn.cursor()
    cursor.execute("select (select count(*) as c from photos p, albums a where a.user_id = '{0}' AND p.album_id = a.album_id)\
+(select count(*) from comments c where c.user_id='{1}') as score;".format(uid, uid))
    return cursor.fetchall()


@app.route('/search_photo', methods=['GET'])
def search_photo():
    user_list = getUserIdList()
    user_list = [int(x[0]) for x in user_list]
    print(getUserIdList())
    print("the user list is ", user_list)
    score_for_all_users = []
    for x in user_list:
        name = getUserName(x)[0]
        score_for_all_users.append([x, name, int(find_total_score(x)[0][0])])
    score_for_all_users = sorted(score_for_all_users, key=lambda x: x[2], reverse=True)
    print(score_for_all_users)

    cursor.execute("select pt.tag_id, t.text, count(*) as c from photo_tag pt, tags t where pt.tag_id = t.tag_id\
	 group by tag_id order by c desc limit 10")
    popular_tag_list = cursor.fetchall()
    print(popular_tag_list)

    return render_template('viewInfo.html', message="search tag for photos", search_photo='search_photo', \
                           popular_tag_list=popular_tag_list, score_for_all_users=score_for_all_users[:10])


# select (select count(*) as c from photos p, albums a where a.user_id = 1 AND p.album_id = a.album_id)+(select count(*) from comments c where c.user_id=1) as sumCount;

@app.route('/search_photo', methods=['GET', 'POST'])
def search():
    tag_input = request.form.get('keyword')
    email_input = request.form.get('user_email')

    tag_list = tag_input.split(",")

    tag_id_list = []

    cursor = conn.cursor()

    for tag in tag_list:
        tag_id = getTagId(tag)
        if tag_id != ():
            tag_id_list.append(int(tag_id[0][0]))
        else:
            return render_template('viewInfo.html', message=str(tag) + ' are not found', search_photo=" ")
            print(tag, " doesn't exist")

    print("tag id is", tag_id_list)

    photo_id_list = []

    for tag_id in tag_id_list:
        cursor.execute("SELECT photo_id FROM photo_tag WHERE tag_id = '{0}'".format(tag_id))
        photo_ids = cursor.fetchall()
        print(photo_ids)

        if photo_ids == ():
            return render_template('viewInfo.html', message="photo not found", search_photo="search photos")

        photo_id_list.append([int(x[0]) for x in photo_ids])

    print("tuples that contain list of photo_id for all tags", photo_id_list)

    intersection = 0
    if len(photo_id_list) != 0:
        intersection = set(photo_id_list[0]).intersection(*photo_id_list)

        data_list = []

        print("photos_id that match all keywords are: ", intersection)
        if len(intersection) != 0:
            for x in intersection:
                cursor.execute("SELECT data, caption, album_id, photo_id FROM Photos WHERE photo_id = '{0}'".format(x))

                data = cursor.fetchall()[0]
                cursor.execute("SELECT name from albums where album_id = '{0}'".format(int(data[2])))
                album_name = cursor.fetchall()[0][0]

                comments = find_comment(x)
                comments = [[x[0], "--by user " + str(x[1]) + " on date " + str(x[2])] for x in comments]

                data_list.append(data)  # this will print data

                print(data_list[0][1])

            return render_template('viewInfo.html', message="photos are found!", search_photo=album_name,
                                   search_result=data_list, comments=comments)
    message = "photo not found"

    return render_template('viewInfo.html', message=message, search_photo="search photos")


@app.route('/comment', methods=['GET', 'POST'])
def comment():
    text = request.form.get('comment')
    photo_id = request.form.get('submit')

    userId = 0  # in this case, 0 represents anonymous users
    if flask_login.current_user.id != None:
        userId = int(getUserIdFromEmail(flask_login.current_user.id))

    else:
        userId = None

    ts = '2013-01-12'
    f = '%Y-%m-%d'
    date_of_creation = datetime.date.today()
    date_of_creation = date_of_creation.strftime(f)

    print("following are required information to store for comments: ", photo_id, userId, text, date_of_creation)

    cursor = conn.cursor()

    cursor.execute("insert into comments (text, user_id, date, photo_id) values ('{0}','{1}','{2}','{3}')".format( \
        text, userId, date_of_creation, photo_id
    ))
    conn.commit()

    return render_template('viewInfo.html', message="comment successfully", search_photo="search photos")


@app.route('/viewallphotos', methods=['GET', 'POST'])
def viewAllPhotos():
    cursor = conn.cursor()
    cursor.execute("select p.data, p.caption, p.photo_id from photos p")
    result = cursor.fetchall()
    info = " "

    info = request.form.get('info')
    photo_id = request.form.get('submit')
    if info == 'comment':
        info = "comments for this photo are", find_comment(photo_id)
        return render_template('viewInfo.html', message=info, view_all_photos=result)

    tag_list = []
    tag_text = []

    if info == None:
        pass

    elif info == 'tag':
        cursor.execute("select tag_id from photo_tag where photo_id = '{0}'".format(photo_id))
        res = cursor.fetchall()
        if len(res) != 0:
            tag_list = [int(x[0]) for x in res]

            for x in tag_list:
                cursor.execute("select text from tags where tag_id = '{0}'".format(x))
                res = [[col.encode('utf8') if isinstance(col, unicode) else col for col in row] for row in
                       cursor.fetchall()]
                tag_text.append(res[0][0])

            info = "tags for " + str(photo_id) + ' is ' + str(tag_text)

        return render_template('viewInfo.html', message=info, view_all_photos=result)

    elif info == 'information':
        cursor.execute(
            "select a.name, a.album_id from albums a, photos p where a.album_id = p.album_id AND p.photo_id = '{0}'".format(
                photo_id))
        res = cursor.fetchall()
        album_name = res[0][0]
        album_id = int(res[0][1])

        cursor.execute("select a.user_id from albums a where a.album_id = '{0}'".format(album_id))
        user_id = cursor.fetchall()[0][0]

        cursor.execute("select first_name, last_name from users where user_id = '{}'".format(user_id))
        user = [[col.encode('utf8') if isinstance(col, unicode) else col for col in row] for row in cursor.fetchall()]

        cursor.execute("select photo_id, count(*) from likes where photo_id='{}'".format(photo_id))
        total_likes = cursor.fetchall()

        cursor.execute(
            "select u.last_name, u.first_name from likes l, users u where l.user_id=u.user_id AND l.photo_id='{0}'".format \
                (photo_id))

        users_likes = cursor.fetchall()

        info = 'photo id ' + str(photo_id) + " is from album " + album_name + " and owner of this album is " + str(
            user[0][0] + " " + user[0][1]) + \
               " AND total number of likes for this photo is " + str(
            total_likes[0][1]) + " AND users who like this photo are " + str(users_likes)

        return render_template('viewInfo.html', message=info, view_all_photos=result)

    elif info == "likes":
        userId = int(getUserIdFromEmail(flask_login.current_user.id))
        cursor.execute("insert into likes (photo_id, user_id) values ('{0}', '{1}')".format(photo_id, userId))
        conn.commit()
        message = "succesfully likes"

    # select p.photo_id, t.text from photos p, photo_tag pt, tags t where pt.tag_id=t.tag_id and p.photo_id = pt.photo_id;
    return render_template('viewInfo.html', message="view all photos", view_all_photos=result)

@app.route('/youmaylike', methods=['GET', 'POST'])
def youmaylike():
    cursor = conn.cursor()
    cursor.execute("select data from photos ORDER BY RAND() LIMIT 5")
    photo = [cursor.fetchall()[0],"hello"]

    return render_template('viewInfo.html', message="you may like", view_all_photos=photo)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
