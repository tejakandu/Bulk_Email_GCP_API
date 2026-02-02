from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Teja Kandukuri | Data Engineer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; color: #333; background: #f7f9fc; }
        header { background: #004c99; color: white; padding: 40px 20px; text-align: center; }
        section { max-width: 900px; margin: 40px auto; padding: 0 20px; }
        h1, h2, h3 { color: #004c99; }
        ul { list-style-type: disc; margin-left: 20px; }
        .cta { background: #007acc; color: white; padding: 10px 20px; display: inline-block; text-decoration: none; border-radius: 5px; }
        footer { background: #004c99; color: white; text-align: center; padding: 20px; margin-top: 40px; }
    </style>
</head>
<body>

<header>
    <h1>Teja Kandukuri</h1>
    <h3>GCP / AWS Data Engineer</h3>
    <p>Building scalable, cloud-native data pipelines across Insurance, Finance, and Healthcare domains.</p>
    <a class="cta" href="/static/Teja_Kandukuri_GCP_Data%20Engineer.pdf" download>Download Resume</a>
</header>

<section>
    <h2>About Me</h2>
    <p>I’m a certified data engineer with over 5 years of experience building enterprise-grade data pipelines on GCP and AWS. I design cloud-native, scalable ETL/ELT frameworks and deliver production-ready analytics systems with a focus on quality, reliability, and compliance.</p>
</section>

<section>
    <h2>Technical Skills</h2>
    <ul>
        <li><strong>Languages:</strong> Python, SQL, Java</li>
        <li><strong>Cloud:</strong> GCP (BigQuery, Dataflow, Composer), AWS (Glue, Redshift, S3, Lambda)</li>
        <li><strong>Big Data:</strong> Spark, Kafka, Databricks, Apache Iceberg</li>
        <li><strong>Tools:</strong> Airflow, Looker Studio, Tableau</li>
        <li><strong>Certifications:</strong> AWS Data Analytics Specialty (2023), AWS Cloud Practitioner (2020)</li>
    </ul>
</section>

<section>
    <h2>Experience</h2>
    <h3>GCP Data Engineer – Definity Financial Corp</h3>
    <p>Mar 2023 – Present</p>
    <ul>
        <li>Integrated Guidewire & Salesforce data into GCP BigQuery via Airflow and Cloud Functions</li>
        <li>Designed CDC workflows using Databricks & implemented schema evolution</li>
        <li>Built real-time ingestion using Pub/Sub and improved reporting with Looker dashboards</li>
    </ul>

    <h3>AWS Data Engineer – Accenture</h3>
    <p>Aug 2018 – Aug 2021</p>
    <ul>
        <li>Built scalable data lakes using Glue, Lambda, and Redshift</li>
        <li>Migrated on-prem Oracle to AWS, implemented real-time ingestion using Kinesis</li>
    </ul>
</section>

<section>
    <h2>Contact</h2>
    <p>Email: <a href="mailto:tejak.de@gmail.com">tejak.de@gmail.com</a></p>
    <p>LinkedIn: <a href="https://linkedin.com/in/kandukuri-teja" target="_blank">kandukuri-teja</a></p>
</section>

<footer>
    <p>&copy; 2025 Teja Kandukuri. All rights reserved.</p>
</footer>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)
