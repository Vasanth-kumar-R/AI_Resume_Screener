#!/usr/bin/env python3
"""
scripts/generate_sample_data.py
Programmatically generates a sample Job Description and 12 synthetic resumes in plain text.
Saves them to data/jd/ and data/resumes/ respectively.
"""
from __future__ import annotations

import os
from pathlib import Path

# Resolve path relative to script location
ROOT = Path(__file__).resolve().parent.parent
JD_DIR = ROOT / "data" / "jd"
RESUMES_DIR = ROOT / "data" / "resumes"


JD_CONTENT = """JOB TITLE: Senior Backend Engineer
DEPARTMENT: Engineering
REPORTS TO: Director of Engineering

ROLE OVERVIEW:
We are looking for a Senior Backend Engineer to join our core team. In this role, you will design, build, and maintain highly scalable backend services. You will collaborate closely with product managers, frontend developers, and data engineers to deliver high-quality features and services.

REQUIRED SKILLS:
- Python
- FastAPI
- PostgreSQL
- Docker
- Git
- Redis
- AWS

MINIMUM EXPERIENCE:
- 5 years of professional backend software engineering experience.

MINIMUM EDUCATION:
- Bachelor's degree in Computer Science, Software Engineering, or a related technical field.

PREFERRED SKILLS & QUALIFICATIONS:
- Experience with asyncio and concurrent programming in Python.
- Familiarity with vector databases and search engines (ElasticSearch, FAISS, Milvus).
- Master's degree in Computer Science or a technical field.
"""

RESUMES = {
    # ── Strong Matches (Meets experience, education, and has most required skills)
    "strong_alice_chen.txt": """Alice Chen
Email: alice.chen@example.com
Phone: +1-555-0101
LinkedIn: linkedin.com/in/alicechen

PROFESSIONAL SUMMARY:
Senior Software Engineer with over 6 years of experience building high-performance backend systems. Expert in Python, FastAPI, and database design using PostgreSQL. Passionate about automated testing, CI/CD, and serverless architectures.

PROFESSIONAL EXPERIENCE:
Senior Software Engineer | FinTech Solutions (2022 - Present)
- Architected and built microservices using Python and FastAPI, handling 10k+ requests per second.
- Migrated legacy data schemas to PostgreSQL, reducing query latency by 40%.
- Integrated Redis for high-speed session caching and message queues.
- Deployed services to AWS using Docker containers and Terraform.

Backend Engineer | TechGlobal (2018 - 2022)
- Designed APIs with Flask and FastAPI.
- Worked with PostgreSQL, SQL Server, and Git for version control.
- Automated testing using pytest, increasing coverage from 50% to 92%.

EDUCATION:
Master of Science in Computer Science | Stanford University (2018)
Bachelor of Science in Computer Science | Stanford University (2016)

TECHNICAL SKILLS:
Languages: Python, SQL, JavaScript
Frameworks: FastAPI, Flask, Django
Databases: PostgreSQL, Redis, DynamoDB
Tools & Cloud: Docker, AWS, Git, Terraform, Jenkins, Redis, CI/CD
""",

    "strong_bob_miller.txt": """Bob Miller
Email: bob.miller@example.com
Phone: +1-555-0102

SUMMARY:
Highly skilled Backend Developer with 7 years of industry experience specialising in API design and scalable infrastructure. Proficient in Python, containerisation with Docker, and cloud engineering on AWS.

WORK EXPERIENCE:
Lead Developer | CloudNest Inc. (2021 - Present)
- Led a team of 4 engineers in developing a cloud-based storage orchestrator.
- Designed system endpoints using FastAPI and PostgreSQL.
- Utilised Redis to manage background workers and celery task queues.
- Containerised all applications with Docker, deploying them to AWS ECS.

Software Engineer | DevCorp (2017 - 2021)
- Wrote reliable backend services in Python, Django, and Flask.
- Managed source code and code reviews using Git and GitLab.
- Designed and maintained PostgreSQL schemas.

EDUCATION:
Bachelor of Science in Software Engineering | University of Michigan (2017)

SKILLS:
Python, FastAPI, Django, Docker, AWS, PostgreSQL, Redis, Git, Gitlab, ECS, Microservices
""",

    # ── Medium Matches (Meets education, but borderline experience or misses a few key skills)
    "medium_charlie_patel.txt": """Charlie Patel
Email: charlie.p@example.com
Phone: +1-555-0103

SUMMARY:
Backend Software Developer with 4 years of experience specializing in Python and FastAPI. Experience designing APIs and working with containerized services.

EXPERIENCE:
Software Engineer | AppForge (2020 - Present)
- Developed APIs using Python, FastAPI, and SQLAlchemy.
- Managed databases with PostgreSQL and Redis.
- Used Git for version control and collaborated in an agile team.
- Containerised services with Docker.

Junior Backend Developer | ByteLabs (2019 - 2020)
- Assisted in Python script optimization and cron job monitoring.
- Documented API endpoints.

EDUCATION:
Bachelor of Technology in Computer Science | IIT Bombay (2019)

SKILLS:
Python, FastAPI, PostgreSQL, Redis, Docker, Git, SQL, Flask, Linux
""",

    "medium_david_jones.txt": """David Jones
Email: david.jones@example.com
Phone: +1-555-0104

SUMMARY:
Backend Engineer with 8 years of software development experience. Primarily worked with Ruby on Rails and Node.js, recently transitioned to Python and FastAPI.

EXPERIENCE:
Senior Engineer | WebFlow (2018 - Present)
- Developed robust web services using Ruby on Rails, PostgreSQL, and AWS.
- Created microservices in Node.js and deployed them using Docker.
- Managed infrastructure on AWS (EC2, S3, RDS).

Software Engineer | RubyDevs (2015 - 2018)
- Built e-commerce backends with Ruby, PostgreSQL, and Redis.
- Managed codebases using Git.

EDUCATION:
Bachelor of Science in Information Technology | Temple University (2015)

SKILLS:
Ruby on Rails, Node.js, JavaScript, PostgreSQL, AWS, Git, Docker, Python, FastAPI (basic), SQL, Redis
""",

    "medium_elena_smirnova.txt": """Elena Smirnova
Email: elena.s@example.com
Phone: +1-555-0105

SUMMARY:
Python enthusiast with 5 years of experience in data engineering and backend services. Proficient in database schemas and AWS analytics integrations.

EXPERIENCE:
Data Engineer | DataStream LLC (2021 - Present)
- Designed data pipelines using Python, PostgreSQL, and AWS Redshift.
- Written internal APIs using Flask to serve data models.
- Deployed worker instances to AWS.

Backend Developer | CodeWeb (2019 - 2021)
- Maintained web APIs using Django, PostgreSQL, and Docker.
- Used Git for team collaboration.

EDUCATION:
Master of Science in Information Systems | Moscow State University (2019)

SKILLS:
Python, Flask, Django, PostgreSQL, AWS, Git, Docker, SQL, Pandas, NumPy, Redis
""",

    # ── Weak Matches (Under-experienced, missing several required skills, or wrong education level)
    "weak_eve_adams.txt": """Eve Adams
Email: eve.a@example.com
Phone: +1-555-0106

SUMMARY:
Junior Developer looking for a backend role. Competent in Python programming, HTML/CSS, and basic Git usage. Eager to learn cloud platforms and databases.

EXPERIENCE:
Associate Software Engineer | LaunchPad Tech (2023 - Present)
- Maintained legacy Python scripts.
- Developed basic web scraper scripts.
- Used Git for individual projects.

EDUCATION:
Associate Degree in Applied Science | Austin Community College (2022)

SKILLS:
Python, Git, HTML, CSS, JavaScript, SQLite
""",

    "weak_frank_miller.txt": """Frank Miller
Email: frank.m@example.com
Phone: +1-555-0107

SUMMARY:
Frontend Engineer with 6 years of experience who wants to transition to Full Stack / Backend roles. Strong expertise in JavaScript, React, and CSS. Limited backend experience.

EXPERIENCE:
Senior Frontend Developer | UI Craft (2020 - Present)
- Designed interactive UI dashboards using React, Redux, and JavaScript.
- Handled state management and client-side page load optimization.
- Styled components using Tailwind CSS and Git for version control.

Frontend Engineer | DesignGrid (2018 - 2020)
- Created responsive pages using HTML, CSS, React.

EDUCATION:
Bachelor of Arts in Graphic Design | NYU (2017)

SKILLS:
React, JavaScript, TypeScript, Tailwind CSS, HTML5, CSS3, Git, Python (basic), Node.js (basic)
""",

    "weak_george_clark.txt": """George Clark
Email: george.c@example.com
Phone: +1-555-0108

SUMMARY:
Software developer with 3 years of experience. Experienced with PHP and Laravel framework. Basic knowledge of Python and Docker.

EXPERIENCE:
Web Developer | WebPros (2021 - Present)
- Developed ecommerce sites using PHP, Laravel, and MySQL.
- Containerised local development environment using Docker.
- Managed repositories with Git.

EDUCATION:
High School Diploma | Central High School (2019)

SKILLS:
PHP, Laravel, MySQL, Git, Docker (basic), Python (basic), HTML, CSS
""",

    # ── Clear Mismatches (Completely unrelated field, or zero backend software engineering)
    "mismatch_grace_taylor_chef.txt": """Grace Taylor
Email: chefgrace@example.com
Phone: +1-555-0109

SUMMARY:
Professional Head Chef with 10+ years of culinary experience in high-volume, upscale restaurants. Skilled in menu development, kitchen staff training, food safety, inventory cost control, and customer satisfaction.

PROFESSIONAL EXPERIENCE:
Head Chef | The Bistro Garden (2021 - Present)
- Supervise a kitchen team of 15 cooks and stewards.
- Designed seasonal menus which boosted restaurant sales by 25%.
- Maintained zero food safety violations over 3 years.
- Managed food inventory budget of $50,000 monthly.

Sous Chef | Ocean Grill (2016 - 2021)
- Managed line execution and daily specials preparation.
- Trained incoming kitchen staff.

EDUCATION:
Associate Degree in Culinary Arts | Culinary Institute of America (2015)

SKILLS:
Culinary Arts, Menu Planning, Cost Control, Staff Management, Food Safety, Kitchen Operations, Event Catering
""",

    "mismatch_harold_finch_teacher.txt": """Harold Finch
Email: harold.f@example.com
Phone: +1-555-0110

SUMMARY:
Dedicated High School History Teacher with 8 years of classroom experience. Experienced in curriculum design, student assessment, parent communication, and educational technology integration.

EXPERIENCE:
History Teacher | Oakridge High School (2018 - Present)
- Teach AP US History and World History courses to over 150 students.
- Designed digital history curriculum, incorporating interactive maps and quizzes.
- Led the student History Club and organized annual field trips.

Social Studies Teacher | Riverdale Academy (2015 - 2018)
- Developed lesson plans for middle school social studies classes.
- Graded assessments and held parent-teacher conferences.

EDUCATION:
Master of Education | Columbia University (2015)
Bachelor of Arts in History | Boston College (2013)

SKILLS:
Curriculum Design, Lesson Planning, Classroom Management, Student Assessment, Educational Tech, Public Speaking
""",

    # ── Borderline Matches (Right skills, but too few years of experience, or right experience but lacks key technical skills)
    "borderline_irene_adler.txt": """Irene Adler
Email: irene.adler@example.com
Phone: +1-555-0111

SUMMARY:
Highly motivated Software Engineering graduate with strong technical capabilities. Excellent knowledge of Python, FastAPI, Docker, PostgreSQL, AWS, and Git. Lacks professional workplace experience.

EXPERIENCE:
Backend Intern | CodeBase Inc. (May 2024 - August 2024)
- Built REST API endpoints in Python using FastAPI.
- Wrote SQL queries for PostgreSQL databases.
- Contributed to Docker-compose setups for local testing.

University Projects (2020 - 2024)
- Built a microservices app deployed on AWS using ECS, Docker, Python, and Git.

EDUCATION:
Bachelor of Science in Computer Science | MIT (2024)

SKILLS:
Python, FastAPI, Docker, PostgreSQL, AWS, Git, Redis, Linux, Agile
""",

    "borderline_jack_reacher.txt": """Jack Reacher
Email: jack.r@example.com
Phone: +1-555-0112

SUMMARY:
Senior Systems Administrator with 10 years of experience managing Linux infrastructure, Docker containers, AWS deployments, and version control with Git. Basic Python scripting knowledge. No API development experience.

EXPERIENCE:
Senior DevOps & Systems Administrator | CyberSecurity Ltd (2019 - Present)
- Maintained high-availability servers on AWS.
- Configured and deployed Docker containers across multiple clusters.
- Managed configuration files and codebase version control with Git.
- Developed internal bash and Python scripts to automate system health checks.

Systems Administrator | NetSolutions (2014 - 2019)
- Maintained Linux servers and internal networks.

EDUCATION:
Bachelor of Science in Computer Engineering | Georgia Tech (2014)

SKILLS:
Linux, AWS, Docker, Git, Python (scripting), Bash Scripting, Network Security, Ansible, Kubernetes
"""
}


def main():
    # Ensure directories exist
    JD_DIR.mkdir(parents=True, exist_ok=True)
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)

    print("Creating data directories...")
    
    # Write Job Description
    jd_path = JD_DIR / "sample_job_description.txt"
    with open(jd_path, "w", encoding="utf-8") as f:
        f.write(JD_CONTENT.strip())
    print(f"Generated Job Description: {jd_path.relative_to(ROOT)}")

    # Write Resumes
    print(f"Generating {len(RESUMES)} sample resumes...")
    for filename, content in RESUMES.items():
        resume_path = RESUMES_DIR / filename
        with open(resume_path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"   -> Created: {resume_path.relative_to(ROOT)}")
        
    print("\nSample data generation complete!")


if __name__ == "__main__":
    main()
