
import datetime
import sys

d = datetime.date.today()
target = d - datetime.timedelta(days=90)

while d > target:
    d = d - datetime.timedelta(days=1)
    if d.weekday() < 5:
        print d.strftime('%Y%m%d')
        
    
