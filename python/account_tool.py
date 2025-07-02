#!/usr/bin/python3

#FAQ/Cheatsheet
# How Do I remove legal holds from a list of graduated students? use LEGAL + GRADS
# How Do I remove graduated students that are now faculty/staff? use DIFF + GRADS
# How Do I remove legal holds from Deactivations (Can be Students or Fac/Staff)? use LEGAL + DEACT 
# What does DIFF + DEACT do? Nothing

import csv
import re
import argparse
import sys

parser = argparse.ArgumentParser(description="CI Multi Tool for batch account deletions.", epilog="If you do not understand the requirements of each function, read the comment above the function.")
parser.add_argument("-f1", "--file1", help="First file to compare", required=True)
parser.add_argument("-f2", "--file2", help="Second file to compare", required=True)
parser.add_argument("-m", "--mode", help="Processing Mode: Legal hold processing or graduated students processing", required=True, choices=["legal", "diff"])
parser.add_argument("-t", "--type", help="Processing Type: Deactivations or Graduated students", required=True, choices=["deact", "grads"])
args = parser.parse_args()

pattern = r'\@[a-zA-z0-9]*.*'

#This function requires the deactivation script output and a list of usernames
#These should all be in CSV format even if they have 1 column
#Column header is optional
#For the deactivation file
#Reached by using LEGAL + DEACT option
def legal_hold_deactivations(f1, f2):
    with open(f1, "r") as legalf, open(f2, "r") as deactf:
        legal = list(csv.reader(legalf))
        deact = list(csv.reader(deactf))
        output = deact

        for email in legal:
            for user in deact:
                res = email[2].split("@")[0]
                if res == user[0]:
                    print("LEGAL HOLD FOUND: " + user[0])
                    output.remove(user)

        f = open("deact_with_holds_removed.csv", "w")
        print("writing file to file \"deact_with_holds_removed.csv\"")
        for row in output:
            f.write(",".join(row) + "\n")
        f.close()
    return

#This function requires the legal hold list and a list of graduated student usernames
#The student list must be usernames only, or if there are more columns, username MUST BE COLUMN 0
#Unfortunately we cannot rely on the student list to have a consistent format each time we get it, so we must format it manually
#These should all be in CSV format even if they have 1 column
#Column header is optional
#Reached by using LEGAL + GRADS option
#Export legal hold list from Vault
def legal_hold_graduates(f1, f2):
    with open(f1, "r") as legalf, open(f2, "r") as gradf:
        legal = list(csv.reader(legalf))
        grad = list(csv.reader(gradf))
        output = grad

        for email in legal:
            for user in grad:
                res = email[2].split("@")[0]
                if res == user[0]:
                    print("LEGAL HOLD FOUND: " + user[0])
                    output.remove(user)

        f = open("graduates_with_holds_removed.csv", "w")
        print("writing file to file \"graduates_with_holds_removed.csv\"")
        for row in output:
            f.write(",".join(row) + "\n")
        f.close()
    return




#This function requires an export of Faculty/Staff from AD, compared to a list of usernames of graduated students
# Get-ADUser -Filter * -SearchBase "ou=Staff-Faculty,dc=trinity,dc=local" -Properties "Name", "mail", "passwordlastset", "msDS-UserPasswordExpiryTimeComputed" | Select-Object -Property "Name","mail","passwordlastset",@{Name="ExpiryDate";Expression={[datetime]::FromFileTime($_."msDS-UserPasswordExpiryTimeComputed")}} | export-csv ~\Desktop\facstaff.csv
#These should be in CSV format even if they have 1 column
#Column header is REQUIRED for the faculty/staff file
#Reached by using DIFF + GRADS option
def diff_grads_from_facstaff(f1, f2):
    with open(f1, "r") as facf, open(f2, "r") as gradf:
        facstaff = csv.DictReader(facf)
        grads = list(csv.reader(gradf))
        output = grads

        for fac in facstaff:
            for grad in grads:
                if fac['Name'] == grad[0]:
                    print("Student to Staff/Faculty found: " + grad[0])
                    output.remove(grad)

        f = open("grads_staff_removed.csv", "w")
        print("writing file to file \"grads_staff_removed.csv\"")
        for row in output:
            f.write(",".join(row) + "\n")
        f.close()
    return

if __name__ == "__main__":
    if args.mode == "legal":
        if args.type == "deact":
            answer = input("You have selected legal hold deactivations. Did you specify the legal hold as FILE 1? [y/n] ")
            if answer.lower() == "y":
                legal_hold_deactivations(args.file1, args.file2)
            else:
                legal_hold_deactivations(args.file2, args.file1)
        if args.type == "grads":
            answer = input("You have selected legal hold graduating students. Did you specify the legal hold as FILE 1? [y/n] ")
            if answer.lower() == "y":
                legal_hold_graduates(args.file1, args.file2)
            else:
                legal_hold_graduates(args.file2, args.file1)
    if args.mode == "diff":
        if args.type == "grads":
            answer = input("You have selected diff between grads and facstaff. Did you specify FAC/STAFF as FILE 1? [y/n] ")
            if answer.lower() == "y":
                diff_grads_from_facstaff(args.file1, args.file2)
            else:
                diff_grads_from_facstaff(args.file2, args.file1)
        if args.type == "deact":
            print("invalid selection")
            sys.exit(0)


# with open("legal_hold_removed.csv") as legalf, open("M365-exportUsers_2025-6-5-DirSynced.csv") as m365f:
#     legal = list(csv.reader(legalf))
#     m365 = list(csv.reader(m365f))

#     pattern = r'\@[a-zA-z0-9]*.*'

#     for l in legal:
#         for m in m365:
#             res = m[3].split("@")[0]
#             if l[0] == res:
#                 print(l[0])

# with open("zoomus_users.csv", "r") as zoom_f, open("emails.csv", "r") as email_f:
#     zoom = list(csv.reader(zoom_f))
#     emails = list(csv.reader(email_f))
#     final = set()
#     zoom_strings = [''.join(ele) for ele in zoom]
#     email_strings = [''.join(ele) for ele in emails]

#     for e in email_strings:
#         #res = any(e in sublist for sublist in zoom_strings)
#         if e not in zoom_strings:
#             final.add(e)
            
    
#     for e in final:
#         print(e)

