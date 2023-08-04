import calendar
import os
from datetime import datetime
from dotenv import load_dotenv
import getpass

load_dotenv()

USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')
HOST = os.environ.get('HOST')
IGNORED_PROJECTS = os.environ.get('IGNORED_PROJECTS')
if IGNORED_PROJECTS is None:
    IGNORED_PROJECTS = ""
else:
    IGNORED_PROJECTS = [int(x) for x in IGNORED_PROJECTS.split(",")]

API_URL = f"{HOST}/api/v1"

USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')
HOST = os.environ.get('HOST')
IGNORED_PROJECTS = [int(x) for x in os.environ.get('IGNORED_PROJECTS').split(",")]

API_URL = f"{HOST}/api/v1"

import requests_cache

requests = requests_cache.CachedSession('demo_cache')


class TaigaInterface:
    def __init__(self, username, password):
        self.user = self.login(username, password)
        self.auth_token = self.user["auth_token"]

    def login(self, username, password) -> dict:
        print("Logging in...")
        # login to the api
        response = requests.post(f"{API_URL}/auth", json={"username": username, "password": password, "type": "normal"})
        # return the token
        if response.status_code != 200:
            print(response.json())
            exit(1)
        print("Login successful!")
        return {"auth_token": response.json()["auth_token"], "refresh": response.json()["refresh"], "full_name": response.json()["full_name"], "id": response.json()["id"]}
    
    def getProjectList(self):
        resp = requests.get(f"{API_URL}/projects", headers={"Authorization": f"Bearer {self.auth_token}"})
        if resp.status_code != 200:
            print(resp.json())
        return resp.json()

    def getProject(self, project_id):
        resp = requests.get(f"{API_URL}/projects/{project_id}", headers={"Authorization": f"Bearer {self.auth_token}"})
        if resp.status_code != 200:
            print(resp.json())
        return resp.json()

    def listMilestoneByProject(self, project_id):
        resp = requests.get(f"{API_URL}/milestones?project={project_id}", headers={"Authorization": f"Bearer {self.auth_token}"})
        if resp.status_code != 200:
            print(resp.json())
        return resp.json()

    def getUserStory(self, userstory_id):
        resp = requests.get(f"{API_URL}/userstories/{userstory_id}", headers={"Authorization": f"Bearer {self.auth_token}"})
        if resp.status_code != 200:
            print(resp.json())
        return resp.json()
    def getUsers(self):
        resp = requests.get(f"{API_URL}/users",  headers={"Authorization": f"Bearer {self.auth_token}"})
        if resp.status_code != 200:
            print(resp.json())
        userlist = resp.json()

        self.users = []
        for user in userlist:
            self.users.append({"id": user["id"], "full_name": user["full_name"]})
        return self.users

class UserInterface:
    def __init__(self, taiga_interface):
        self.taiga = taiga_interface
        self.projects = self.getProjects()
        self.first_day = datetime(2023,7,1)
        self.last_day = datetime(2023,7,31)
        self.overall_points = 0
        self.allUsersPoints = {}

    def getProjects(self):
        allprojects = self.taiga.getProjectList()
        MyProjects = []
        for project in allprojects:
            if project["id"] in IGNORED_PROJECTS:
                continue
            if project["i_am_member"]:
                MyProjects.append(project)
        return MyProjects

    def printProjects(self):
        print("You have access to the following projects:")
        for i, project in enumerate(self.projects):
            print(f"{i}: {project['name']}")

    def printMilestones(self, project, userid):
        print("------------------------")
        print(f"Project: {project['name']}")
        print(f"Milestones: ")
        point_total = 0
        milestonethismonth = []
        for milestone in self.taiga.listMilestoneByProject(project["id"]):
            if self.first_day <= datetime.fromisoformat(milestone["estimated_finish"]) <= self.last_day:
                milestonethismonth.append(milestone)
        for milestone in milestonethismonth:
            print(f"{milestone['name']} \t {milestone['estimated_finish']}")
            for userstory in milestone["user_stories"]:
                id = userstory["id"]
                userstory = self.taiga.getUserStory(id)
                if userid in userstory["assigned_users"]:
                    point_total += userstory["total_points"] / len(userstory["assigned_users"])
                    print(f"\t{userstory['subject']} \t {userstory['total_points'] / len(userstory['assigned_users'])}")
        print(f"Total points: {point_total}")
        self.overall_points += point_total
        return point_total
    
    def printUsersMilstone(self, users):
        for user in users:
            self.allUsersPoints[user['id']] = 0
            print("=====================================")
            print("Calculating points for user: " + user["full_name"])
            for project in self.projects:
                self.allUsersPoints[user['id']] += self.printMilestones(project, user['id'])
            print(f"{user['full_name']} total points: {self.allUsersPoints[user['id']]}")




if __name__ == "__main__":
    if (HOST is None or USERNAME is None):
        print("Please set the following in your .env file: HOST, USERNAME")
        exit(1)
    if (PASSWORD == "" or PASSWORD is None):
        PASSWORD = getpass.getpass("Please enter your password: ")
    
    taiga = TaigaInterface(USERNAME, PASSWORD)
    ui = UserInterface(taiga)
    projects = taiga.getProjectList()
    users = taiga.getUsers()
    print("=====================================")
    for user in users:
        print(f"{user['id']} : {user['full_name']}")
    
    ignored_users = input("Please enter the user id you want to ignore sperated by coma: ")
    ignored_users = [int(x) for x in ignored_users.split(",")]
    users = [user for user in users if user['id'] not in ignored_users]
    
    ui.printUsersMilstone(users)

    print("=====================================")
    print("Summary: ")
    with open("summary.csv", "w") as f:
        f.write("Name,Points\n")
        for user in users:
            f.write(f"{user['full_name']}: {ui.allUsersPoints[user['id']]}\n")
    print(f"Overall points: {ui.overall_points}")
    print("Output saved to summary.csv")
