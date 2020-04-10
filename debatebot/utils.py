# Features of the Bot
#
import roles

String command = input.read()
String user = self.getUser()

if user.hasPermission: #checks role: if admin or adjudicator

    if command == "!help":
        print("Help...")
    elif command == "!createrooms":
        createrooms()
    elif command == "!connecttabbycat":
        connecttabbycat()
    else:
        print("error")
#
#
#
#
