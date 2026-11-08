import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # SECRET_KEY は環境変数で必須設定。既知の文字列へのフォールバックは置かない
    # （セッション Cookie の署名鍵のため、既知だと任意ユーザーへのなりすましが可能になる）。
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY or SECRET_KEY == 'dev-secret-key-change-in-production':
        raise RuntimeError('SECRET_KEY environment variable must be set to a strong random value')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
