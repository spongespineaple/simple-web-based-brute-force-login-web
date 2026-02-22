from flask import Flask, request, render_template_string
import time

app = Flask(__name__)

# =========================
# CONFIGURATION
# =========================
MAX_ATTEMPTS = 3
LOCKOUT_TIME = 60  # seconds

VALID_USERNAME = "CYB203"
VALID_PASSWORD = "FCP/CYB"

login_attempts = {}

# =========================
# LOGIN PAGE (HTML + CSS + JS)
# =========================
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Brute Force Login</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
body {
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #667eea, #764ba2);
    min-height: 100vh;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.login-box {
    background: white;
    padding: 25px;
    width: 100%;
    max-width: 350px;
    border-radius: 12px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    text-align: center;
}

h2 {
    margin-bottom: 15px;
}

input {
    width: 100%;
    padding: 12px;
    margin: 10px 0;
    border-radius: 6px;
    border: 1px solid #ccc;
    font-size: 15px;
}

.password-container {
    position: relative;
}

.toggle-password {
    position: absolute;
    right: 12px;
    top: 14px;
    cursor: pointer;
    font-size: 14px;
    color: #555;
}

button {
    width: 100%;
    padding: 12px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    cursor: pointer;
    margin-top: 10px;
}

button:hover {
    background: #5a67d8;
}

.message {
    color: red;
    font-size: 14px;
    margin-bottom: 10px;
}

.timer {
    color: #d9534f;
    font-weight: bold;
}

@media (max-width: 480px) {
    .login-box {
        padding: 20px;
    }
}
</style>

<script>
function togglePassword() {
    const pw = document.getElementById("password");
    pw.type = pw.type === "password" ? "text" : "password";
}

function startCountdown(seconds) {
    let timer = seconds;
    const el = document.getElementById("countdown");

    const interval = setInterval(() => {
        if (timer > 0) {
            el.textContent = timer;
            timer--;
        } else {
            clearInterval(interval);
            // 🔁 Reload page when timer hits 0
            window.location.href = "/";
        }
    }, 1000);
}
</script>

</head>
<body>
<div class="login-box">
    <h2>Brute Force Login</h2>

    {% if locked %}
        <p class="timer">
            Locked. Try again in
            <span id="countdown">{{ remaining }}</span> seconds
        </p>
        <script>startCountdown({{ remaining }});</script>
    {% else %}
        <div class="message">{{ message }}</div>
        <form method="POST">
            <input name="username" placeholder="Username" required>

            <div class="password-container">
                <input id="password" name="password" type="password" placeholder="Password" required>
                <span class="toggle-password" onclick="togglePassword()">👁️</span>
            </div>

            <button type="submit">Login</button>
        </form>
    {% endif %}
</div>
</body>
</html>
"""

# =========================
# SUCCESS PAGE
# =========================
SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login Success</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #f0fdf4;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    margin: 0;
}
.box {
    background: white;
    padding: 30px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
h1 {
    color: #22c55e;
}
</style>
</head>
<body>
<div class="box">
    <h1>Login Successful ✅</h1>
    <p>Welcome, CYB203.</p>
</div>
</body>
</html>
"""

# =========================
# LOGIN LOGIC
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    ip = request.remote_addr
    now = time.time()

    if ip not in login_attempts:
        login_attempts[ip] = {"count": 0, "lockout_until": 0}

    record = login_attempts[ip]

    if now < record["lockout_until"]:
        remaining = int(record["lockout_until"] - now)
        return render_template_string(
            HTML,
            locked=True,
            remaining=remaining
        )

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == VALID_USERNAME and password == VALID_PASSWORD:
            record["count"] = 0
            return SUCCESS_HTML

        record["count"] += 1

        if record["count"] >= MAX_ATTEMPTS:
            record["lockout_until"] = now + LOCKOUT_TIME
            return render_template_string(
                HTML,
                locked=True,
                remaining=LOCKOUT_TIME
            )

        return render_template_string(
            HTML,
            locked=False,
            message=f"Invalid credentials. Attempts left: {MAX_ATTEMPTS - record['count']}"
        )

    return render_template_string(HTML, locked=False, message="")

# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)