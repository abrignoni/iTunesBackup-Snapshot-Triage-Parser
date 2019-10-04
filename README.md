# iTunesBackup-Snapshot-Triage-Parser

Parse iOS 13 iTunes backups to extract application snapshots. These snapshots are screenshots that show the last thing that an app had on screen before the app was sent to the background.

iTunes backups need to be unencrytped/decrypted.

Usage:
SnapTriage.py iTunesBackupDirectoryPath

Script will generate:
* Html reports showing available snapshots per app.
* Extract snapshot bplists from the Manifest.db file for third party application analysis.
