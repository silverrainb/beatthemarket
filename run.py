from beatthemarket.app import create_app
app = create_app()

if __name__ == "__main__":
    app.run()

# export FLASK_APP=run
# flask run
# flask run --host=0.0.0.0 --port=8000
# beatthemarket db init/reset/seed
# gunicorn -b 0.0.0.0:8000 --access-logfile - --reload "beatthemarket.app:create_app()" beatthemarket db --help
