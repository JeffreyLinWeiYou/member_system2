from flask import Flask, url_for, render_template, request, redirect, session
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

DB_URI = "mysql+pymysql://root:@127.0.0.1:3306/member"
Session = sessionmaker(autocommit=False,
                       autoflush=False,
                       bind=create_engine(DB_URI))
session_db = scoped_session(Session)
app = Flask(__name__)

engine = create_engine(DB_URI, max_overflow=5)

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(32))
    password = Column(String(32))
    email = Column(String(32))
    telephone = Column(String(32))
    extra = Column(Text)

    def __init__(self, id, username, password, email, telephone, extra):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.telephone = telephone
        self.extra = extra


class Administrator(Base):
    __tablename__ = 'administrator'
    id = Column(Integer, primary_key=True)
    username = Column(String(32))
    password = Column(String(32))
    email = Column(String(32))
    telephone = Column(String(32))
    extra = Column(Text)

    def __init__(self, id, username, password, email, telephone, extra):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.telephone = telephone
        self.extra = extra


def init_db():
    Base.metadata.create_all(engine)


def drop_db():
    Base.metadata.drop_all(engine)


@app.route('/', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        if session['identity'] == 'member':
            if request.method == 'POST':
                user = session_db.query(Users).filter(Users.username == session['username']).first()
        else:
            if request.method == 'POST':
                user = session_db.query(Administrator).filter(Administrator.username == session['username']).first()

        if request.method == 'POST':
            user.password = request.form['password']
            session['password'] = request.form['password']
            user.email = request.form['email']
            user.telephone = request.form['telephone']
            user.extra = request.form['extra']
            session_db.commit()

        if session['identity'] == 'member':
            data_username = session_db.query(Users).filter(Users.username == session['username']).first()
        else:
            data_username = session_db.query(Administrator).filter(
                Administrator.username == session['username']).first()

        return render_template('index.html', username=data_username.username, password=data_username.password,
                               email=data_username.email, telephone=data_username.telephone,
                               extra=data_username.extra, identity=session['identity'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name = request.form['username']
        passw = request.form['password']
        identity = request.form['identity']
        if identity == 'member':

            data_username = session_db.query(Users).filter(Users.username == name).first()
            if data_username is not None:
                data_username_passw = session_db.query(Users).filter(Users.username == name,
                                                                     Users.password == passw).first()
                if data_username_passw is not None:
                    session['logged_in'] = True
                    session['username'] = name
                    session['password'] = passw
                    session['identity'] = 'member'

                    data_username = session_db.query(Users).filter(Users.username == session['username']).first()
                    return render_template('index.html', username=session['username'],
                                           password=data_username.password,
                                           email=data_username.email, telephone=data_username.telephone,
                                           extra=data_username.extra, identity=session['identity'])
                else:
                    return 'Username Exist,but password error'

            else:
                return 'Username Error'
        else:
            data_username = session_db.query(Administrator).filter(Administrator.username == name).first()
            if data_username is not None:
                data_username_passw = session_db.query(Administrator).filter(Administrator.username == name,
                                                                             Administrator.password == passw).first()
                if data_username_passw is not None:
                    session['logged_in'] = True
                    session['username'] = name
                    session['password'] = passw
                    session['identity'] = 'administrator'

                    data_username = session_db.query(Administrator).filter(
                        Administrator.username == session['username']).first()
                    return render_template('index.html', username=session['username'],
                                           password=data_username.password,
                                           email=data_username.email, telephone=data_username.telephone,
                                           extra=data_username.extra, identity=session['identity'])
                else:
                    return 'Username Exist,but password error'

            else:
                return 'Username Error'


@app.route('/register/', methods=['GET', 'POST'])
def register():
    """Register Form"""
    if request.method == 'POST':
        identity = request.form['identity']
        session['identity'] = identity
        if identity == 'member':
            rows = session_db.query(func.count(Users.id)).scalar()

        else:
            rows = session_db.query(func.count(Administrator.id)).scalar()
        new_user = Users(id=rows + 1, username=request.form['username'], password=request.form['password'],
                         email=request.form['email'], telephone=request.form['telephone'],
                         extra=request.form['extra'])
        session_db.add(new_user)
        session_db.commit()
        return render_template('login.html')
    return render_template('register.html')


@app.route('/logout')
def logout():
    session['logged_in'] = False
    session['username'] = 'Null'
    session['password'] = 'Null'
    session['identity'] = 'Null'

    return redirect(url_for('home'))


@app.route('/modify', methods=['GET', 'POST'])
def modify():
    if request.method == 'GET':
        user = session_db.query(Users).all()
        return render_template('modify.html', users=user)
    if request.method == 'POST':
        user = session_db.query(Users).all()
        for i in range(len(user)):
            user[i].email = request.form['email' + str(i + 1)]
            user[i].telephone = request.form['telephone' + str(i + 1)]
            user[i].extra = request.form['extra' + str(i + 1)]
        session_db.commit()
        return redirect(url_for('modify'))


if __name__ == '__main__':
    init_db()
    app.secret_key = "MemberSystem"
    app.run(port=8008)
