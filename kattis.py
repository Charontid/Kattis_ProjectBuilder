import os
import sys
import requests
from bs4 import BeautifulSoup
from time import sleep
import csv
from collections import defaultdict
from itertools import chain
LANGUAGES = {'cpp':'C++', 'py':'Python3', 'rs':'Rust'}
# search for : TODO
# marking places for further rework

def main():
    pass
    check_project_structure()
    git_commit_recent_changes()
    build_readme()


def check_project_structure():
    for directory in ["./problems", "./data"]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    if not os.path.exists("./.git"):
        #Needs a check, wether or not git is installed on the system.
        initialize_git()

    if not os.path.exists("./data/kattis_problems.csv"):
        print('scraping')
        scrape_kattis()


def initialize_git():
    ### Maybe i should add email-validation and same for github repo , kattis profile
    username = input("Please insert your username: ")
    email = input("Please insert your email: ")
    github_repository = input("Please create a resository on github and copy the url into input: ")
    kattis_profile = set_kattis_profile()
    write_gitignore()

    os.system("git init")
    os.system(f"git config --local user.name {username}")
    os.system(f"git config --local user.email {email}")
    os.system("git add README.md")
    os.system('git commit -m "first commit"')
    os.system("git branch -M main")
    os.system(f"git remote add origin {github_repository}")
    os.system("git push -u origin main")


def write_gitignore():
    with open(".gitignore", "w", encoding="UTF-8") as gitignore:
        patterns = ['.gitignore', '*.csv', '*.txt', '*data*', '*.in', '*.out']
        for pattern in patterns:
            gitignore.write(pattern)
            gitignore.write("\n")


def get_repository():
    """returns the remote url from .git/config, removes the .git at the end"""
    return os.popen("git remote get-url origin").read().strip()[:-4]


def git_commit_recent_changes():
    newly_added = os.popen("git ls-files --others --exclude-standard").read().split('\n')
    if newly_added[-1] == '':
        newly_added.pop()

    modified = os.popen("git ls-files -m").read().split('\n')
    if modified[-1] == '':
        modified.pop()

    for file in chain(newly_added, modified):
        os.system(f"git add {file}")
    os.system('git commit -m "adding new solutions"')
    os.system('git push -u origin main')


def scrape_kattis(num_pages=29):
    print("Gently scraping open.Kattis.com ...")
    print("... takes around 3 Minutes.")
    print("Scraping ...")
    problems = list()
    problems.append(["ID", "ProblemName", "LinkToKattis", "Difficulty", "LinkToGithub"])
    for i in range(num_pages):
        print(f"... Page {i}")
        soup = request_soup(i)
        problems.extend(filter_problem_rows(soup))
        sleep(5)
    write_csv(problems)


def request_soup(i):
    url = 'https://open.kattis.com/problems'
    parameters = {
        'page' : str(i),
        'order' : 'problem_difficulty',
        'dir' : 'asc'
    }
    source = requests.get(url, params=parameters)
    #print(source) # <Response[200]> #everything went - ok
    soup = BeautifulSoup(source.text, 'lxml')
    return soup


def filter_problem_rows(soup):
    kattis_url = 'https://open.kattis.com'
    problems_update = list()
    soup = soup.find_all('tr')
    for problem in soup:
        current = problem.find('a', href = True)
        try:
            link_to_kattis = kattis_url + current.get('href')
        except AttributeError:
            # there have been a few empty lines seperating the table rows
            continue
        problem_name, *_, difficulty = [x for x in problem.text.split('\n') if x != '']
        github_repository = get_repository()
        if problem_name != 'Name':
            id = link_to_kattis.split('/')[-1]
            link_to_github = '/'.join([github_repository, 'blob/master/problems', id, id])
            problems_update.append([id, problem_name, link_to_kattis, difficulty, link_to_github])
    return problems_update


def write_csv(info, dest='data/kattis_problems.csv'):
    for problem in info:
        print(problem)

    with open(dest, 'w', encoding='UTF-8') as csv_file:
        spamwriter = csv.writer(
            csv_file,
            delimiter=';',
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
        )
        for row in info:
            spamwriter.writerow(row)


def set_kattis_profile():
    kattis_profile = input("Please copy the url to your profile on open.kattis.org: ")
    with open("data/kattis_profile.txt", "w", encoding="UTF-8") as target:
        target.write(kattis_profile)
    return kattis_profile


def get_kattis_profile():
    with open("data/kattis_profile.txt", "r", encoding="UTF-8") as source:
        return next(source)



#### BUILDING README
def build_readme():
    solved = tracked_files()
    #Match to Kattis data:
    readme_header()
    place_in_readme = match_problems(solved)
    readme_table(place_in_readme)
    os.system("git add README.md")
    os.system('git commit -m "README - update"')
    os.system('git push -u origin main')


def readme_table(place_in_readme):
    """Adding the problem table"""
    # sort descending
    place_in_readme.sort(key=lambda x: -float(x.get('Difficulty')))

    with open('README.md', 'a', encoding='UTF-8') as readme: #TODO Most likely either making a global or reading from a user file
        lang_rev = {
            'py' : 'Python3',
            'cpp' : 'C++'
        }
        for problem in place_in_readme:
            description = f"[{problem['ProblemName']}]({problem['LinkToKattis']})"
            langs = list()
            for link in problem['FileLinks']:
                langs.append(f"[{lang_rev[link.split('.')[-1]]}]({link})")
            difficulty = problem.get('Difficulty')
            readme.write(f"| {description} | {', '.join(langs)} | {difficulty} |\n")


def tracked_files():
    """Gets every file currently tracked by git:"""
    files = os.popen("git ls-files").read().split('\n')
    if files[-1] == '':
        files.pop()
    solved = defaultdict(list)
    for file in files:
        *_, file = file.split('/')
        id, language = file.split('.')
        if language in LANGUAGES.keys():
            solved[id].append(language)
    del solved['kattis'] # project builder
    return solved


def match_problems(solved):
    with open('data/kattis_problems.csv', 'r', encoding='UTF-8') as kattiscsv:
        fieldnames = next(kattiscsv).strip().split(';')
        kattis = csv.DictReader(
            kattiscsv,
            delimiter=';',
            fieldnames=fieldnames,
            restkey="Garbage",
            skipinitialspace=True
        )

        place_in_readme = list()
        for problem in kattis:
            matched_languages = solved.get(problem['ID'])
            if matched_languages: # not None --> at least one file matching
                #Building Links to the language-specific files:
                file_links = list()
                for language in matched_languages:
                    file_links.append('.'.join([problem.get('LinkToGithub'), language]))

                problem['FileLinks'] = file_links
                problem['Languages'] = matched_languages
                place_in_readme.append(problem)
                #remove matches from solved:
                del solved[problem['ID']]

    scraping_flag = True if len(solved) > 1 else False
    if scraping_flag == True:
        print("MAYBE THERE IS STILL A BUG")
        print("please check the problem, wether or not the problem-id's are correct:")
        print("unmachted Problems: ", len(solved))
        print(solved.keys())
        while True:
            choice = input("Do you want to force scraping on the next run? (0):No, (1):Yes")
            if choice in {'0', '1'}:
                break
    return place_in_readme#, scraping_flag


def get_kattis_profile():
    with open("data/kattis_profile.text", "r", encoding="UTF-8") as profile:
        return next(profile)


def readme_header():
    """
    Writing the Repositoriy Description to README.md
    """
    with open('README.md', 'w', encoding='UTF-8') as readme:
        readme.write('# Kattis\n')
        readme.write('Solutions for a couple of Coding-Riddles on [Kattis](https://open.kattis.com).\n')
        readme.write('[My Profile]({get_kattis_profile()}) on Kattis.\n')
        readme.write('\n')
        readme.write("Project build with [Kattis_ProjectManager](https://github.com/Charontid/Kattis_ProjectBuilder)\n")
        readme.write('\n')
        readme.write('## Problems\n')
        readme.write('| Problem Description | Languages | Difficulty |\n')
        readme.write('| - | - | - |\n')


if __name__ == '__main__':
    print(*sys.argv)
    main()
