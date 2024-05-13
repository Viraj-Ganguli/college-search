from flask import Flask, redirect, render_template, request

import sqlite3

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/", methods=["GET", "POST"])
def main():
	with sqlite3.connect('college.db') as conn:
		conn.row_factory = sqlite3.Row
		cursor = conn.cursor()
		# assemble the db query
		query = "SELECT UNITID, INSTNM, CITY, STABBR, ZIP, INSTURL, ADM_RATE FROM colleges "

		cursor.execute(query)
		rows = (cursor.fetchall())
	return render_template("index.html", colleges = rows)

# College detail page
@app.route('/college/<college_id>')
def detail(college_id):
	with sqlite3.connect('college.db') as conn:
		conn.row_factory = sqlite3.Row
		cursor = conn.cursor()
		cursor.execute("SELECT UNITID, INSTNM, CITY, STABBR, ZIP, INSTURL, LATITUDE, LONGITUDE, ADM_RATE, SAT_AVG, COSTT4_A, TUITIONFEE_IN, TUITIONFEE_OUT, UGDS, UGDS_WHITE, UGDS_BLACK, UGDS_HISP, UGDS_ASIAN, UGDS_AIAN, UGDS_NHPI, UGDS_2MOR, UGDS_NRA, UGDS_UNKN FROM colleges WHERE UNITID=?", [college_id])
		row = (cursor.fetchone())
		
	return render_template("detail.html", college = row)



app.run(host='0.0.0.0', port=8080)
