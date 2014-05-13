# -*- coding: utf-8 -*-

import csv

#from closed_beta.models import Invitation

csv_file = open('members_Landmarker_Beta_Signup_Jul_13_2012.csv', 'r')

reader = csv.reader(csv_file)

fPass = True

for row in reader:
    if fPass:
        fPass = False
        continue
    print "Processing ...", row[0]
    if Invitation.objects.filter(email=row[0]).exists():
        pass
    else:
        u = Invitation(email=row[0])
        u.save()
