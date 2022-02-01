from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import pprint

class WCL:
    def __init__(self, token):
        transport = AIOHTTPTransport(url='https://classic.warcraftlogs.com/api/v2/client', headers={'Authorization': 'Bearer '+token}, timeout=120)
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def fetch(self, logCode):
        nTanks = 3
        healCutOff = 0.02 # Minimum healing to be counted as a healer

        query = gql("""
            query ($logCode: String!) {
                reportData {
                    report(code: $logCode) {
                        rankedCharacters {
                            name
                        }
                        dps: table(dataType: DamageDone, startTime: 0, endTime: 9999999999, hostilityType: Friendlies)
                        healers: table(dataType: Healing, startTime: 0, endTime: 9999999999, hostilityType: Friendlies)
                        tanks: table(dataType: DamageTaken, startTime: 0, endTime: 9999999999, hostilityType: Friendlies)
                        ff: table(dataType: Casts, abilityID: 26993, startTime: 0, endTime: 9999999999, hostilityType: Friendlies)
                        coe: table(dataType: Casts, abilityID: 27228, startTime: 0, endTime: 9999999999, hostilityType: Friendlies)
                        cor: table(dataType: Casts, abilityID: 27226, startTime: 0, endTime: 9999999999, hostilityType: Friendlies)
                    }
                }
            }
        """)

        result = self.client.execute(query, {
            "logCode": logCode,
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

        for player in result["reportData"]["report"]["tanks"]["data"]["entries"]:
            if player["name"] in data["players"]["all"]:
                data["players"]["tanks"].append({
                    "name": player["name"],
                    "total": player["total"],
                    "icon": player["icon"]
                })

        # Faerie fire
        name = self.mostCasts(result["reportData"]["report"]["ff"]["data"]["entries"])
        if name:
            data["players"]["support"].append({
                "name": name,
                "type": "ff",
                "title": "Faerie Fire",
            })

        # CoE
        name = self.mostCasts(result["reportData"]["report"]["coe"]["data"]["entries"])
        if name:
            data["players"]["support"].append({
                "name": name,
                "type": "coe",
                "title": "Curse of Elements",
            })

        # CoR
        name = self.mostCasts(result["reportData"]["report"]["cor"]["data"]["entries"])
        if name:
            data["players"]["support"].append({
                "name": name,
                "type": "cor",
                "title": "Curse of Recklessness",
            })

        # Sorting
        data["players"]["dps"].sort(key=lambda x: x.get("total"), reverse=True)
        data["players"]["healers"].sort(key=lambda x: x.get("total"), reverse=True)
        data["players"]["tanks"].sort(key=lambda x: x.get("total"), reverse=True)

        # Most damage taken = Tanks
        data["players"]["tanks"] = data["players"]["tanks"][:nTanks]

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
                    "title": "Shadow priest",
                })
            if player["icon"] == "Shaman-Enhancement":
                data["players"]["support"].append({
                    "name": player["name"],
                    "type": "enh",
                    "title": "Enhancement",
                })
            if player["icon"] == "Shaman-Elemental":
                data["players"]["support"].append({
                    "name": player["name"],
                    "type": "ele",
                    "title": "Elemental",
                })
            if player["icon"] == "Paladin-Retribution":
                data["players"]["support"].append({
                    "name": player["name"],
                    "type": "ret",
                    "title": "Ret paladin",
                })
        for player in data["players"]["healers"]:
            if player["icon"] == "Paladin-Holy":
                data["players"]["support"].append({
                    "name": player["name"],
                    "type": "hpal",
                    "title": "Holy paladin",
                })

        return data

    def mostCasts(self, players):
        name = ""
        n = 0
        for player in players:
            if player["total"] > n:
                name = player["name"]
                n = player["total"]
        if n:
            return name
        return None

    def printResult(self, data, includeHealingDone=True, includeDamageDone=True):
        print("Healers")
        for player in data["players"]["healers"]:
            if includeHealingDone:
                print(player["name"]+"\t"+str(player["total"]))
            else:
                print(player["name"])
        print(" ")

        print("Tanks")
        for player in data["players"]["tanks"]:
            print(player["name"])
        print(" ")

        print("DPS")
        for player in data["players"]["dps"]:
            if includeDamageDone:
                print(player["name"]+"\t"+str(player["total"]))
            else:
                print(player["name"])
        print(" ")

        print("Support")
        for player in data["players"]["support"]:
            print(player["type"]+": "+player["name"])
        print(" ")

        print("All")
        for player in data["players"]["all"]:
            print(player)