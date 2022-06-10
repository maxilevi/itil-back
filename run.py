from flask import Flask
from app.routes import routes_bp
from app.models import db
import os
from dotenv import load_dotenv
from flask_swagger_ui import get_swaggerui_blueprint

load_dotenv()

def create_app():

	app = Flask(__name__)
	app.config['DEBUG'] = True
	app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
		# f'postgresql://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_DATABASE")}'

	db.init_app(app)
	app.register_blueprint(routes_bp, url_prefix='/')

	@app.after_request
	def after_request(response):
	    header = response.headers
	    header['Access-Control-Allow-Origin'] = '*'
	    header["Access-Control-Allow-Headers" ] = "Origin, X-Requested-With, Content-Type, Accept"
	    header["Access-Control-Allow-Methods" ] = "GET,PUT,POST,PATCH,DELETE"
	    return response

	return app

app = create_app()

if __name__ == '__main__':
	with app.app_context():
		db.create_all()

	app.run()