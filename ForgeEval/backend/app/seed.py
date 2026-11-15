from sqlalchemy import select
from app.core.db import Base, engine, SessionLocal
from app.models import Challenge

CHALLENGES = [
 {"slug":"two-sum","title":"Two Sum","description":"Given an integer array nums and an integer target, return the indices of two numbers that add up to target. Print the two indices separated by a space. Indices are zero-based.","difficulty":"Easy","tags":["arrays","hash-map"],"starter_code":{"python":"nums = list(map(int, input().split()))\ntarget = int(input())\n# print two indices\n","javascript":"const fs = require('fs');\nconst lines = fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n// first n values, then target\n","java":"import java.util.*;\npublic class Main { public static void main(String[] args) { } }"},"tests":[{"input":"2 7 11 15\n9\n","expected":"0 1"},{"input":"3 2 4\n6\n","expected":"1 2"}]},
 {"slug":"reverse-string","title":"Reverse a String","description":"Read one line and print its characters in reverse order.","difficulty":"Easy","tags":["strings"],"starter_code":{"python":"s = input()\nprint(s[::-1])\n","javascript":"const fs=require('fs'); console.log(fs.readFileSync(0,'utf8').trim().split('').reverse().join(''));","java":"import java.util.*; public class Main { public static void main(String[] a) { Scanner s=new Scanner(System.in); System.out.println(new StringBuilder(s.nextLine()).reverse()); } }"},"tests":[{"input":"forgeeval\n","expected":"laveegro f".replace(" ","")},{"input":"hello\n","expected":"olleh"}]}
]

def seed():
 Base.metadata.create_all(bind=engine)
 with SessionLocal() as db:
  for item in CHALLENGES:
   if not db.scalar(select(Challenge).where(Challenge.slug==item["slug"])):
    db.add(Challenge(**item))
  db.commit()
if __name__ == "__main__": seed()
