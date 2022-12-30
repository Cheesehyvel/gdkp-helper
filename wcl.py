from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import pprint

class WCL:
    def __init__(self, token):
        transport = AIOHTTPTransport(url='https://classic.warcraftlogs.com/api/v2/client', headers={'Authorization': 'Bearer '+token}, timeout=120)
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def fetch(self, logCode, endTime = 9999999999, tanks = 3):
        healCutOff = 0.03 # Minimum healing to be counted as a healer

        query = gql("""
            query ($logCode: String!, $endTime: Float!) {
                reportData {
                    report(code: $logCode) {
                        zone {
                            id
                        }
                        rankedCharacters {
                            name
                        }
                        dps: table(dataType: DamageDone, startTime: 0, endTime: $endTime, hostilityType: Friendlies)
                        healers: table(dataType: Healing, startTime: 0, endTime: $endTime, hostilityType: Friendlies)
                        tanks: table(dataType: DamageTaken, startTime: 0, endTime: $endTime, hostilityType: Friendlies)
                    }
                }
            }
        """)

        result = self.client.execute(query, {
            "logCode": logCode,
            "endTime": endTime
        })

        data = {
            "players": {
                "dps": [],
                "healers": [],
                "tanks": [],
                "all": [],
                "support": [],
            },
            "damage": 0,
            "healing": 0,
        }

        if "rankedCharacters" in result["reportData"]["report"] and result["reportData"]["report"]["rankedCharacters"]:
            for player in result["reportData"]["report"]["rankedCharacters"]:
                data["players"]["all"].append(player["name"])
        else:
            for player in result["reportData"]["report"]["dps"]["data"]["entries"]:
                if "gear" in player and len(player["gear"]):
                    data["players"]["all"].append(player["name"])

        for player in result["reportData"]["report"]["dps"]["data"]["entries"]:
            if player["name"] in data["players"]["all"]:
                data["players"]["dps"].append({
                    "name": player["name"],
                    "total": player["total"],
                    "icon": player["icon"]
                })
                data["damage"]+= player["total"]

        for player in result["reportData"]["report"]["healers"]["data"]["entries"]:
            if player["name"] in data["players"]["all"]:
                data["players"]["healers"].append({
                    "name": player["name"],
                    "total": player["total"],
                    "icon": player["icon"]
                })
                data["healing"]+= player["total"]

        tankTypes = ["Warrior", "Paladin", "Druid", "DeathKnight"]
        for player in result["reportData"]["report"]["tanks"]["data"]["entries"]:
            if player["name"] in data["players"]["all"] and player["type"] in tankTypes:
                data["players"]["tanks"].append({
                    "name": player["name"],
                    "total": player["total"],
                    "icon": player["icon"]
                })

        # Sorting
        data["players"]["dps"].sort(key=lambda x: x.get("total"), reverse=True)
        data["players"]["healers"].sort(key=lambda x: x.get("total"), reverse=True)
        data["players"]["tanks"].sort(key=lambda x: x.get("total"), reverse=True)

        # Most damage taken = Tanks
        data["players"]["tanks"] = data["players"]["tanks"][:tanks]

        # Healers
        def filterHealers(p):
            if p["total"] / data["healing"] < healCutOff:
                return False
            if p["icon"] == "Priest-Shadow":
                return False
            return True
        data["players"]["healers"] = list(filter(filterHealers, data["players"]["healers"]))

        # DPS
        def filterDps(p):
            for h in data["players"]["healers"]:
                if p["name"] == h["name"]:
                    return False
            for t in data["players"]["tanks"]:
                if p["name"] == t["name"]:
                    return False
            return True
        data["players"]["dps"] = list(filter(filterDps, data["players"]["dps"]))

        # Support
        for player in data["players"]["dps"]:
            if player["icon"] == "Priest-Shadow":
                data["players"]["support"].append({
                    "name": player["name"],
                    "type": "sp",
                    "title": "SP",
                })
            if player["icon"] == "Shaman-Enhancement":
                data["players"]["support"].append({
                    "name": player["name"],
                    "type": "enh",
                    "title": "Enh",
                })
            if player["icon"] == "Shaman-Elemental":
                data["players"]["support"].append({
                    "name": player["name"],
                    "type": "ele",
                    "title": "Ele",
                })
            if player["icon"] == "Paladin-Retribution":
                data["players"]["support"].append({
                    "name": player["name"],
                    "type": "ret",
                    "title": "Ret",
                })
        for player in data["players"]["healers"]:
            if player["icon"] == "Paladin-Holy":
                data["players"]["support"].append({
                    "name": player["name"],
                    "type": "hpal",
                    "title": "Hpal",
                })

        return data

    def highestEntry(self, entries, key="total"):
        re = None
        for entry in entries:
            if re == None or entry[key] > re[key]:
                re = entry
        return re

    def printResult(self, data):
        print("Healers")
        for player in data["players"]["healers"]:
            print(player["name"]+"\t"+str(player["total"]))
        print(" ")

        print("Tanks")
        for player in data["players"]["tanks"]:
            print(player["name"])
        print(" ")

        print("DPS")
        for player in data["players"]["dps"]:
            print(player["name"]+"\t"+str(player["total"]))
        print(" ")

        print("Support")
        for player in data["players"]["support"]:
            print(player["type"]+": "+player["name"])
        print(" ")

        print("All")
        for player in data["players"]["all"]:
            print(player)