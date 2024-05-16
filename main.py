from flask import Flask, render_template, request
import sqlite3

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

def search_schools(college, searchTerm):
    return searchTerm.lower() in college['INSTNM'].lower()



def filter_colleges(colleges, min_admission, max_admission, min_tuition, max_tuition, min_sat, max_sat, state, tuition_type, searchTerm):
    filtered_colleges = []
    for college in colleges:
        # Convert strings to floats for comparison
        adm_rate_str = college['ADM_RATE']
        sat_avg_str = college['SAT_AVG']
        tuition_str = college['TUITIONFEE_OUT'] if tuition_type == 'outstate' else college['TUITIONFEE_IN']

        # Check if any of the values are 'NULL'
        if adm_rate_str == 'NULL' or tuition_str == 'NULL' or sat_avg_str == 'NULL':
            continue

        adm_rate = float(adm_rate_str)
        sat_avg = float(sat_avg_str)
        tuition = float(tuition_str)



        # Apply filters
        if (adm_rate >= min_admission and adm_rate <= max_admission and
            tuition >= min_tuition and tuition <= max_tuition and
            sat_avg >= min_sat and sat_avg <= max_sat and
            (state == '' or college['STABBR'] == state) and 
        search_schools(college, searchTerm)):
            filtered_colleges.append(college)

    return filtered_colleges


@app.route("/", methods=["GET", "POST"])
def main():
    # Retrieve filter parameters from the request
    min_admission_percent = request.args.get("minAdmission", 0, type=float)
    max_admission_percent = request.args.get("maxAdmission", 100, type=float)
    min_admission_decimal = min_admission_percent / 100
    max_admission_decimal = max_admission_percent / 100
    min_tuition = request.args.get("minTuition", 0, type=float)
    max_tuition = request.args.get("maxTuition", 100000, type=float)
    min_sat = request.args.get("minSAT", 400, type=float)
    max_sat = request.args.get("maxSAT", 1600, type=float)
    print("======================", request.args.get("tuitionType", ""), "============================")
    tuition_type = request.args.get("tuitionType", "")
    state = request.args.get("state", "")
    searchTerm = request.args.get("searchTerm", "")



    with sqlite3.connect('college.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT UNITID, INSTNM, CITY, STABBR, ZIP, INSTURL, ADM_RATE, SAT_AVG, TUITIONFEE_IN, TUITIONFEE_OUT FROM colleges")
        rows = cursor.fetchall()

    filtered_colleges = filter_colleges(rows, min_admission_decimal, max_admission_decimal, min_tuition, max_tuition, min_sat, max_sat, state, tuition_type, searchTerm)

    return render_template("index.html", colleges=filtered_colleges, tuition_type=tuition_type)


@app.route('/college/<college_id>')
def college_detail(college_id):
    with sqlite3.connect('college.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM colleges WHERE UNITID = ?", (college_id,))
        college = cursor.fetchone()

    return render_template("college_detail.html", college=college)

@app.route('/college_data/<college_id>')
def college_data(college_id):
    with sqlite3.connect('college.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ethnicity, percentage
            FROM student_ethnicity
            WHERE college_id = ?""", [college_id])
        rows = cursor.fetchall()
        data = [{'ethnicity': row['ethnicity'], 'percentage': row['percentage']} for row in rows]

    return jsonify(data) 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)