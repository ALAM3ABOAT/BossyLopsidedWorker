import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class App(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    version = db.Column(db.String(20))
    size = db.Column(db.String(20))
    downloads = db.Column(db.String(20), default='0')
    category = db.Column(db.String(50), default='الكل')
    icon = db.Column(db.String(10), default='📱')
    download_link = db.Column(db.String(500))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    apps = App.query.all()
    categories = ['الكل', 'ألعاب', 'أدوات', 'تواصل', 'وسائط']
    return render_template('index.html', apps=apps, categories=categories)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    apps = App.query.filter(App.name.ilike(f'%{query}%')).all()
    return render_template('index.html', apps=apps, categories=['الكل', 'ألعاب', 'أدوات', 'تواصل', 'وسائط'], search_query=query)

@app.route('/category/<cat>')
def category(cat):
    if cat == 'الكل':
        apps = App.query.all()
    else:
        apps = App.query.filter_by(category=cat).all()
    return render_template('index.html', apps=apps, categories=['الكل', 'ألعاب', 'أدوات', 'تواصل', 'وسائط'], active_cat=cat)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['logged_in'] = True
            return redirect(url_for('admin_panel'))
        flash('اسم المستخدم أو كلمة المرور غير صحيحة')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_panel():
    apps = App.query.all()
    return render_template('admin.html', apps=apps)

@app.route('/admin/add', methods=['POST'])
@login_required
def add_app():
    new_app = App(
        name=request.form['name'],
        description=request.form['description'],
        version=request.form['version'],
        size=request.form['size'],
        downloads=request.form.get('downloads', '0'),
        category=request.form['category'],
        icon=request.form.get('icon', '📱'),
        download_link=request.form['download_link']
    )
    db.session.add(new_app)
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete/<int:id>')
@login_required
def delete_app(id):
    app_to_delete = App.query.get_or_404(id)
    db.session.delete(app_to_delete)
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit/<int:id>', methods=['POST'])
@login_required
def edit_app(id):
    app_to_edit = App.query.get_or_404(id)
    app_to_edit.name = request.form['name']
    app_to_edit.description = request.form['description']
    app_to_edit.version = request.form['version']
    app_to_edit.size = request.form['size']
    app_to_edit.downloads = request.form.get('downloads', '0')
    app_to_edit.category = request.form['category']
    app_to_edit.icon = request.form.get('icon', '📱')
    app_to_edit.download_link = request.form['download_link']
    db.session.commit()
    return redirect(url_for('admin_panel'))

def init_db():
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(username='meessee').first():
            admin = Admin(
                username='meessee',
                password=generate_password_hash('12345@12345')
            )
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
