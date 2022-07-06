# Install Courier SDK: pip install trycourier
from trycourier import Courier
import json
from generalData import UserData
from generalData import Gender
from singleton import Singleton
from environmentProvider import EnvKeys
import environmentProvider as ep

class NotificationsProvider(metaclass=Singleton):
    def __init__(self):
      self.authToken = ep.getAttribute(EnvKeys.courier, EnvKeys.courierAuthToken)
      self.client = Courier(auth_token=self.authToken)

    def sendWelcomeMail (self, userName, userMail, password: str):
      resp = self.client.send(
        event="welcome-mail",
        recipient=userMail,
        data={
          "firstName": userName,
          "defaultPassword" : password
        },
        profile={
          "email": userMail
        }
      )

      return resp

    def sendDiscoveryDoneMail(self, notifyTo, userWhoEndedDiscoveryDetails):
      if ep.shouldSuppressNotifications():
        return

      resp = self.client.send(
        event="discoveryDoneForTeamMember",
        recipient=notifyTo,
        data={
          "teamMemberName": userWhoEndedDiscoveryDetails.firstName,
          "teamMemberGender" : "him" if userWhoEndedDiscoveryDetails.gender == Gender.MALE else "her"
        },
        profile={
          "email": notifyTo
        }
      )

      return resp

    def sendDiscoveryReminder(self, notifyToMail, notifyToName, teamManagerName):
      resp = self.client.send(
        event="discovery-done-for-team-member",
        recipient=notifyToMail,
        data={
          "userName": notifyToName,
          "userManagerName": teamManagerName
        },
        profile={
          "email": notifyToMail
        }
      )

      return resp


    def sendIssueMoovIsAboutToOverdue(self, moovOwner, moovCounterpart, moovName):
        if ep.shouldSuppressNotifications():
          return 

        resp = self.client.send(
          event="issue-moov-soon-to-overdue",
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
        return resp

    def sendConflictMoovIsAboutToOverdue(self, moovOwner, moovName):
        if ep.shouldSuppressNotifications():
          return 

        resp = self.client.send(
          event="conflict-moov-soon-overdue",
          recipient=moovOwner.mailAddress,
          data={
            "userName": moovOwner.firstName,
            "moovName" : moovName
          },
          profile={
            "email": moovOwner.mailAddress
          }
        )
        return resp

    def sendUserFeedback(self, userId, userMail, issue, text):
      if ep.shouldSupressNotificationsToAdmin():
        return
      
      recipient = ep.getAttribute(EnvKeys.feedback, EnvKeys.sendFeedbackRecipient)

      resp = self.client.send(
        event="feedback-received",
        recipient=recipient,
        data={
          "userId": userId,
          "userMail": userMail,
          "issue" : issue,
          "text" : text
        },
        profile={
          "email": recipient
        }
      )
      return resp

    def sendResetPassword(self, userName, userMail, newPassword):
      if ep.shouldSupressNotificationsToAdmin():
        return
      
      recipient = ep.getAttribute(EnvKeys.feedback, EnvKeys.sendFeedbackRecipient)

      resp = self.client.send(
        event="reset-password",
        recipient=userMail,
        data={
          "userName": userName,
          "newPassword" : newPassword
        },
        profile={
          "email": userMail
        }
      )
      return resp

    