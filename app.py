from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Todo
from forms import LoginForm, RegistrationForm, TodoForm
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_guest_user():
    with app.app_context():
        guest_user = User.query.filter_by(username='guest').first()
        if not guest_user:
            guest_user = User(username='guest', password='')
            db.session.add(guest_user)
            db.session.commit()

# アプリケーションの起動時に一度だけ実行
create_guest_user()

@app.route('/')
def index():
    todos = Todo.query.all()
    for todo in todos:
        print(f"ID: {todo.id}, Title: {todo.title}, Description: {todo.description}")
    return render_template('todo_list.html', todos=todos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('ユーザー名またはパスワードが間違っています。')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('アカウントが作成されました。ログインしてください。')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/add_todo', methods=['GET', 'POST'])
def add_todo():
    form = TodoForm()
    if form.validate_on_submit():
        user_id = current_user.id if current_user.is_authenticated else User.query.filter_by(username='guest').first().id
        new_todo = Todo(title=form.title.data, description=form.description.data, user_id=user_id)
        db.session.add(new_todo)
        db.session.commit()
        flash('ToDoが追加されました。')
        return redirect(url_for('index'))
    return render_template('todo_edit.html', form=form, title='新規ToDo追加')

@app.route('/edit_todo/<int:id>', methods=['GET', 'POST'])
def edit_todo(id):
    todo = Todo.query.get_or_404(id)
    form = TodoForm(obj=todo)
    if form.validate_on_submit():
        todo.title = form.title.data
        todo.description = form.description.data
        db.session.commit()
        flash('ToDoが更新されました。')
        return redirect(url_for('index'))
    return render_template('todo_edit.html', form=form, title='ToDo編集')

@app.route('/delete_todo/<int:id>')
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    flash('ToDoが削除されました。')
    return redirect(url_for('index'))

@app.route('/admin')
def admin_panel():
    users = User.query.all()
    return render_template('admin_panel.html', users=users)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)