from flask import Flask, render_template, request

app = Flask(__name__)

# Temporary storage (in a real app, use a database!)
url_db = {}

@app.route("/", methods=["GET", "POST"])
def index():
    short_url = None
    if request.method == "POST":
        long_url = request.form.get("url")
        # Simple logic to create a "short" key
        short_key = str(len(url_db) + 1)
        url_db[short_key] = long_url
        short_url = f"http://localhost:5000/{short_key}"
        
    return render_template("index.html", short_url=short_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)