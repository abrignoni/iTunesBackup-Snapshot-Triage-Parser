import datetime
import argparse
from argparse import RawTextHelpFormatter
from six.moves.configparser import RawConfigParser
import sys
import ccl_bplist
import biplist
import plistlib
import io
import os
import glob
import sqlite3
from shutil import copy
from time import process_time

parser = argparse.ArgumentParser(description="\
	iTunes Backup App Snapshot Traige Parser\
	\n\n Parse an unencrypted/decrypted iTunes Backup for app snapshot images."
, prog='SnapTriage.py'
, formatter_class=RawTextHelpFormatter)
parser.add_argument('-y', action='store_true',help="Override encryption flag. Use for 3rd party decrypted backups.")
parser.add_argument('data_dir',help="Path  to the iTunes Backup Directory")

args = parser.parse_args()
data_dir = args.data_dir
override = str(args.y)


pathfound = 0
foldername = ("iTunesSnapshotTriageReports_" + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

print("\n--------------------------------------------------------------------------------------")
print("iTunes Backup App Snapshot Triage Parser.")
print("By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com")
print("Selected iTunes Backup directory: " + data_dir)
print("\n--------------------------------------------------------------------------------------")


#write plist function
def analizeplist():
	output_file = open('./'+foldername+'/ExtractedPlists/'+bundleid2+'-'+fileID+'.plist', 'wb') #export from manifest.db
	output_file.write(wbplist)
	output_file.close()
	
	with open('./'+foldername+'/ExtractedPlists/'+bundleid2+'-'+fileID+'.plist', 'rb') as plist:
		p2 = ccl_bplist.load(plist)
		parseplist = (p2['$objects'])
		relativePathpl = (parseplist[2])
		lastModified = (parseplist[1]['LastModified'])
		lastStatusChange = (parseplist[1]['LastStatusChange'])
		birth = (parseplist[1]['Birth'])
		birthN = datetime.datetime.utcfromtimestamp(birth)
		lastmodifiedN = datetime.datetime.utcfromtimestamp(lastModified)
		laststatuschangedN = datetime.datetime.utcfromtimestamp(lastModified)
		h.write('<tr><tD>Birth: '+str(birth)+'----'+str(birthN)+'</td></tr>')
		h.write('<tr><tD>Last Modified: '+str(lastModified)+'----'+str(lastmodifiedN)+'</td></tr>')
		h.write('<tr><tD>Last Status Change: '+str(lastStatusChange)+'----'+str(laststatuschangedN)+'</td></tr>')
		#print(lastStatusChange)
		#print(lastModified)
	
		#convert to calendar the utc
		
		#encstatus = pl['IsEncrypted']
		#print (encstatus+'inside function')

#write report function
def writehtml():
	print('inside function twite report')
	

for root, dirs, filenames in os.walk(data_dir):
	for f in filenames:
		if f == "Manifest.plist":
			pathfound = os.path.join(root, f)
			pathDB = os.path.join(root, 'Manifest.db')

if pathfound == 0:
	print("No Manifest.plist located")
else:
	#check for plist and db existence
	if os.path.isfile(pathfound):
		print('Manifest.plist located at: '+pathfound)
	else:
		sys.exit('No Manifest.plist located')
	
	if os.path.isfile(pathDB):
		print('Manifest.db located at: '+pathDB)
	else:
		sys.exit('No Manifest.db located')

	with open(pathfound,'rb') as mpl:
		pl = plistlib.load(mpl)
		encstatus = pl['IsEncrypted']
	
	if override == 'True':
		encstatus = 0
		print('Override encrypted flag: '+override)
		
	if encstatus == 0:
		print('Itunes Backup not encrypted.')
		
		path = os.getcwd()
		try:  
			outpath = path + "/" + foldername
			os.mkdir(outpath)
			os.mkdir(outpath+"/ExtractedPlists")
			os.mkdir(outpath+"/Reports")
			os.mkdir(outpath+"/Reports/images")
			print('Output directories created.')
		except OSError:  
			sys.exit("Error making output/report directories.")
		
		#connect sqlite databases
		db = sqlite3.connect(pathDB)
		cursor = db.cursor()

		cursor.execute('''
		SELECT * FROM Files
		WHERE relativePath LIKE '%@2x.jpeg' or relativePath LIKE '%@3x.jpeg'
		order by relativePath
		''')
		
		all_rows = cursor.fetchall()
		
		compare = 0
		
		for row in all_rows:
			fileID = row[0]
			domain = row[1]
			relativePath = row[2]
			bundleid = domain.split('-')
			bundleid2 = bundleid[1]
			fileName = relativePath.rsplit('/', 1)[-1]
			wbplist = row[4]
			
			for root, dirs, filenames in os.walk(data_dir):
				for f in filenames:
					if f == fileID:
						fileIDP = os.path.join(root, f)
						#rename image
						imageoutpath = (outpath+'/Reports/images/'+fileName)
						copy(fileIDP, imageoutpath)
			
			#print(fileName)
			
			if bundleid2 == compare:
			#continue the current report
				#print(fileName+' next app')
				print(fileName)
				h.write('<table>')
				h.write('<tr><td> App Snapshot name: '+fileName+'</td></tr>')
				h.write('<tr><td> App Snapshot fileID: '+fileID+'</td></tr>')
				h.write('<tr><td> Relative path per database: '+relativePath+'</td></tr>')
				h.write('<tr><td align="center"><a href=./images/'+fileName+' target="_blank">')
				h.write('<img src=./images/'+fileName+' width="310" height="552" </td></tr> ')
				analizeplist()
				h.write('</table>')
				h.write('<br>')
				#put values in report html
				
				
				
			else:
				print('')
				print('Processing: '+bundleid2)
				print(fileName)
				#start html for the bundle id new run
				h = open('./'+foldername+'/Reports/'+bundleid2+'.html', 'w') #write report
				h.write('<html><body>')
				h.write('<h2>iTunes Backup App Snapshot Triage Parser. </h2>')
				h.write('<h3>Application: '+bundleid2+'</h3>')
				h.write('Data aggregated per following data source: '+pathfound)
				h.write('<br>Press on the image to get full size.')
				h.write('<br>Unix timestamps converted to UTC.<br>')
				h.write ('<style> table, th, td {border: 1px solid black; border-collapse: collapse;}</style>')
				h.write('<br>')
				
				
				h.write('<table>')
				h.write('<tr><td> App Snapshot name: '+fileName+'</td></tr>')
				h.write('<tr><td> App Snapshot fileID: '+fileID+'</td></tr>')
				h.write('<tr><td> Relative path per database: '+relativePath+'</td></tr>')
				h.write('<tr><td align="center"><a href=./images/'+fileName+' target="_blank">')
				h.write('<img src=./images/'+fileName+' width="310" height="552" </td></tr> ')
				analizeplist()
				h.write('</table>')
				h.write('<br>')
			
				compare = bundleid2
	else:
		sys.exit('Itunes Backup is encrypted. No support available.')
print('')
print('Processing completed')