print("Starting Flask App...")

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("Running Server...")
    app.run(debug=True)