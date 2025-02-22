import flask

from data import db_session
from data.news import News

blueprint = flask.Blueprint('news_api', __name__, template_folder='templates')


@blueprint.route('/api/news')
def get_news():
    db_sess = db_session.create_session()
    news = db_sess.query(News).all()
    return flask.jsonify(
        {
            'news':
                [item.to_dict(only=('title', 'content', 'user.name'))
                 for item in news]
        }
    )


@blueprint.route('/api/news/<int:news_id>', methods=['GET'])
def get_one_news(news_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).get(news_id)
    if not news:
        return flask.jsonify({'error': 'Not found'})
    return flask.jsonify(
        {
            'news': news.to_dict(only=(
                'title', 'content', 'user_id', 'is_private'))
        }
    )

