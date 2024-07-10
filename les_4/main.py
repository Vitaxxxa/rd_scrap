import requests
import re
import json

def listToJsonFile(list):
    json_list = json.dumps(list)

    with open('./jobs.json', 'w') as f:
        f.write(json_list)

def run():
    url = 'https://www.lejobadequat.com/emplois'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        pattern = r'<h3 class="jobCard_title">(.*?)</h3>'

        titles = re.findall(pattern, response.text)
        #print(titles)

        if titles:
            listToJsonFile(titles)
    else:
        print(f"Status code: {response.status_code}")


if __name__ == "__main__":
    run()