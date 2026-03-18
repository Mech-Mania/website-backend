import requests, json,os
from dotenv import load_dotenv

_=load_dotenv('.env')
pw:str = os.environ['ADMIN_PASSWORD']

# test updating team existance
def updateTeams(teams:list[str]):
    response=requests.post(
                    "http://127.0.0.1:8000/scoreboard/team",
                    json.dumps({"data":teams, "password":pw}), 
    )

    print(response.text)

# test updating game scores
def updateScores(teams:list[str],scores:list[int], game:str):
    response=requests.post(
                    "http://127.0.0.1:8000/scoreboard/game/score",
                    json.dumps(
                        {
                            "data":[{
                                "team":t,"score":s  
                                } for t,s in zip(teams,scores)
                            ],
                            "password":pw,
                            "game":game
                        }
                    )
    )

    print(response.text)

# test getting all scores
def getScores():
    response=requests.get(
                    "http://127.0.0.1:8000/scoreboard",
    )
    
    print(response.text)

# test getting scoreboard enable status
def getEnStatus():
    response=requests.get(
                    "http://127.0.0.1:8000/scoreboard/status"
    )
    print(response.text)

# test settings scoreboard enable status
def setEnStatus(enabled:bool):
    response=requests.post(
                    "http://127.0.0.1:8000/scoreboard/status",
                    json.dumps(
                        {
                            "password":pw,
                            "data":enabled
                        }
                    )
    )
    print(response.text)


#updateTeams(["atest","test2","tester3","test"])
'''
updateScores(
    ["atest","test2","tester3","test"],
    [0,0,0,0],
    "overall"
)
'''
#getScores()
#getEnStatus()
setEnStatus(True);
