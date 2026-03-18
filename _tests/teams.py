import requests, json,os
from dotenv import load_dotenv

_=load_dotenv('.env')
pw:str = os.environ['ADMIN_PASSWORD']


def updateTeams(teams:list[str]):
    response=requests.post(
                    "http://127.0.0.1:8000/scoreboard/team/update",
                    json.dumps({"data":teams, "password":pw}), 
    )

    print(response.text)


updateTeams(["atest","test2","tester3","test"])
