import requests
import re
import json
import sqlite3
import hashlib
import os



def fetch_url(url, full_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open(full_path, 'w') as f:
            f.write(response.text)

        return response.text
    else:
        return False

def get_content(url):
    filename = hashlib.md5(url.encode('utf-8')).hexdigest()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    full_path = os.path.join(dir_path, filename)

    try:
        with open(full_path, 'r') as f:
            if os.stat(full_path).st_size > 0:
                content = f.read()
                return content
            else:
                return False
    except:
        return fetch_url(url, full_path)

def save_to_json(jobs):
    with open(os.path.dirname(os.path.realpath(__file__)) +'/jobs.json', 'w') as f:
        json.dump(jobs, f, indent=4)

def extract_jobs(content):
    job_blocks = re.findall(r'<article[^>]*class="[^"]*\bjob\b[^"]*"[^>]*>.*?</article>', content, re.DOTALL)

    jobs = []
    for block in job_blocks:
        link_match = re.search(r'href="([^"]+)"', block, re.DOTALL)   
        title_match = re.search(r'<h3 class="jobCard_title">(.+)<\/h3>', block, re.DOTALL)
        
        if link_match and title_match:
            job = {
                'title': title_match.group(1).strip(),
                'url': link_match.group(1).strip()
            }

            jobs.append(job)
    
    return jobs

def save_to_db(jobs):
    conn = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + '/jobs.db')
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, title TEXT, url TEXT)')

    for job in jobs:
        c.execute('INSERT INTO jobs (title, url) VALUES (?, ?)', (job['title'], job['url']))

    conn.commit()
    conn.close()

def get_from_db():
    conn = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + '/jobs.db')
    c = conn.cursor()

    c.execute('SELECT * FROM jobs')
    jobs = c.fetchall()

    conn.close()

    return jobs

def main():
    url = 'https://www.lejobadequat.com/emplois'

    content = get_content(url)

    if content:
        jobs = extract_jobs(content)
        
        save_to_json(jobs)

        save_to_db(jobs)
        jobs = get_from_db()

if __name__ == '__main__':
    main()