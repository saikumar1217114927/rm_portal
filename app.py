from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Load RM and investor mapping
df = pd.read_excel("rm_investors.xlsx")

# Create a dictionary for login
users = {row['Username']: {'password': row['Password'], 'RM_Name': row['RM_Name']} for idx, row in df.iterrows()}

# Reports list
reports = [
    "Portfolio Factsheet",
    "Portfolio Apprisal",
    "Performance Apprisal",
    "Statement of Capital Gain/Loss",
    "Transaction Report",
    "Dividend Report"
]

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            return redirect(url_for('dashboard', username=username))
        else:
            flash("Invalid Credentials")
    return render_template("login.html")

@app.route("/dashboard/<username>", methods=["GET", "POST"])
def dashboard(username):
    rm_name = users[username]['RM_Name']
    mapped_investors = df[df['RM_Name'] == rm_name]['Investor_Name'].tolist()
    
    if request.method == "POST":
        investor = request.form['investor']
        report = request.form['report']
        from_date = request.form.get('from_date', '')
        to_date = request.form.get('to_date', '')
        
        # Send Email
        sender = "saikumar.thota@pmsbazaar.com"
        password = "fvzh fpje imdy buik"
        receiver = "saikumar.thota@pmsbazaar.com"
        
        subject = f"Report Request by {rm_name}"
        body = f"""
        RM Name: {rm_name}
        Investor: {investor}
        Report: {report}
        From Date: {from_date}
        To Date: {to_date}
        """
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver
        
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender, password)
                server.sendmail(sender, receiver, msg.as_string())
            flash("Request Sent Successfully!")
        except Exception as e:
            flash(f"Error sending email: {e}")
    
    return render_template("dashboard.html", investors=mapped_investors, reports=reports, rm_name=rm_name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
