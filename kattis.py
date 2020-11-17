import os
import sys
import requests
from bs4 import BeautifulSoup
from time import sleep
import csv
from collections import defaultdict
from itertools import chain
LANGUAGES = {'cpp':'C++', 'py':'Python3', 'rs':'Rust'}


def main(*args):
    #check_project_structure()
    git_recent_changes()

    #with open("data/kattis_problems.csv", "r", encoding='UTF-8') as source:
    #    for line in source:
    #        print(line)
    #        print()


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

    #if not os.path.exists("README.md"):
    #    readme_header()
    #build_readme()


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
    print('solved')
    for problem in solved:
        print(problem)
    #Match to Kattis data:
    """
    place_in_readme, scraping_flag = match_problems(solved)
    #Write the readme.md
    header(scraping_flag)
    readme_table(place_in_readme)
    os.system("git add readme.md")
    return scraping_flag
    """


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


def git_recent_changes():
    newly_added = os.popen("git ls-files --others --exclude-standard").read().split('\n')
    if newly_added[-1] == '':
        newly_added.pop()
    modified = os.popen("git ls-files -m").read().split('\n')
    print('modified: ', modified)
    if modified[-1] == '':
        modified.pop()

    for file in chain(newly_added, modified):
        os.system(f"git add {file}")

    print(newly_added)
    print(modified)
    """
    if newly_added and modified:
        chained = chain([newly_added], modified)
    elif newly_added and not modified:
        chained = newly_added
    elif not newly_added and modified:
        chained = modified
    """
    """
    else:
        chained = None
    if chained:
        for file in chained:
            os.system(f"git add {file}")
    """











def readme_header():
    """
    Writing the Repositoriy Description to readme.md
    """
    with open('README.md', 'w', encoding='UTF-8') as readme:
        readme.write('# Kattis\n')
        readme.write('Solutions for a couple of Coding-Riddles on [Kattis](https://open.kattis.com)\n')
        readme.write('\n')
        readme.write("Project build with [Kattis_ProjectManager](https://github.com/Charontid/Kattis_ProjectBuilder)\n")
        readme.write()


if __name__ == '__main__':
    main()
    """
    if len(sys.argv) == 3:
        main(*sys.argv[1:])
    elif len(sys.argv) == 1:
        main()
    """
    #else:
    #    raise SyntaxError("""Insufficient arguments:
    #    call with 0 arguments: push recent changes to github repository
    #    call with 2 arguments: probem id and filesuffix one of (.py, .cpp, ...)
    #    to create a new problem
    #    """)
