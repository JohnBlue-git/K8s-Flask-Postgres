from flask import Flask
import psycopg2

app = Flask(__name__)

@app.route('/')
def hello():
    try:
        conn = psycopg2.connect(
            host='postgres-service',
            dbname='postgres',
            user='postgres',
            password='example'
        )
        return "✅ Connected to PostgreSQL!"
    except Exception as e:
        return f"❌ Failed to connect to DB: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
