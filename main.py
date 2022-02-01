import os
import sys
import argparse
import pprint
from dotenv import load_dotenv
from wcl import WCL
from sheets import Sheets

load_dotenv()

def getenv_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("yes", "y", "true", "1", "t")

wcl = WCL(os.getenv("WCL_ACCESS_TOKEN"))

parser = argparse.ArgumentParser()
parser.add_argument("command", help="Command to run (fetch/sheet)")
parser.add_argument("code", help="Warcraft logs id")
parser.add_argument("--sheet", help="Google sheet id", type=int)
parser.add_argument("--endTime", help="Set endtime for log", type=float, default=9999999999)
parser.add_argument("--tanks", help="Set number of tanks", type=int, default=3)
args = parser.parse_args()

if args.command == "fetch":

    result = wcl.fetch(
        logCode=args.code,
        endTime=args.endTime,
        tanks=args.tanks
    )

    wcl.printResult(
        result,
        includeHealingDone=getenv_bool("INCLUDE_HEALING_DONE"),
        includeDamageDone=getenv_bool("INCLUDE_DAMAGE_DONE")
    )

elif args.command == "sheet":
    if args.sheet == None:
        sys.exit("Missing sheet id")

    gs = Sheets()
    sheetName = gs.getSheetName(os.getenv("SPREADHEET_ID"), args.sheet)
    if sheetName == None:
        sys.exit("Could not find sheet")

    result = wcl.fetch(
        logCode=args.code,
        endTime=args.endTime,
        tanks=args.tanks
    )

    gs.enterResult(
        result,
        spreadsheetId=os.getenv("SPREADHEET_ID"),
        sheetId=args.sheet,
        allCell=os.getenv("SHEET_CELL_ALL"),
        dpsCell=os.getenv("SHEET_CELL_DPS"),
        healCell=os.getenv("SHEET_CELL_HEAL"),
        tankCell=os.getenv("SHEET_CELL_TANK"),
        supportCell=os.getenv("SHEET_CELL_SUPPORT"),
        cuts={
            "sp": os.getenv("SHEET_CUT_SP"),
            "ff": os.getenv("SHEET_CUT_FF"),
            "cor": os.getenv("SHEET_CUT_COR"),
            "coe": os.getenv("SHEET_CUT_COE"),
            "enh": os.getenv("SHEET_CUT_ENH"),
            "ele": os.getenv("SHEET_CUT_ELE"),
            "ret": os.getenv("SHEET_CUT_RET"),
            "hpal": os.getenv("SHEET_CUT_HPAL"),
            "mtank": os.getenv("SHEET_CUT_MTANK"),
            "wtank": os.getenv("SHEET_CUT_WTANK"),
        },
        includeHealingDone=getenv_bool("INCLUDE_HEALING_DONE"),
        includeDamageDone=getenv_bool("INCLUDE_DAMAGE_DONE")
    )

    print("Success")

else:
    print("Unknown command: "+args.command)
