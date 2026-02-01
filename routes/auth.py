from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        name = request.form.get('name', '').strip()

        if not email or not password or not name:
            flash('すべての必須項目を入力してください', 'error')
            return render_template('auth/register.html')

        if password != password_confirm:
            flash('パスワードが一致しません', 'error')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('パスワードは6文字以上で入力してください', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('このメールアドレスは既に登録されています', 'error')
            return render_template('auth/register.html')

        user = User(email=email, name=name)
        user.set_password(password)

        # オプション項目
        if request.form.get('height'):
            user.height = float(request.form.get('height'))
        if request.form.get('current_weight'):
            user.current_weight = float(request.form.get('current_weight'))
        if request.form.get('target_weight'):
            user.target_weight = float(request.form.get('target_weight'))
        if request.form.get('age'):
            user.age = int(request.form.get('age'))
        if request.form.get('gender'):
            user.gender = request.form.get('gender')
        if request.form.get('activity_level'):
            user.activity_level = float(request.form.get('activity_level'))

        db.session.add(user)
        db.session.commit()

        flash('登録が完了しました。ログインしてください', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash('メールアドレスまたはパスワードが正しくありません', 'error')
            return render_template('auth/login.html')

        login_user(user, remember=request.form.get('remember'))
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', '').strip()

        if request.form.get('height'):
            current_user.height = float(request.form.get('height'))
        if request.form.get('current_weight'):
            current_user.current_weight = float(request.form.get('current_weight'))
        if request.form.get('target_weight'):
            current_user.target_weight = float(request.form.get('target_weight'))
        if request.form.get('age'):
            current_user.age = int(request.form.get('age'))
        if request.form.get('gender'):
            current_user.gender = request.form.get('gender')
        if request.form.get('activity_level'):
            current_user.activity_level = float(request.form.get('activity_level'))

        db.session.commit()
        flash('プロフィールを更新しました', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')
