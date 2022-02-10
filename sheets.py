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

    def enterResult(self, result, spreadsheetId, sheetId, config):
        data = []

        sheetName = self.getSheetName(spreadsheetId, sheetId)

        if self.hasCell(config, "all_names") and len(result["players"]["all"]) > 0:
            startCell = config["cells"]["all_names"]
            endCell = self.incrementRow(startCell, len(result["players"]["all"])-1)
            d = {
                "range": "'"+sheetName+"'!"+startCell+":"+endCell,
                "values": []
            }
            for player in result["players"]["dps"]:
                d["values"].append([player["name"]])
            for player in result["players"]["healers"]:
                d["values"].append([player["name"]])
            for player in result["players"]["tanks"]:
                d["values"].append([player["name"]])
            data.append(d);

        if self.hasCell(config, "dps_names") and len(result["players"]["dps"]) > 0:
            startCell = config["cells"]["dps_names"]
            endCell = self.incrementRow(startCell, len(result["players"]["dps"])-1)
            d = {
                "range": "'"+sheetName+"'!"+startCell+":"+endCell,
                "values": []
            }
            for player in result["players"]["dps"]:
                d["values"].append([player["name"]])
            data.append(d);

        if self.hasCell(config, "dps_amounts") and len(result["players"]["dps"]) > 0:
            startCell = config["cells"]["dps_amounts"]
            endCell = self.incrementRow(startCell, len(result["players"]["dps"])-1)
            d = {
                "range": "'"+sheetName+"'!"+startCell+":"+endCell,
                "values": []
            }
            for player in result["players"]["dps"]:
                d["values"].append([player["total"]])
            data.append(d);

        if self.hasCell(config, "healer_names") and len(result["players"]["healers"]) > 0:
            startCell = config["cells"]["healer_names"]
            endCell = self.incrementRow(startCell, len(result["players"]["healers"])-1)
            d = {
                "range": "'"+sheetName+"'!"+startCell+":"+endCell,
                "values": []
            }
            for player in result["players"]["healers"]:
                d["values"].append([player["name"]])
            data.append(d);

        if self.hasCell(config, "healer_amounts") and len(result["players"]["healers"]) > 0:
            startCell = config["cells"]["healer_amounts"]
            endCell = self.incrementRow(startCell, len(result["players"]["healers"])-1)
            d = {
                "range": "'"+sheetName+"'!"+startCell+":"+endCell,
                "values": []
            }
            for player in result["players"]["healers"]:
                d["values"].append([player["total"]])
            data.append(d);

        if self.hasCell(config, "tank_names") and len(result["players"]["tanks"]) > 0:
            startCell = config["cells"]["tank_names"]
            endCell = self.incrementRow(startCell, len(result["players"]["tanks"])-1)
            d = {
                "range": "'"+sheetName+"'!"+startCell+":"+endCell,
                "values": []
            }
            for player in result["players"]["tanks"]:
                d["values"].append([player["name"]])
            data.append(d);

        if self.hasCell(config, "support_names") and len(result["players"]["support"]) > 0:
            startCell = config["cells"]["support_names"]
            endCell = self.incrementRow(startCell, len(result["players"]["support"])-1)
            d = {
                "range": "'"+sheetName+"'!"+startCell+":"+endCell,
                "values": []
            }
            for player in result["players"]["support"]:
                d["values"].append([player["name"]])
            data.append(d)

            if self.hasCell(config, "support_titles"):
                startCell = config["cells"]["support_titles"]
                endCell = self.incrementRow(startCell, len(result["players"]["support"])-1)
                d = {
                    "range": "'"+sheetName+"'!"+startCell+":"+endCell,
                    "values": []
                }
                for player in result["players"]["support"]:
                    d["values"].append([player["title"]])
                data.append(d)

            if self.hasCell(config, "support_cuts") and "cuts" in config:
                startCell = config["cells"]["support_cuts"]
                endCell = self.incrementRow(startCell, len(result["players"]["support"])-1)
                d = {
                    "range": "'"+sheetName+"'!"+startCell+":"+endCell,
                    "values": []
                }
                for player in result["players"]["support"]:
                    if player["type"] in config["cuts"]:
                        d["values"].append([str(config["cuts"][player["type"]]).replace(".", ",")+"%"])
                data.append(d)

        response = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheetId,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": data
            }
        ).execute()

        return response

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

    def hasCell(self, config, cell):
        return config and "cells" in config and cell in config["cells"]
