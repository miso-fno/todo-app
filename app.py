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

@app.route('/')
@login_required
def index():
    todos = Todo.query.filter_by(user_id=current_user.id).all()
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
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

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
@login_required
def add_todo():
    form = TodoForm()
    if form.validate_on_submit():
        new_todo = Todo(title=form.title.data, description=form.description.data, user_id=current_user.id)
        db.session.add(new_todo)
        db.session.commit()
        flash('ToDoが追加されました。')
        return redirect(url_for('index'))
    return render_template('todo_edit.html', form=form, title='新規ToDo追加')

@app.route('/edit_todo/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_todo(id):
    todo = Todo.query.get_or_404(id)
    if todo.user_id != current_user.id:
        flash('このToDoを編集する権限がありません。')
        return redirect(url_for('index'))
    form = TodoForm(obj=todo)
    if form.validate_on_submit():
        todo.title = form.title.data
        todo.description = form.description.data
        db.session.commit()
        flash('ToDoが更新されました。')
        return redirect(url_for('index'))
    return render_template('todo_edit.html', form=form, title='ToDo編集')

@app.route('/delete_todo/<int:id>')
@login_required
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    if todo.user_id != current_user.id:
        flash('このToDoを削除する権限がありません。')
        return redirect(url_for('index'))
    db.session.delete(todo)
    db.session.commit()
    flash('ToDoが削除されました。')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('管理者ページにアクセスする権限がありません。')
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin_panel.html', users=users)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)