import os
import sys
import pprint
from dotenv import load_dotenv
from wcl import WCL
from sheets import Sheets

load_dotenv()

def getenv_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("yes", "y", "true", "1", "t")

wcl = WCL(os.getenv("WCL_ACCESS_TOKEN"))

if len(sys.argv) < 3:
    print("Missing arguments")
    print("Usage: python3 main.py <command> <warcraft log id>")
    print("Available commands:")
    print("  fetch: Fetch log and print a copy-pastable list")
    print("  sheet: Fetch log and paste into google sheet")

if sys.argv[1] == "fetch":
    result = wcl.fetch(sys.argv[2])
    wcl.printResult(
        result,
        includeHealingDone=getenv_bool("INCLUDE_HEALING_DONE"),
        includeDamageDone=getenv_bool("INCLUDE_DAMAGE_DONE")
    )

elif sys.argv[1] == "sheet":
    if len(sys.argv) < 4:
        sys.exit("Missing sheet id")

    gs = Sheets()
    sheetId = int(sys.argv[3])
    sheetName = gs.getSheetName(os.getenv("GOOGLE_SPREADHEET_ID"), sheetId)
    if sheetName == None:
        sys.exit("Could not find sheet")

    result = wcl.fetch(sys.argv[2])

    gs.enterResult(
        result,
        spreadsheetId=os.getenv("GOOGLE_SPREADHEET_ID"),
        sheetId=sheetId,
        allCell=os.getenv("GOOGLE_SHEET_ALL_CELL"),
        dpsCell=os.getenv("GOOGLE_SHEET_DPS_CELL"),
        healCell=os.getenv("GOOGLE_SHEET_HEAL_CELL"),
        tankCell=os.getenv("GOOGLE_SHEET_TANK_CELL"),
        includeHealingDone=getenv_bool("INCLUDE_HEALING_DONE"),
        includeDamageDone=getenv_bool("INCLUDE_DAMAGE_DONE")
    )

else:
    print("Unknown command: "+sys.argv[1])
