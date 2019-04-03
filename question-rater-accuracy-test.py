# Testing Question Rater
import os
import json
import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
import csv

API_ENDPOINT = "https://api.concord.org/question-rater"
PATH_TO_JSON = "./automated-test-sample-data/"
PATH_TO_OUTPUT_FILE = "./"
json_files = [pos_json for pos_json in os.listdir(
    PATH_TO_JSON) if pos_json.endswith(".json")]

def getItemIDForFile(fileName, ending):
    itemID = fileName[:-len(ending)]
    # print("Printing the current item ID: " + itemID)
    return itemID

def checkScoreRange(humanScore, actualScore):
    acceptance = ""
    humanScore = int(humanScore)
    if actualScore is not None:
        actualScore = int(actualScore)
    else:
        return "False"
    acceptanceRange = [humanScore-1, humanScore, humanScore+1]

    if actualScore in acceptanceRange:
        acceptance = "TRUE"
    else:
        acceptance = "FALSE"
    return acceptance


def updateFileResultData(fileData, status):
    if status == "TRUE":
        fileData["Correct"] += 1
    elif status == "FALSE":
        fileData["Incorrect"] += 1
    fileData["Total"] += 1
    fileData["Accuracy"] = round(((fileData["Total"]-fileData["Incorrect"])/fileData["Total"]),2)

    return fileData

def scoreTestFileData(jsonFile):
    #File Result Data
        itemID = getItemIDForFile(jsonFile, "_test_sample.json")
        fileData = {"ItemID":itemID,"Correct":0, "Incorrect":0, "Total":0, "Accuracy":0}
        with open(PATH_TO_JSON + jsonFile, "r") as read_file:
            data = json.load(read_file)
            # Loop through answers within file
            for currentAnswer in data:
                text = currentAnswer["text"]
                expectedScore = currentAnswer["classification"]
                # Use variables in post method to API
                actualScore = returnScoreFromAPI(itemID, text)
                acceptanceStatus = checkScoreRange(expectedScore, actualScore)
                updateFileResultData(fileData, acceptanceStatus)
        writer.writerow(fileData)

def returnScoreFromAPI(itemID, text):
    headers = {
        "Content-Type": "text/xml",
        "x-api-key": "HsIXRYCsAgL5Tjfvm71jX5ZY599wmGaAojVvsli0"
    }
  
    xml = """
    <crater-request includeRNS="N">
      <client id="cc"/>
      <items>
        <item id=\""""+itemID + """\">
          <responses>
            <response id="456">
              <![CDATA["""+text+"""]]>
            </response>
          </responses>
        </item>
      </items>
    </crater-request>
    </root>"""

    r = requests.post(API_ENDPOINT, data=xml, headers=headers,auth=HTTPBasicAuth("extSysCRTR02dev", "3edc$RFV"))
    root = ET.fromstring(r.text)
    for i in root.iter('response'):
        actualScore = i.get('score')
        return actualScore


# Open write file 'crater-accuracr-results.csv'
with open('crater-accuracy-results.csv', mode='w') as csv_file:
    fieldnames = ["ItemID", "Correct", "Incorrect", "Total", "Accuracy"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    # Loop through answer files
    for jsonFile in json_files:
        #File Result Data
        itemID = getItemIDForFile(jsonFile, "_test_sample.json")
        fileData = {"ItemID":itemID,"Correct":0, "Incorrect":0, "Total":0, "Accuracy":0}
        with open(PATH_TO_JSON + jsonFile, "r") as read_file:
            data = json.load(read_file)
            # Loop through answers within file
            for currentAnswer in data:
                text = currentAnswer["text"]
                expectedScore = currentAnswer["classification"]
                # Use variables in post method to API
                actualScore = returnScoreFromAPI(itemID, text)
                acceptanceStatus = checkScoreRange(expectedScore, actualScore)
                updateFileResultData(fileData, acceptanceStatus)
        writer.writerow(fileData)

