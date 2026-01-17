from flask import Flask, render_template, request
import spotify_roast

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")

@app.route("/roasted", methods=["GET", "POST"])
def get_roast():
    if request.method == "POST":
        username = request.form.get("username")
        user_playlists = spotify_roast.get_spotify_account(username)
        roast_response = spotify_roast.gemini_roast(user_playlists)
        return render_template("show_roast.html", response=roast_response)

    return render_template("error.html")


if __name__ == "__main__":
    app.run(debug=True)