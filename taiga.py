import json
import requests_cache

requests = requests_cache.CachedSession('demo_cache')


class TaigaInterface:
    def __init__(self, username, password, apiurl):
        self.API_URL = apiurl
        self.user = self.login(username, password)
        self.auth_token = self.user["auth_token"]

    def login(self, username, password) -> dict:
        print("Logging in...")
        # login to the api
        response = requests.post(f"{self.API_URL}/auth", json={"username": username, "password": password, "type": "normal"})
        # return the token
        if response.status_code != 200:
            print(response.json())
            exit(1)
        print("Login successful!")
        return {"auth_token": response.json()["auth_token"], "refresh": response.json()["refresh"], "full_name": response.json()["full_name"], "id": response.json()["id"]}
    
    def getProjectList(self):
        resp = requests.get(f"{self.API_URL}/projects", headers={"Authorization": f"Bearer {self.auth_token}"})
        if resp.status_code != 200:
            print(resp.json())
        return resp.json()

    def getProject(self, project_id):
        resp = requests.get(f"{self.API_URL}/projects/{project_id}", headers={"Authorization": f"Bearer {self.auth_token}"})
        if resp.status_code != 200:
            print(resp.json())
        return resp.json()

    def listMilestoneByProject(self, project_id, closed=None):
        if closed is None:
            resp = requests.get(f"{self.API_URL}/milestones?project={project_id}", headers={"Authorization": f"Bearer {self.auth_token}"})
        else:
            resp = requests.get(f"{self.API_URL}/milestones?project={project_id}&closed={closed}", headers={"Authorization": f"Bearer {self.auth_token}"})
        if resp.status_code != 200:
            print(resp.json())
        return resp.json()

    def getUserStory(self, userstory_id):
        resp = requests.get(f"{self.API_URL}/userstories/{userstory_id}", headers={"Authorization": f"Bearer {self.auth_token}"})
        if resp.status_code != 200:
            print(resp.json())
        return resp.json()
    def getUsers(self):
        resp = requests.get(f"{self.API_URL}/users",  headers={"Authorization": f"Bearer {self.auth_token}"})
        if resp.status_code != 200:
            print(resp.json())
        userlist = resp.json()

        self.users = []
        for user in userlist:
            self.users.append({"id": user["id"], "full_name": user["full_name"]})
        return self.users
    
    def getLastOpenedMilestone(self, project_id):
        milestones = self.listMilestoneByProject(project_id, closed=False)
        if len(milestones) == 0:
            return None
        return milestones[0]
    
    def summaryLastMilestone(self, project_id):
        milestone = self.getLastOpenedMilestone(project_id)
        print(milestone['id'])
        userstories = requests.get(f"{self.API_URL}/userstories?milestone={milestone['id']}&project={project_id}", headers={"Authorization": f"Bearer {self.auth_token}"})
        userstories = userstories.json()
        summary = {}
        
        for userstory in userstories:
            asigned_user = userstory["assigned_users"]
            point_each = userstory["total_points"] / len(asigned_user)

            for user in asigned_user:
                if user in summary:
                    summary[user] += point_each
                else:
                    summary[user] = point_each
            
        return summary
                

    def getUserStoriesByMilestone(self, milestone_id):
        resp = requests.get(f"{self.API_URL}/userstories?milestones={milestone_id}", headers={"Authorization": f"Bearer {self.auth_token}"})

        if resp.status_code != 200:
            print(resp.json())
        return resp.json()


     

if __name__ == "__main__":
    import os
    import getpass
    from dotenv import load_dotenv
    
    load_dotenv()

    # initiate the taiga interface
    USERNAME = os.environ.get('TAIGA_USERNAME')
    PASSWORD = getpass.getpass("Password: ")
    HOST = os.environ.get('HOST')
    API_URL = f"{HOST}/api/v1"

    taiga = TaigaInterface(USERNAME, PASSWORD, API_URL)

    print(taiga.summaryLastMilestone(10))

