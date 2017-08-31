# -*- coding: utf-8 -*-
"""
Created on Tue May  9 19:54:47 2017

@author: ivan
"""

import bs4 as bs
import urllib.request
import pymysql as pms
import re

url = "http://advisory.mtanyct.info/eeoutage/"
source = urllib.request.urlopen(url).read()

soup = bs.BeautifulSoup(source)

#check last update
result = re.search('Last updated: (.*?)<', str(source))
last_update = result.group(1)

#connect to db
db = pms.connect("localhost","root","","nycaccessibility")
cursor = db.cursor()

#get last db insert
try:
    cursor.execute("SELECT * FROM scrape WHERE mta_last_update= '" + last_update + "'")
    results = cursor.fetchall()
except pms.Error as e:
    print('Got error {!r}, errno is {}'.format(e, e.args[0]))

#scrape only if last mta update is different than any other recorded mta update
if len(results) == 0:
    
    #get all rows in html
    rows = soup.find_all("tr")
    
    #start counting rows
    row_id = 0
    
    for row in rows:
        columns = row.find_all("td")
        
        #there are many different columns, only the ones with 10 columns are relevant
        if len(columns) == 10:
            #a status
            status = {}        
            column_id = 0
            
            for column in columns:
                #column 0 is ADA compliance column
                if column_id == 0:
                    is_ada = column.find("img")
                    
                    if is_ada:
                        status[column_id] = 1
                    else:
                        status[column_id] = 0
                #column 3 is an image
                elif column_id == 3:
                    status[column_id] = column.find("img")['src']
                        
                #do nothing for alternate path column                
                elif column_id != 9:    
                    status[column_id] = column.get_text().strip()
                
                column_id += 1
            
            status_string = 'NOW(),' + str(status[0]);
            
            for j in range(1,9):
                status_string = status_string + ",'" + str(status[j]) + "'"
            status_string = status_string + ",'" + last_update + "'"
            
            #insert into db
            sql = "INSERT INTO scrape VALUES (" + status_string + ")"
            try:
                cursor.execute(sql)
                db.commit()
            except pms.Error as e:
                print('Got error {!r}, errno is {}'.format(e, e.args[0]))
db.close()