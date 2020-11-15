import os
import sys
import requests
from bs4 import BeautifulSoup
from time import sleep
LANGUAGES = {'cpp':'C++', 'py':'Python3', 'rs':'Rust'}


def main(*args):
    github_repository = check_project_structure()


def check_project_structure():
    for directory in ["./problems", "./data"]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    if not os.path.exists("./.git"):
        #Needs a check, wether or not git is installed on the system.
        github_repository = initialize_git()
    else:
        github_repository = os.popen("git remote get-url origin").read()

    if not os.path.exists("./data/kattis_problems.csv"):
        scrape_kattis(github_repository)

    if not os.path.exists("README.md"):
        readme_header()



def initialize_git():
    ### Maybe i should add email-validation and same for github repo , kattis profile
    username = input("Please insert your username: ")
    email = input("Please insert your email: ")
    github_repository = input("Please create a resository on github and copy the url into input: ")
    kattis_profile = set_kattis_profile()

    os.system("git init")
    os.system(f"git config --local user.name {username}")
    os.system(f"git config --local user.email {email}")
    os.system("git add README.md")
    os.system('git commit -m "first commit"')
    os.system("git branch -M main")
    os.system(f"git remote add origin {github_repository}")
    os.system("git push -u origin main")


def scrape_kattis(github_repository):
    print("Test: ", github_repository)
    print("scrape-scrape")


    """
    print("Gently scraping open.Kattis.com ...")
    print("... takes around 3 Minutes.")
    print("Scraping ...")
    problems = list()
    problems.append(["ID", "ProblemName", "LinkToKattis", "Difficulty", "LinkToGithub"])
    for i in range(28):
        print(f"... Page {i}")
        soup = request_soup(i)
        problems.extend(filter_problem_rows(soup, github_repository))
        sleep(5)
    write_csv(problems)
    """

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


def write_csv(info, dest='data/kattis_problems.csv'):
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
