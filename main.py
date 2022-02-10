import os
import sys
import argparse
import pprint
import json
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
parser.add_argument("--config", help="Load a config from config.json")
args = parser.parse_args()

config = None
if args.config:
    with open("config.json", "r") as rf:
        configs = json.load(rf)
    config = configs[args.config]


if args.command == "fetch":

    result = wcl.fetch(
        logCode=args.code,
        endTime=args.endTime,
        tanks=args.tanks
    )

    wcl.printResult(
        result
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
        config=config
    )

    print("Success")

else:
    print("Unknown command: "+args.command)
