import calendar
import os
import requests
from datetime import datetime

USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')
HOST = os.environ.get('HOST')
IGNORED_PROJECTS = [int(x) for x in os.environ.get('IGNORED_PROJECTS').split(",")]

API_URL = f"{HOST}/api/v1"


def login(username, password) -> dict:
    # login to the api
    response = requests.post(f"{API_URL}/auth", json={"username": username, "password": password, "type": "normal"})
    # return the token
    if response.status_code != 200:
        print(response.json())
        exit(1)
    return {"auth_token": response.json()["auth_token"], "refresh": response.json()["refresh"], "full_name": response.json()["full_name"], "id": response.json()["id"]}

def getProjectList(auth_token):
    resp = requests.get(f"{API_URL}/projects", headers={"Authorization": f"Bearer {auth_token}"})
    if resp.status_code != 200:
        print(resp.json())
    return resp.json()

def getProject(auth_token, project_id):
    resp = requests.get(f"{API_URL}/projects/{project_id}", headers={"Authorization": f"Bearer {auth_token}"})
    if resp.status_code != 200:
        print(resp.json())
    return resp.json()

def listMilestoneByProject(auth_token, project_id):
    resp = requests.get(f"{API_URL}/milestones?project={project_id}", headers={"Authorization": f"Bearer {auth_token}"})
    if resp.status_code != 200:
        print(resp.json())
    return resp.json()

def getUserStory(auth_token, userstory_id):
    resp = requests.get(f"{API_URL}/userstories/{userstory_id}", headers={"Authorization": f"Bearer {auth_token}"})
    if resp.status_code != 200:
        print(resp.json())
    return resp.json()


auth = login(USERNAME, PASSWORD)
allprojects = getProjectList(auth["auth_token"])



MyProjects = []
for project in allprojects:
    if project["id"] in IGNORED_PROJECTS:
        continue
    if project["i_am_member"]:
        MyProjects.append(project)
# get first day of this month
first_day = datetime.today().replace(day=1)
# get last day of this month
last_day = datetime.today().replace(day=calendar.monthrange(datetime.today().year, datetime.today().month)[1])


print("You have access to the following projects:")
for i, project in enumerate(MyProjects):
    print(f"{i}: {project['name']}\t {project['id']}")

overall_points = 0
for project in MyProjects:
    print("=====================================")
    print(f"Project: {project['name']}")
    print(f"Milestones: ")
    point_total = 0
    milestonethismonth = []
    for milestone in listMilestoneByProject(auth["auth_token"], project["id"]):
        if first_day <= datetime.fromisoformat(milestone["estimated_finish"]) <= last_day:
            milestonethismonth.append(milestone)
    for milestone in milestonethismonth:
        print(f"{milestone['name']} \t {milestone['estimated_finish']}")
        for userstory in milestone["user_stories"]:
            id = userstory["id"]
            userstory = getUserStory(auth["auth_token"], id)
            if auth["id"] in userstory["assigned_users"]:
                point_total += userstory["total_points"] / len(userstory["assigned_users"])
                print(f"\t{userstory['subject']} \t {userstory['total_points'] / len(userstory['assigned_users'])}")
    print(f"Total points: {point_total}")
    overall_points += point_total

print("=====================================")
print(f"Overall points: {overall_points}")
print("=====================================")