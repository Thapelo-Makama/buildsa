from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_cors import CORS
from config import Config
import os
from app.ai_assistant import AIAssistant

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
migrate = Migrate()
socketio = SocketIO()
ai_assistant = AIAssistant()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")

    with app.app_context():
        ai_assistant.initialize()

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.feed import feed_bp
    from app.routes.materials import materials_bp
    from app.routes.messages import messages_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(feed_bp, url_prefix='/feed')
    app.register_blueprint(materials_bp, url_prefix='/materials')
    app.register_blueprint(messages_bp, url_prefix='/messages')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/ai/chat', methods=['POST'])
    def ai_chat():
        data = request.get_json() or {}
        msg = data.get('message', '').strip()
        page = data.get('page_url', '/')
        if not msg:
            return jsonify({'error': 'No message provided'}), 400
        response = ai_assistant.generate_response(msg, page_url=page)
        return jsonify({
            'response': response,
            'suggestions': ai_assistant.get_suggestion_buttons(page)
        })

    @app.route('/ai/suggestions')
    def ai_suggestions():
        return jsonify({
            'suggestions': ai_assistant.get_suggestion_buttons(request.args.get('page', '/'))
        })

    @app.context_processor
    def inject():
        return {'current_page': request.path}

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
