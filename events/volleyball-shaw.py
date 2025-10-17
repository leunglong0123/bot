USER_ID = "442240"
DATE = "25 Oct 2025"
START_TIME = "08:30"
END_TIME = "09:30"
CSRF_TOKEN = "1ba87331-0be7-4373-a5de-341fc684944a"
FACILITY_ID = "1751"


form_data = {
    "dataSetId": "18",
    "boBookingType.id": "1",
    "boBookingType.value": "INDV",
    "boBookingMode.value": "SPORT",
    "boBookingMode.id": "1",
    "userRefNum": "",
    "fbUserId": USER_ID,
    "grpFacilityIds": "",
    "repeatOccurrence": "false",
    "startDate": "",
    "startTime": "",
    "endDate": "",
    "endTime": "",
    "dayOfWeeks": "",
    "functionsAvailable": "false",
    "brcdNo": "",
    "phone": "",
    "onBehalfOfFbUserId": "",
    "byPassQuota": "false",
    "byPassChrgSchm": "false",
    "byPassBookingDaysLimit": "false",
    "searchFormString": f"fbUserId={USER_ID}&bookType=INDV&dataSetId=18&actvId=6&searchDate=25+Oct+2025&ctrId=1&facilityId=",
    "extlPtyDclrId": "",
    "boMakeBookFacilities[0].ctrId": "1",
    "boMakeBookFacilities[0].centerName": "Shaw Sports Complex",
    "boMakeBookFacilities[0].facilityId": FACILITY_ID,
    "boMakeBookFacilities[0].facilityName": "Volleyball Court No. 3",
    "boMakeBookFacilities[0].startDateTime": f"{DATE} {START_TIME}",
    "boMakeBookFacilities[0].endDateTime": f"{DATE} {END_TIME}",
    "declare": "on",
    "CSRFToken": None,
}