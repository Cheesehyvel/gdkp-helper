from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import pprint

class WCL:
    def __init__(self, token):
        transport = AIOHTTPTransport(url='https://classic.warcraftlogs.com/api/v2/client', headers={'Authorization': 'Bearer '+token}, timeout=120)
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def fetch(self, logCode, endTime = 9999999999, tanks = 3):
        healCutOff = 0.05 # Minimum healing to be counted as a healer

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
                        ff: table(dataType: Casts, abilityID: 26993, startTime: 0, endTime: $endTime, hostilityType: Friendlies)
                        coe: table(dataType: Casts, abilityID: 27228, startTime: 0, endTime: $endTime, hostilityType: Friendlies)
                        cor: table(dataType: Casts, abilityID: 27226, startTime: 0, endTime: $endTime, hostilityType: Friendlies)
                        mtankIllidari: table(dataType: DamageTaken, encounterID: 608, abilityID: 41483, startTime: 0, endTime: $endTime, hostilityType: Friendlies)
                        ltankLeo: table(dataType: DamageTaken, encounterID: 625, abilityID: 37675, startTime: 0, endTime: $endTime, hostilityType: Friendlies)
                        #ltankKT: table(dataType: DamageTaken, encounterID: 733, abilityID: 36971, startTime: 0, endTime: $endTime, hostilityType: Friendlies)
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

        for player in result["reportData"]["report"]["rankedCharacters"]:
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

        tankTypes = ["Warrior", "Paladin", "Druid"]
        for player in result["reportData"]["report"]["tanks"]["data"]["entries"]:
            if player["name"] in data["players"]["all"] and player["type"] in tankTypes:
                data["players"]["tanks"].append({
                    "name": player["name"],
                    "total": player["total"],
                    "icon": player["icon"]
                })

        # Faerie fire
        player = self.highestEntry(result["reportData"]["report"]["ff"]["data"]["entries"])
        if player:
            data["players"]["support"].append({
                "name": player["name"],
                "type": "ff",
                "title": "FF",
            })

        # CoE
        player = self.highestEntry(result["reportData"]["report"]["coe"]["data"]["entries"])
        if player:
            data["players"]["support"].append({
                "name": player["name"],
                "type": "coe",
                "title": "CoE",
            })

        # CoR
        player = self.highestEntry(result["reportData"]["report"]["cor"]["data"]["entries"])
        if player:
            data["players"]["support"].append({
                "name": player["name"],
                "type": "cor",
                "title": "CoR",
            })

        # Mage tank on Illidari Council
        player = self.highestEntry(result["reportData"]["report"]["mtankIllidari"]["data"]["entries"])
        if player:
            data["players"]["support"].append({
                "name": player["name"],
                "type": "mtank",
                "title": "M tank"
            })

        # Warlock tank on Leotheras
        player = self.highestEntry(result["reportData"]["report"]["ltankLeo"]["data"]["entries"])
        if player and player["type"] == "Warlock":
            data["players"]["support"].append({
                "name": player["name"],
                "type": "ltank",
                "title": "Ltank"
            })

        # Warlock tank on Kael'Thas
        """
        player = self.highestEntry(result["reportData"]["report"]["ltankKT"]["data"]["entries"])
        if player and player["type"] == "Warlock":
            already_tanked = False
            for p in data["players"]["support"]:
                if p["type"] == "ltank" and p["name"] == player["name"]:
                    already_tanked = True
                    break
            if already_tanked == False:
                data["players"]["support"].append({
                    "name": player["name"],
                    "type": "ltank",
                    "title": "Ltank"
                })
                */
        """

        # Sorting
        data["players"]["dps"].sort(key=lambda x: x.get("total"), reverse=True)
        data["players"]["healers"].sort(key=lambda x: x.get("total"), reverse=True)
        data["players"]["tanks"].sort(key=lambda x: x.get("total"), reverse=True)

        # Most damage taken = Tanks
        data["players"]["tanks"] = data["players"]["tanks"][:tanks]

        # Healers
        num = 0
        for player in data["players"]["healers"]:
            if player["total"] / data["healing"] < healCutOff:
                break
            num+= 1
        data["players"]["healers"] = data["players"]["healers"][:num]

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