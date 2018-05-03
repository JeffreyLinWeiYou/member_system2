from flask import Flask, url_for, render_template, request, redirect, session
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy import create_engine
from flask_restful import reqparse


DB_URI = "mysql+pymysql://root:@127.0.0.1:3306/member"
Session = sessionmaker(autocommit=False,
                       autoflush=False,
                       bind=create_engine(DB_URI))
session_db = scoped_session(Session)
app = Flask(__name__)

engine = create_engine(DB_URI, max_overflow=5)

Base = declarative_base()

parser = reqparse.RequestParser()
parser.add_argument('id', type=int)
parser.add_argument('username', type=str)
parser.add_argument('password', type=str)
parser.add_argument('telephone', type=str)
parser.add_argument('extra', type=str)

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(32))
    password = Column(String(32))
    telephone = Column(String(32))
    extra = Column(Text)

    def __init__(self, username, password):
        # self.id = id
        self.username = username
        self.password = password
        # self.telephone = telephone
        # self.extra = extra

def init_db():
    Base.metadata.create_all(engine)

def drop_db():
    Base.metadata.drop_all(engine)

@app.route('/', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return  render_template('index.html')
    else:
        if request.method == 'POST':
            parser = reqparse.RequestParser()
            parsed_args = parser.parse_args()
            email = parsed_args['email']
            return 'aaa'
        return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name = request.form['username']
        passw = request.form['password']
        # try:
        data = session_db.query.filter(Users.username == name, Users.password == passw).first()
        if data is not None:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return 'Dont Login'
        # except:
        #     return "Dont Login"

@app.route('/register/',methods=['GET', 'POST'])
def register():
    """Register Form"""
    if request.method == 'POST':
        new_user = Users(username=request.form['username'], password=request.form['password'])
        session_db.add(new_user)
        session_db.commit()
        return render_template('login.html')
    return render_template('register.html')


if __name__ == '__main__':

    init_db()
    app.run(port=8008)