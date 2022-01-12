# Install Courier SDK: pip install trycourier
from trycourier import Courier
import json
from generalData import UserData
from generalData import Gender
from singleton import Singleton
from environmentProvider import EnvironmentProvider, EnvKeys
import environmentProvider as ep

class NotificationsProvider(metaclass=Singleton):
    def __init__(self):
      self.authToken = ep.getAttribute(EnvKeys.courier, EnvKeys.courierAuthToken)
      self.client = Courier(auth_token=self.authToken)

    def sendWelcomeMail (self, userDetails : UserData):
      if ep.shouldSuppressNotifications():
        return

      resp = self.client.send(
        event="welcome-mail",
        recipient=userDetails.mailAddress,
        data={
          "firstName": userDetails.firstName,
          "defaultPassword" : ep.getAttribute(EnvKeys.defaults, EnvKeys.initialUserPassword)
        },
        profile={
          "email": userDetails.mailAddress
        }
      )

    def sendDiscoveryDoneMail(self, notifyTo, userWhoEndedDiscoveryDetails):
      if ep.shouldSuppressNotifications:
        return

      resp = self.client.send(
        event="discoveryDoneForTeamMember",
        recipient=notifyTo.mailAddress,
        data={
          "teamMemberName": userWhoEndedDiscoveryDetails.firstName,
          "teamMemberGender" : "him" if userWhoEndedDiscoveryDetails.gender == Gender.MALE else "her"
        },
        profile={
          "email": notifyTo.mailAddress
        }
      )

    def sendIssueMoovIsAboutToOverdue(self, moovOwner, moovCounterpart, moovName):
        if ep.shouldSuppressNotifications:
          return 

        resp = self.client.send(
          event="moov-soon-to-overdue",
          recipient=moovOwner.mailAddress,
          data={
            "userName": moovOwner.firstName,
            "counterpartName" : moovCounterpart.firstName,
            "moovName" : moovName
          },
          profile={
            "email": moovOwner.mailAddress
          }
        )

    def sendConflictMoovIsAboutToOverdue(self, moovOwner, moovName):
        if ep.shouldSuppressNotifications:
          return 

        resp = self.client.send(
          event="moov-soon-to-overdue",
          recipient=moovOwner.mailAddress,
          data={
            "userName": moovOwner.firstName,
            "moovName" : moovName
          },
          profile={
            "email": moovOwner.mailAddress
          }
        )