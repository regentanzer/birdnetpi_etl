# birdnetpi_etl
ETL Pipeline from BirdNETPi to Google Sheets

These are easy instructions for setting up an ETL pipeline in order to egress aggregate data from a BirdNETpi system to Google Sheets. I did this both to be able to track birds without having to be on my network and to be able to create a custom dashboard that can be shared.


## Step 0: BirdNETpi
This assumes that you have built a birdnet on a raspberry pi and it is running on your local network. You should be able to SSH into the RPi.

Notes before starting:
- Anything in brackets [] below and in the files need to be replaced with your information

## Step 1: Google Cloud Console
You need to set up a service account via Google Cloud Console. I set up a separate email address that I used for this and that also owned the Google sheet (see step 2). 

Navigate to the Google Cloud Console and sign in with the account you are going to be using for this project. 

Create a new project.

Enable the following APIs:
- Google Sheets API
- Google Drive API

On the lefthand side, click on APIs & Services, then click on Credentials. Click on Create Credentials and then create a Service Account.

You'll need to grant the service account access to the project you just set up. 

Finally, you need to create a key for the service account in the keys section. Click Add Key and then JSON. This will download a file (that you can then rename and upload to your RPi in step 4). Take note of the service account email address (located in the client_email field in the JSON) and make sure that your service account email has access as an editor to the google sheet (step 2).


## Step 2: Set Up Google Sheet

Set up a google sheet that will hold your raw data. Remember that the service account must have access to the sheet as an editor. 

Put in the column names (in the SQL query in the program). If you use my SQL query, these are the column names I used:
id,
date,
week,
hour,
common_name,
detections


## Step 3: RPi Virtual Environment Setup

ssh into your BirdNETpi

BirdNETPi does not allow you to run programs in Python except for in a virtual environment. In your command line, please run these lines to first create your virtual environment (venv) and activate it:

cd /home/[birdnet_username]
python3 -m venv /home/[birdnet_username]/venv
source /home/[birdnet_username]/venv/bin/activate

Any time you want to make a change to your program, you need to enable your virtual environment, you can do so running these lines:

cd /home/[birdnet_username]/venv
source /home/[birdnet_username]/venv/bin/activate

Once your virtual environment is activated, please install the required packages:
pip install gspread oauth2client

gspread is a package that allows you to connect to the Google Sheets API
oauth2client is a package that aids with authorization


## Step 4: Add Program + Credentials to Venv
The program is called birdnet_to_sheets.py, you need to edit this file to update anything with brackets around it [].

You can either save your own credentials as google_sheets_credentials.json, or paste them into the json provided. 

Upload both to the virtual environment with this code: 
scp [your_directory_location]\google_sheets_credentials.json USERNAME@BIRDNET_IP:/home/[birdnet_username]/venv/google_sheets_credentials.json
scp [your_directory_location]\birdnet_to_sheets.py USERNAME@BIRDNET_IP:/home/[birdnet_username]/venv/google_sheets_credentials.json


## Step 5: Testing
Within your virtual environment, run this code to test your program:

python /home/[birdnet_username]/birdnet_to_sheets.py


## Step 6: Backfilling
Continue to run the program until you have backfilled all the data. I found that doing it every minute brought in about 60 records, so if your data goes back quite a bit, you may want to set up a cron expression (see step 7) to do this for you. 


## Step 7: Cron expression
Run the program however often you would like. However, keep in mind the per minute limit above. I have mine update on the hour. 

To do that, please run this code to open the crontab:
crontab -e

Then add this cron job to the file it opens:
0 * * * * source /home/[birdnet_username]/venv/bin/activate && /home/[birdnet_username]/venv/bin/python /home/[birdnet_username]/birdnet_to_sheets.py

To verify that your cron job is working, use this code:
crontab -l


## Step 8: Display Data
The reason why I built this was to display data in a dashboard. I connected the google sheet to a Looker Studio dashboard. 



## Notes

The program creates a temporary copy of the database because BirdNETpi is continually putting data into the database, meaning that it is unuseable any time it is inserting data. This assures that there will be no crashes due to the database being unavailable. 

I set up the SQL query to aggregate data. In order for the appending to work, it needed to have a unique identifier so that the program could find the last record and append the new data. 

I've opted to run a macro on the google sheets side to deal with any data type issues. I found that the date data type is not stored particularly well in the BirdNETpi database and to be honest, this is my lazy way of dealing with it. 
