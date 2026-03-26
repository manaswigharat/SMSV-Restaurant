from flask import Flask, request, redirect, render_template_string, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "smart_secret"

# ---------------- DATABASE ----------------

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # your MySQL username
        password="root",      # your MySQL password
        database="smartaid"
    )
def init_db():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        password VARCHAR(100),
        role VARCHAR(20)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS donations(
        id INT AUTO_INCREMENT PRIMARY KEY,
        donor VARCHAR(100),
        item VARCHAR(100),
        quantity INT,
        status VARCHAR(20)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests(
        id INT AUTO_INCREMENT PRIMARY KEY,
        ngo VARCHAR(100),
        item VARCHAR(100),
        quantity INT,
        status VARCHAR(20)
    )
    """)

    conn.commit()
    conn.close()

# ---------------- SMART AI MATCH ----------------

def smart_match():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM donations WHERE status='available'")
    donations = cur.fetchall()

    cur.execute("SELECT * FROM requests WHERE status='pending'")
    requests = cur.fetchall()

    keywords = {
        "food": ["food", "rice", "meal"],
        "clothes": ["clothes", "shirt"],
        "books": ["books", "study"],
        "money": ["money", "cash"]
    }

    def get_category(item):
        item = item.lower()
        for k, words in keywords.items():
            for w in words:
                if w in item:
                    return k
        return item

    for r in requests:
        best = None
        best_score = 0

        for d in donations:
            score = 0

            if get_category(d["item"]) == get_category(r["item"]):
                score += 50

            if d["quantity"] >= r["quantity"]:
                score += 30

            if r["quantity"] <= 5:
                score += 20

            if score > best_score:
                best_score = score
                best = d

        if best:
            cur.execute("UPDATE donations SET status='assigned' WHERE id=?", (best["id"],))
            cur.execute("UPDATE requests SET status='fulfilled' WHERE id=?", (r["id"],))

    conn.commit()
    conn.close()

# ---------------- UI ----------------

def layout(content):
    return render_template_string(f"""
<!DOCTYPE html>
<html>
<head>
<title>SmartAid</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

body {{
    margin: 0;
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(135deg, #1f4037, #99f2c8);
    min-height: 100vh;
    color: white;
}}

#particles-js {{
    position: fixed;
    width: 100%;
    height: 100%;
    z-index: -1;
}}

.card {{
    background: rgba(255,255,255,0.15);
    border-radius: 20px;
    padding: 25px;
    backdrop-filter: blur(15px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    transition: 0.3s;
}}

.card:hover {{
    transform: translateY(-5px);
}}

.hero {{
    text-align:center;
    padding:100px 20px;
}}

.hero h1 {{
    font-size:50px;
}}

.btn {{
    border-radius:30px;
}}
.hero h1 {{
    font-size: 60px;
    font-weight: 600;
    background: linear-gradient(90deg, #fff, #00ffcc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.card h4 {{
    margin-bottom: 10px;
    font-weight: 600;
}}

.card p {{
    font-size: 14px;
}}
</style>
</head>

<body>

<div id="particles-js"></div>

<div class="container mt-4">
<h2>Smart Donation Platform</h2>

{"<a href='/dashboard' class='btn btn-light'>Dashboard</a> <a href='/logout' class='btn btn-danger'>Logout</a>" if session.get("user") else "<a href='/login' class='btn btn-light'>Login</a> <a href='/register' class='btn btn-warning'>Register</a>"}

<hr>
{content}
</div>

<script src="https://cdn.jsdelivr.net/npm/particles.js"></script>

<script>
particlesJS("particles-js", {{
  "particles": {{
    "number": {{ "value": 60 }},
    "color": {{ "value": "#ffffff" }},
    "shape": {{ "type": "circle" }},
    "opacity": {{ "value": 0.5 }},
    "size": {{ "value": 3 }},
    "line_linked": {{
      "enable": true,
      "distance": 150,
      "color": "#ffffff",
      "opacity": 0.4
    }},
    "move": {{
      "enable": true,
      "speed": 3
    }}
  }},
  "interactivity": {{
    "events": {{
      "onhover": {{ "enable": true, "mode": "repulse" }}
    }}
  }}
}});
</script>

</body>
</html>
""")

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return layout("""
    
    <!-- HERO SECTION -->
    <div class='hero text-center'>
        <h1>SmartAid</h1>
        <h3 class='mt-3'>Give Smart. Help Fast.</h3>
        <p class='mt-3'>An AI-powered platform connecting donors with NGOs efficiently</p>

        <div class="mt-4">
            <a href="/login" class="btn btn-light btn-lg mx-2">Login</a>
            <a href="/register" class="btn btn-warning btn-lg mx-2">Register</a>
        </div>
    </div>

    <!-- FEATURES -->
    <div class="row mt-5 text-center">

        <div class="col-md-4">
            <div class="card">
                <h4>🤖 Smart Matching</h4>
                <p>AI automatically connects donations with the most relevant requests.</p>
            </div>
        </div>

        <div class="col-md-4">
            <div class="card">
                <h4>⚡ Fast Help</h4>
                <p>Reduce waiting time and deliver help instantly to those in need.</p>
            </div>
        </div>

        <div class="col-md-4">
            <div class="card">
                <h4>🌍 Community Impact</h4>
                <p>Build a stronger community by sharing resources efficiently.</p>
            </div>
        </div>

    </div>

    <!-- ABOUT SECTION -->
    <div class="card mt-5">
        <h3>About SmartAid</h3>
        <p>
        SmartAid is an intelligent donation platform designed to bridge the gap between donors and NGOs.
        Using smart algorithms, it ensures that resources like food, clothes, books, and funds reach the right people at the right time.
        </p>

        <p>
        Whether you're donating or requesting help, SmartAid makes the process simple, fast, and effective.
        </p>
    </div>

    <!-- CALL TO ACTION -->
    <div class="text-center mt-5 mb-5">
        <h4>Start Making a Difference Today</h4>
        <a href="/register" class="btn btn-success btn-lg mt-3">Get Started</a>
    </div>

    """)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        try:
            conn = connect_db()
            conn.execute("INSERT INTO users VALUES(NULL,?,?,?,?)",
                         (request.form["name"], request.form["email"],
                          request.form["password"], request.form["role"]))
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            return layout("<h3 style='text-align:center;'>User already exists</h3>")

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Register</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

<style>
body {
    margin:0;
    height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(-45deg, #667eea, #764ba2, #6a11cb, #2575fc);
    background-size: 400% 400%;
    animation: gradientBG 10s ease infinite;
}

@keyframes gradientBG {
    0% {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100% {background-position:0% 50%;}
}

.card {
    width: 350px;
    padding: 30px;
    border-radius: 20px;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(15px);
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0% { transform: translateY(0px);}
    50% { transform: translateY(-10px);}
    100% { transform: translateY(0px);}
}

input, select {
    border-radius: 12px !important;
    padding: 10px !important;
}

.btn {
    border-radius: 25px;
}

h3 {
    text-align:center;
    margin-bottom:20px;
    color:white;
}
</style>
</head>

<body>

<div class="card text-white">
<h3>Create Account</h3>

<form method="post">
<input class="form-control my-2" name="name" placeholder="Full Name" required>
<input class="form-control my-2" name="email" placeholder="Email" required>
<input class="form-control my-2" name="password" type="password" placeholder="Password" required>

<select class="form-control my-2" name="role">
<option value="donor">Donor</option>
<option value="ngo">NGO</option>
</select>

<button class="btn btn-success w-100 mt-2">Register</button>
</form>

<p class="text-center mt-3">
Already have account? <a href="/login" class="text-warning">Login</a>
</p>

</div>

</body>
</html>
""")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        conn = connect_db()
        user = conn.execute("SELECT * FROM users WHERE email=? AND password=?",
                            (request.form["email"], request.form["password"])).fetchone()
        conn.close()

        if user:
            session["user"] = user["name"]
            session["role"] = user["role"]
            return redirect("/dashboard")

        return render_template_string("<h3 style='text-align:center;'>Invalid Login</h3>")

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Login</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

<style>
body {
    margin:0;
    height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(-45deg, #ff512f, #dd2476, #ff9966, #ff5e62);
    background-size: 400% 400%;
    animation: gradientBG 10s ease infinite;
}

@keyframes gradientBG {
    0% {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100% {background-position:0% 50%;}
}

.card {
    width: 350px;
    padding: 30px;
    border-radius: 20px;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(15px);
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0% { transform: translateY(0px);}
    50% { transform: translateY(-10px);}
    100% { transform: translateY(0px);}
}

input {
    border-radius: 12px !important;
    padding: 10px !important;
}

.btn {
    border-radius: 25px;
}

h3 {
    text-align:center;
    margin-bottom:20px;
    color:white;
}
</style>
</head>

<body>

<div class="card text-white">
<h3>Welcome Back</h3>

<form method="post">
<input class="form-control my-2" name="email" placeholder="Email" required>
<input class="form-control my-2" name="password" type="password" placeholder="Password" required>

<button class="btn btn-primary w-100 mt-2">Login</button>
</form>

<p class="text-center mt-3">
New user? <a href="/register" class="text-warning">Register</a>
</p>

</div>

</body>
</html>
""")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = connect_db()
    donations = conn.execute("SELECT * FROM donations").fetchall()
    requests = conn.execute("SELECT * FROM requests").fetchall()
    conn.close()

    data = "<h3>Dashboard</h3>"

    if session["role"] == "donor":
        data += "<a href='/donate' class='btn btn-success'>Donate</a><br><br>"
    else:
        data += "<a href='/request_help' class='btn btn-warning'>Request Help</a><br><br>"

    data += "<h4>Donations</h4>"
    for d in donations:
        data += f"<p>{d['donor']} → {d['item']} ({d['status']})</p>"

    data += "<h4>Requests</h4>"
    for r in requests:
        data += f"<p>{r['ngo']} → {r['item']} ({r['status']})</p>"

    return layout(data)

@app.route("/donate", methods=["GET","POST"])
def donate():
    if request.method == "POST":
        conn = connect_db()
        conn.execute("INSERT INTO donations VALUES(NULL,?,?,?,?)",
                     (session["user"], request.form["item"],
                      int(request.form["quantity"]), "available"))
        conn.commit()
        conn.close()

        smart_match()
        return redirect("/dashboard")

    return layout("""
    <div class='card'>
    <h3>Donate</h3>
    <form method='post'>
    <input class='form-control my-2' name='item'>
    <input class='form-control my-2' name='quantity'>
    <button class='btn btn-success'>Submit</button>
    </form>
    </div>
    """)

@app.route("/request_help", methods=["GET","POST"])
def request_help():
    if request.method == "POST":
        conn = connect_db()
        conn.execute("INSERT INTO requests VALUES(NULL,?,?,?,?)",
                     (session["user"], request.form["item"],
                      int(request.form["quantity"]), "pending"))
        conn.commit()
        conn.close()

        smart_match()
        return redirect("/dashboard")

    return layout("""
    <div class='card'>
    <h3>Request Help</h3>
    <form method='post'>
    <input class='form-control my-2' name='item'>
    <input class='form-control my-2' name='quantity'>
    <button class='btn btn-warning'>Submit</button>
    </form>
    </div>
    """)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)