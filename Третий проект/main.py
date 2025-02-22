from flask import Flask, render_template, redirect, abort, request, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session, news_api
from data.news import News
from data.users import User
from forms.news import NewsForm
from forms.user import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(news_api.blueprint)
    app.run()


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/", methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    tags = db_sess.query(User).all()
    tags = [user.position for user in tags]
    if request.method == 'POST':
        filter_tag = request.form.get('select')
        if filter_tag != 'Все записи':
            users_with_tag = db_sess.query(User).filter(User.position == filter_tag)
            users_with_tag = [user.id for user in users_with_tag]
            if current_user.is_authenticated:
                news = db_sess.query(News).filter(
                    ((News.user == current_user) | (News.is_private != True)) &
                    News.user_id.in_(users_with_tag)
                )
            else:
                news = db_sess.query(News).filter((News.is_private != True) &
                                                  (News.user_id.in_(users_with_tag)))
        else:
            if current_user.is_authenticated:
                news = db_sess.query(News).filter(
                    (News.user == current_user) | (News.is_private != True))
            else:
                news = db_sess.query(News).filter(News.is_private != True)
        return render_template("index.html", news=news, tags=tags, title='Записи')
    elif request.method == 'GET':
        if current_user.is_authenticated:
            news = db_sess.query(News).filter(
                (News.user == current_user) | (News.is_private != True))
        else:
            news = db_sess.query(News).filter(News.is_private != True)
        return render_template("index.html", news=news, tags=tags, title='Записи')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли должны совпадать!")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            position=form.position.data,
            email=form.email.data,
            speciality=form.speciality.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неверный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости', form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html', title='Редактирование новости', form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/user/<int:id>', methods=['GET', 'POST'])
def show_user(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(id)
    if request.method == 'POST':
        f = request.files['file']
        print(f.filename)
    return render_template('user.html', title='Профиль', user=user)


@app.route('/user/<int:id>/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    form = RegisterForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(id)
        if user:
            form.email.data = user.email
            form.surname.data = user.surname
            form.age.data = user.age
            form.name.data = user.name
            form.about.data = user.about
            form.position.data = user.position
            form.speciality.data = user.speciality
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(id)
        if user:
            user.email = form.email.data
            user.surname = form.surname.data
            user.name = form.name.data
            user.about = form.about.data
            user.position = form.position.data
            user.speciality = form.speciality.data
            user.set_password(form.password.data)
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('register.html', title='Редактирование профиля', form=form)


@app.route('/user/<int:id>/upload_photo', methods=['GET', 'POST'])
@login_required
def upload_photo(id):
    if request.method == "GET":
        return render_template('upload photo.html', title='Загрузите файл')
    elif request.method == "POST":
        f = request.files['file']
        content = f.read()
        with open('static/img/tmp.png', 'wb') as image:
            image.write(content)
            image.close()
        return render_template('upload photo.html', title='Загрузите файл', photo='tmp.png')


@app.route('/user/<int:id>/save_photo')
@login_required
def save_photo(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(id)
    content = open(f'static/img/tmp.png', 'rb').read()
    with open(f'static/img/photo{id}.png', 'wb') as image:
        image.write(content)
    user.photo = f'photo{id}.png'
    db_sess.commit()
    return redirect(f'/user/{id}')


if __name__ == '__main__':
    main()
