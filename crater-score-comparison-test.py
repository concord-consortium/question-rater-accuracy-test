# Comparing Old CRater Scores with New Question Rater Scores
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import requests
import csv
import os

API_ENDPOINT = "https://api.concord.org/question-rater"
PATH_TO_CSV = "./csv-test-files/"

def getCSVFiles():
    csv_files = sorted([pos_csv for pos_csv in os.listdir(
        PATH_TO_CSV) if pos_csv.endswith(".csv")])
    return csv_files

def getItemIDForFile(fileName, ending):
    itemID = fileName[:-len(ending)]
    return itemID

def updateFileResultData(results,expectedScore,actualScore):
    results[0] += expectedScore
    if actualScore is not None:
        results[1] += actualScore
    else:
        results[1] += ' '
    return results

def scoreTestFileData(file, writer):
    # File Result Data
    i = 0
    expected = []
    actual = []
    results = [expected,actual]
    itemID = getItemIDForFile(file, "_test_sample.csv")
    with open(PATH_TO_CSV + file, "r") as read_file:
        data = csv.reader(read_file)
        # Loop through answers within file
        for currentAnswer in data:
            text = currentAnswer[0]
            expectedScore = currentAnswer[1]
            # Use variables in post method to API
            actualScore = returnScoreFromAPI(itemID, text)
            print(str(i))
            i += 1
            results = updateFileResultData(results,expectedScore,actualScore)
            row = [itemID,text,expectedScore,actualScore]
            print(row)
            writer.writerow(row)
        return results
    read_file.close()

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

    r = requests.post(API_ENDPOINT, data=xml, headers=headers, auth=HTTPBasicAuth("extSysCRTR02dev", "3edc$RFV"))
    root = ET.fromstring(r.text)
    for i in root.iter('response'):
        actualScore = i.get('score')
        return actualScore

# Open write file 'crater-accuracy-results.csv' and add headers

csvFiles = getCSVFiles()
for csvFile in csvFiles:
    with open("results" + csvFile, mode='w') as csv_file:
        writer = csv.writer(csv_file)
        answerPairingsForFile = scoreTestFileData(csvFile, writer)
    csv_file.close()