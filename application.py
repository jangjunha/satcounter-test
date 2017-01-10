from flask import Flask, render_template, request, redirect, url_for, session, abort
from datetime import datetime
from flask import g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'development-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///satcounter2.db'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    messages = db.relationship('Message',
                               backref=db.backref('writer',
                                                  lazy='joined'),
                               lazy='dynamic')


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)

    writer_user_id = db.Column(db.Integer,
                               db.ForeignKey('user.id'))

    def __init__(self, writer_user_id, content):
        self.writer_user_id = writer_user_id
        self.content = content

    def __repr__(self):
        return '<Message %r>' % self.id


def get_countdown():
    return datetime(2017, 11, 16) - datetime.now()


@app.before_request
def before_request():
    g.countdown = get_countdown()
    if 'user_id' in session:
        g.user = User.query.filter_by(id=session['user_id']).one()
    else:
        g.user = None


@app.teardown_request
def teardown_request(exception):
    print(">> TEARDOWN REQUEST")


@app.route('/')
def index():
    #DB에서 가져오기
    # db = get_db()
    # comments = db.execute("SELECT * FROM comments LIMIT 10").fetchall()
    comments = Message.query.limit(10).all()
    return render_template('index.html',
                           comments=comments)


@app.route('/users/<int:user_id>')
def user_profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return abort(404)

    return render_template('profile.html', user=user)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/new_comment')
def new_comment():
    return render_template('write.html')


@app.route('/new_comment', methods=['POST'])
def post_comment():
    if not g.user:
        return abort(401)

    msg = Message(g.user.id, request.form['content'])
    db.session.add(msg)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/signup')
def signup_form():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup():
    user = User()
    user.username = request.form['username']
    user.password = generate_password_hash(request.form['password'])
    db.session.add(user)
    db.session.commit()

    return redirect(url_for('index'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user is None:
            error = '아이디 또는 비밀번호가 잘못되었습니다.'
        elif not check_password_hash(user.password, password):
            error = '아이디 또는 비밀번호가 잘못되었습니다.'
        else:
            session['user_id'] = user.id
            return redirect(url_for('index'))

    return render_template('login.html', error=error)


@app.route("/comments/<int:pages>")
def get_comments(pages):
    # db = get_db()
    # comments = db.execute (
    #     "SELECT * FROM comments LIMIT 5 OFFSET ?",
    #     ((pages - 1) * 5,)
    # ).fetchall()
    comments = Message.query.offset((pages - 1) * 5).limit(5).all()
    return str(comments)


if __name__ == '__main__':
    app.run(debug=True)








# .
