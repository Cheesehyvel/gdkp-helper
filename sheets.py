from googleapiclient import discovery
from google.oauth2.credentials import Credentials
import os.path
from pprint import pprint

class Sheets:
    def __init__(self):
        if os.path.exists("google/token.json"):
            credentials = Credentials.from_authorized_user_file("google/token.json", ["https://www.googleapis.com/auth/spreadsheets"])
        else:
            raise Exception("Missing google credentials. Run oauth.py inside google directory.")

        self.service = discovery.build("sheets", "v4", credentials=credentials)

    def copyAndEnter(self, result, spreadsheetId, sheetId):
        print("copy and enter")

    def enterResult(self, result, spreadsheetId, sheetId, allCell="", dpsCell="", healCell="", tankCell="", includeHealingDone=False, includeDamageDone=False):
        data = []

        sheetName = self.getSheetName(spreadsheetId, sheetId)

        if len(allCell) > 0 and len(result["players"]["all"]) > 0:
            d = {
                "range": "'"+sheetName+"'!"+allCell+":"+self.incrementRow(allCell, len(result["players"]["all"])-1),
                "values": []
            }
            for player in result["players"]["dps"]:
                d["values"].append([player["name"]])
            for player in result["players"]["healers"]:
                d["values"].append([player["name"]])
            for player in result["players"]["tanks"]:
                d["values"].append([player["name"]])
            data.append(d);

        if len(dpsCell) > 0 and len(result["players"]["dps"]) > 0:
            endCell = self.incrementRow(dpsCell, len(result["players"]["dps"])-1)
            if includeDamageDone:
                endCell = self.incrementColumn(endCell)
            d = {
                "range": "'"+sheetName+"'!"+dpsCell+":"+endCell,
                "values": []
            }
            for player in result["players"]["dps"]:
                if includeDamageDone:
                    d["values"].append([player["name"], player["total"]])
                else:
                    d["values"].append([player["name"]])
            data.append(d);

        if len(healCell) > 0 and len(result["players"]["healers"]) > 0:
            endCell = self.incrementRow(healCell, len(result["players"]["healers"])-1)
            if includeHealingDone:
                endCell = self.incrementColumn(endCell)
            d = {
                "range": "'"+sheetName+"'!"+healCell+":"+endCell,
                "values": []
            }
            for player in result["players"]["healers"]:
                if includeHealingDone:
                    d["values"].append([player["name"], player["total"]])
                else:
                    d["values"].append([player["name"]])
            data.append(d);

        if len(tankCell) > 0 and len(result["players"]["tanks"]) > 0:
            endCell = self.incrementRow(tankCell, len(result["players"]["tanks"])-1)
            d = {
                "range": "'"+sheetName+"'!"+tankCell+":"+endCell,
                "values": []
            }
            for player in result["players"]["tanks"]:
                d["values"].append([player["name"]])
            data.append(d);

        response = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheetId,
            body={
                "valueInputOption": "RAW",
                "data": data
            }
        ).execute()

        pprint(response)

    def copySheet(self, spreadsheetId, sheetId):
        request = self.service.spreadsheets().sheets().copyTo(
            spreadsheetId=spreadsheetId,
            sheetId=sheetId,
            body={
                "destination_spreadsheet_id": spreadsheetId
            }
        )

        response = request.execute();

        return response

    def getSheetName(self, spreadsheetId, sheetId):
        request = self.service.spreadsheets().get(spreadsheetId=spreadsheetId)
        response = request.execute()

        for sheet in response["sheets"]:
            if sheet["properties"]["sheetId"] == sheetId:
                return sheet["properties"]["title"]

        return None

    def incrementRow(self, cell, increment = 1):
        col = cell[:1]
        num = int(cell[1:])
        return col+str(num+increment)

    def incrementColumn(self, cell, increment = 1):
        col = cell[:1]
        num = cell[1:]
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        index = chars.find(col)
        col = chars[index+increment]
        return col+num
