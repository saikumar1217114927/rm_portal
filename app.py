from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import threading

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Load RM & Investor mapping
df = pd.read_excel("rm_investors.xlsx")

# Create login dictionary
users = {
    row['Username']: {
        'password': row['Password'],
        'RM_Name': row['RM_Name']
    }
    for idx, row in df.iterrows()
}

# Available reports
reports = [
    "Portfolio Factsheet",
    "Portfolio Apprisal",
    "Performance Apprisal",
    "Statement of Capital Gain/Loss",
    "Transaction Report",
    "Dividend Report"
]

# ------------ ASYNC EMAIL SENDER ---------------- #
def send_email_async(subject, body):
    sender = "saikumar.thota@pmsbazaar.com"
    sender_password = "fvzh fpje imdy buik"
    receiver = "saikumar.thota@pmsbazaar.com"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        # 10-second timeout prevents Render request blocking
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.starttls()
            server.login(sender, sender_password)
            server.sendmail(sender, receiver, msg.as_string())
        print("Email sent in background")
    except Exception as e:
        print("Email sending failed:", e)


# ---------------- LOGIN ROUTE ---------------- #
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if username in users and users[username]['password'] == password:
            return redirect(url_for("dashboard", username=username) + "/")
        else:
            flash("Invalid Username or Password")

    return render_template("login.html")


# ---------------- DASHBOARD ROUTE ---------------- #
@app.route("/dashboard/<username>/", methods=["GET", "POST"])
def dashboard(username):
    if username not in users:
        flash("Invalid user session")
        return redirect(url_for("login"))

    rm_name = users[username]["RM_Name"]
    mapped_investors = df[df["RM_Name"] == rm_name]["Investor_Name"].tolist()

    if request.method == "POST":
        investor = request.form["investor"]
        report = request.form["report"]
        from_date = request.form.get("from_date", "")
        to_date = request.form.get("to_date", "")

        subject = f"Report Request by {rm_name}"
        body = f"""
RM Name: {rm_name}
Investor: {investor}
Report: {report}
From Date: {from_date}
To Date: {to_date}
"""

        # Send email in background thread
        threading.Thread(
            target=send_email_async,
            args=(subject, body),
            daemon=True
        ).start()

        flash("Request submitted! Email is being sent in the background.")

    return render_template(
        "dashboard.html",
        investors=mapped_investors,
        reports=reports,
        rm_name=rm_name
    )


# ---------------- RUN APP (Render compatible) ---------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
