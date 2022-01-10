# Install Courier SDK: pip install trycourier
from trycourier import Courier
import json

def example (auth_token): 
  client = Courier(auth_token=auth_token)

  resp = client.send(
    event="courier-quickstart",
    recipient="claro.platform@gmail.com",
    data={
      "favoriteAdjective": "awesomeness"
    },
    profile={
      "email": "claro.platform@gmail.com"
    }
  )

def sendWelcomeMail (auth_token):
  client = Courier(auth_token=auth_token)

  resp = client.send(
    event="welcome-mail",
    recipient="shaul.ben.maor@gmail.com",
    data={
      "firstName": "Shaul",
      "defaultPassword" : "123456"
    },
    profile={
      "email": "shaul.ben.maor@gmail.com"
    }
  )

def sendDiscoveryDoneMail(auth_token):
    client = Courier(auth_token=auth_token)

    resp = client.send(
      event="discoveryDoneForTeamMember",
      recipient="smadar@connaction.team",
      data={
        "teamMemberName": "Shaul",
        "teamMemberGender" : "him"
      },
      profile={
        "email": "smadar@connaction.team"
      }
    )

def main():
  
  infra_file = open("c:\\dev\\data\\env\\env.json")

  infra_details = json.load (infra_file)

  auth_token = infra_details["courier"]["token"]

  # sendWelcomeMail(auth_token)
  sendDiscoveryDoneMail(auth_token)

if __name__ == '__main__':
  main()
