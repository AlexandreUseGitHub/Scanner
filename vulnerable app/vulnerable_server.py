from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route("/")
def home():
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Application vulnérable à DOM XSS</title>
    </head>
    <body>
        <h1>Bienvenue sur la page vulnérable à DOM XSS</h1>
        <p>Ajoutez ?msg=VotreMessage à l'URL pour voir le message affiché.</p>
        <div id="output"></div>
        <script>
            // Vulnérable à DOM XSS : insertion directe depuis l'URL
            var params = new URLSearchParams(window.location.search);
            document.getElementById("output").innerHTML = params.get("msg");
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

if __name__ == "__main__":
    app.run(debug=True)
