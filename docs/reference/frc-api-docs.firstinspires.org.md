# FRC Events

# Overview

_FIRST_/FMS FRC Events API is a service to return relevant information about the _FIRST_ Robotics Competition (FRC). Information is made available from events operating around the world.

For FRC, information is made available by the Field Management System (FMS) server operating at each event site. The FMS will attempt to sync all data from the event to "the cloud" as long as internet is available at the venue. If internet is unavailable, or "goes down" during the event, the FMS will automatically sync all data from the time the system was offline as soon as the connection is restored. The API will provide data as soon as it has synced, and we do not add any artificial delays. If you are receiving "stale" data, it may be because of connectivity problems at the venue. We recommend you try again later, and post on the FIRST FMS TeamForge site if the problem persists. _(Note: FMS does not sync while a match is running, so data that has to do with a particular match should become available once the score has been revealed to the audience at the event.)_

### Migration and Program Notes:

Pay close attention to the addresses for calling the various endpoints- as well as the notes regarding endpoints with multiple possible responses (i.e. score details and rankings).

# Documentation Notes

All times are listed in the local time to the event venue. HTTP-date values will show their timezone.

If you specify a parameter, but no value for that parameter, it will be ignored. For example, if you request **URL?teamNumber=** the **teamNumber** parameter would be ignored.

We will continue to support the current version of the API plus one version older. Old APIs are depricated once a version "two times newer" is available, at minimum 6 months. For example, version 2.0 and 1.0 are supported right now, but 1.0 will not be supported once 2.1 (or 3.0) is available. Versions may also be retired earlier with prior notice here in the documentation.

The full host address of the API is needed in all calls. The version number is required in each call in order to ensure your requests are made (and responses are returned) in the formats you anticipate. The version number for this documentation is found on the top of the page, in the title. If you call this version number, the API responses will match the formats listed below.

All of the APIs are capable of accepting the **Accept** HTTP header with either **application/xml** or **application/json** based on the desired return type. Any API call that results in an **HTTP Status Code** other than **200 (OK)** will only be shown here as an **application/json** response to save space, but the content is the same regardless of the request type. All response will have a **Content-Length** and **Date** response header, but those are not shown in the documentaiton.

For all APIs that accept a query string in addition to the URI base, the order of parameters do not matter, but the name shown in the documentation must match exactly, as does the associated value format as described in details.

For response codes that are not **HTTP 200 (OK)**, the documentation will show a body message that represents a possible response value. While the "title" of the **HTTP Status Code** will match those shown in the response codes documentation section exactly, the body of the response will be a more detailed explanation of why that status code is being returned and may not always be exactly as shown in the examples.

None of the APIs will show possible return here in the documentation of **HTTP 401 (Unauthorized)**, but that code applies to all APIs as a possible response if the request is made without a valid token.

### Last-Modified, FMS-OnlyModifiedSince, and If-Modified-Since Headers

The FRC Events API utilizes the **Last-Modified** and **If-Modified-Since** Headers to communicate with consumers regarding the age of the data they are requesting. With a couple of exceptions, all calls will return a **Last-Modified** Header set with the time at which the data at that endpoint was last modified. The Header will always be set in the HTTP-date format, as described in the [HTTP Protocol](https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html). There are two exceptions: the **Last-Modified** Header is not set if the endpoint returns no results (such as a request for a schedule with no matches) and will also not be set if the request was an **HTTP DELETE**.

Consumers should keep track of the **Last-Modified** Header, and return it on subsequent calls to the same endpoint as the **If-Modified-Since**. The server will recognize this request, and will only return a result if the data has been modified since the last request. If no changes have been made, an **HTTP 304** will be returned. If data has been modified, ALL data on that call will be returned (for "only modified" data, see below).

The FRC Events API also allows a custom header used to filter the return data to a specific subset. This is done by specifying a **FMS-OnlyModifiedSince** header with each call. As with the **If-Modified-Since** header, consumers should keep track of the **Last-Modified** Header, and return it on subsequent calls to the same endpoint as the **FMS-OnlyModifiedSince** Header. The server will recognize this request, and will only return a result if the data has been modified since the last request, and, if returned, the data will only be those portions modified since the included date. If no changes, have been made, an **HTTP 304** will be returned. Using this method, the server and consumer save processing time by only receiving modified data that is in need of update on the consumer side.

If the Headers are improperly passed (such as the wrong Day of Week for the matching date, or a date in the future), the endpoint will simply ignore the Header and return all results. If both headers are specified, the request will be denied.

# Response Codes

The FRC Events API HTTP Status Codes correspond with the [common codes](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html), but occasionally with different "titles". The "title" used by the API is shown next to each of the below possible response HTTP Status Codes. Throughout the documentation, Apiary may automatically show the common "title" in example returns (like "Not Found" for 404) but on the production server, the "title" will instead match those listed below.

Plain Text

```plain
HTTP 200 - "OK"
```

The request has succeeded. An entity corresponding to the requested resource is sent in the response. This will be returned as the HTTP Status Code for all request that succeed, even if the body is empty (such as an event that has no rankings, but with a valid season and event code were used)

Plain Text

```plain
HTTP 304 - "Not Modified"
```

When utilizing a Header that allows filtered data returns, such as **If-Modified-Since**, this response indicates that no data meets the request.

View More

Plain Text

```plain
HTTP 400 - "Invalid Season Requested"/"Malformed Parameter Format In Request"/"Missing Parameter In Request"/"Invalid API Version Requested":
```

The request could not be understood by the server due to malformed syntax. The client SHOULD NOT repeat the request without modifications. Specifically for this API, a 400 response indicates that the requested URI matches with a valid API, but one or more required parameter was malformed or invalid. Examples include an event code that is too short or team number that contains a letter.

Plain Text

```plain
HTTP 401 - "Unauthorized"
```

All requests against the API require authentication via a valid user token. Failing to provide one, or providing an invalid one, will warrant a 401 response. The client MAY repeat the request with a suitable Authorization header field.

Plain Text

```plain
HTTP 404 - "Invalid Event Requested"
```

Even though the 404 code usually indicates any not found status, a 404 will only be issued in this API when an event cannot be found for the requested season and event code. If the request didn't match a valid API or there were malformed parameters, the response would not receive a 404 but rather a 400 or 501. If this HTTP code is received, the season was a valid season and the event code matched the acceptable style of an event code, but there were no records of an event matching the combination of that season and event code. For example, HTTP 404 would be issued when the event had a different code in the requested season (the codes can change year to year based on event location).

Plain Text

```plain
HTTP 500 - "Internal Server Error"
```

The server encountered an unexpected condition which prevented it from fulfilling the request. This is a code sent directly by the server, and has no special alternate definition specific to this API.

Plain Text

```plain
HTTP 501 - "Request Did Not Match Any Current API Pattern"
```

The server does not support the functionality required to fulfill the request. Specifically, the request pattern did not match any of the possible APIs, and thus processing was discontinued. This code is also issued when too many optional parameters were included in a single request and fulfilling it would make the result confusing or misleading. Each API will specify which parameters or combination of parameters can be used at the same time.

Plain Text

```plain
HTTP 503 - "Service Unavailable"
```

The server is currently unable to handle the request due to a temporary overloading or maintenance of the server. The implication is that this is a temporary condition which will be alleviated after some delay. If known, the length of the delay MAY be indicated in a Retry-After header. This code will not always appear, sometimes the server may outright refuse the connection instead. This is a code sent directly by the server, and has no special alternate definition specific to this API.

See the notes at the top of this documentation for important information about HTTP Status Codes.

# Authorization

In order to make calls against the FRC Events API, you must include an HTTP Header called **Authorization** with the value set as specified below. If a request is made without this header, processing stops and an **HTTP 401** is issued. All **Authorization** headers follow the same format:

Authorization: Basic 000000000000000000000000000000000000000000000000000000000000

Where the Zeros are replaced by your Token. The Token can be formed by taking your **username** and your **AuthorizationKey** and adding a colon. For example, if your **username** is sampleuser and your **AuthorizationKey** is 7eaa6338-a097-4221-ac04-b6120fcc4d49 you would have this string:

**sampleuser:7eaa6338-a097-4221-ac04-b6120fcc4d49**

This string must then be encoded using Base64 Encoded to form the Token, which will be the same length as the example above, but include letters and numbers. For our example, we would have:

c2FtcGxldXNlcjo3ZWFhNjMzOC1hMDk3LTQyMjEtYWMwNC1iNjEyMGZjYzRkNDk=

**NOTICE**: Publicly distributing an application, code snippet, etc, that has your username and token in it, encoded or not, WILL result in your token being blocked from the API. Each user should apply for their own token.

If you wish to acquire a token for your development, you may do so by requesting a token through our automated system on [this website](https://frc-events.firstinspires.org/services/API).

**AUTOMATED REMOVAL**: If you do not activate your account within 72 hours of making your request for a token, or if you do not make at least one API request every twelve (12) months, your account/token will be marked as disabled for inactivity and subject to being deleted. (This policy does not apply to accounts with special operating agreements with FIRST)

### HTTP401 and Authorization

Each Token can be individually enabled and disabled by _FIRST_. As such, a normally valid combination of **username** and **AuthorizationToken** could still be rejected. The possible return messages you may see in these instances are:

**Incorrect Token** (You supplied an AuthorizationToken, but it wasn't correct)

**Account Disabled, Contact Support** (You have been disabled for excessive traffic or abuse. Contact support)

**Username Not Found** (A username was found, but didn't match any on file)

**Unable To Determine Authorization Token** (The format of the **Authorization** header was incorrect)

# Webhooks

> **COMING SOON**

AUTHORIZATIONBasic Auth

Username

Password

## 

Ancillary

AUTHORIZATIONBasic Auth

This folder is using Basic Auth from collection[FRC Events](#auth-info-51a3938d-2026-4a5c-9f17-d87d035584cd)

### GETAPI Index

https://frc-api.firstinspires.org/v3.0/

Root level call with no parameters.

Example Request

Details about the API

python

```python
import requests

url = "https://frc-api.firstinspires.org/v3.0/"

payload={}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

200 OK

Example Response

-   Body
-   Headers (1)

json

```json
{
  "currentSeason": 2021,
  "maxSeason": 2021,
  "name": "FIRST ROBOTICS COMPETITION API",
  "apiVersion": "2.0",
  "status": "normal"
}
```

Content-Type

application/json

## 

Season Data

AUTHORIZATIONBasic Auth

This folder is using Basic Auth from collection[FRC Events](#auth-info-51a3938d-2026-4a5c-9f17-d87d035584cd)

### GETTeam Avatar Listings

https://frc-api.firstinspires.org/v3.0/:season/avatars?teamNumber=&eventCode=&page=

This endpoint applies only to the 2018 or later seasons. Requests for other seasons will result in a `Bad Season` error. The team avatar listings API returns all FRC official teams in a particular `season` with, if applicable, their Avatar. If specified, the `teamNumber` parameter will return only one result with the details of the requested `teamNumber`. Alternately, the `eventCode` parameter allows sorting of the team list to only those teams attending a particular event in the particular `season`. If you specify a `teamNumber` parameter, you cannot additionally specify an `eventCode` or you will receive an `HTTP 501`. If a team does not have an Avatar, the return value will be `null`. Please note that the returned Avatar is encoded in the reply, and would need to be properly handled in order to render a PNG image.

AUTHORIZATIONBasic Auth

This request is using Basic Auth from collection[FRC Events](#auth-info-51a3938d-2026-4a5c-9f17-d87d035584cd)

HEADERS

If-Modified-Since

PARAMS

teamNumber

**(int)** Numeric teamNumber of the team about which information is requested. Must be 1 to 4 digits.

eventCode

**(string)** Case insensitive alphanumeric eventCode of the event from which details are requested.

page

**(int)** Numeric page of results to return. If not included, page 1 will be returned.

PATH VARIABLES

season

2022

**\[REQUIRED\] (int)** Numeric year of the event from which the award listings are requested. Must be 4 digits and greater than or equal to 2015, and less than or equal to the current year.

Example Request

unexpected error

View More

python

```python
import requests

url = "https://frc-api.firstinspires.org/v3.0/:season/avatars?teamNumber=&eventCode=&page="

payload={}
headers = {
  'Authorization': 'Basic <credentials>',
  'If-Modified-Since': ''
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

500 Internal Server Error

Example Response

-   Body
-   Headers (1)

json

```json
{
  "code": 500,
  "message": "Internal Server Error"
}
```

Content-Type

application/json

## 

Awards

AUTHORIZATIONBasic Auth

This folder is using Basic Auth from collection[FRC Events](#auth-info-51a3938d-2026-4a5c-9f17-d87d035584cd)

### GETEvent Awards

https://frc-api.firstinspires.org/v3.0/:season/awards/event/:eventCode

The event awards API returns details about awards presented at a particular event in a particular season. Return values may contain either `teamNumber` or `person` values, and if the winner was a `person`, and that person is from a team, the `teamNumber` value might be set with their `teamNumber`.

AUTHORIZATIONBasic Auth

This request is using Basic Auth from collection[FRC Events](#auth-info-51a3938d-2026-4a5c-9f17-d87d035584cd)

HEADERS

If-Modified-Since

PATH VARIABLES

season

2022

**\[REQUIRED\] (int)** Numeric year of the event from which the award listings are requested. Must be 4 digits and greater than or equal to 2015, and less than or equal to the current year.

eventCode

(Required) **(string)** Optional case insensitive alphanumeric eventCode of the event from which the awards are requested. Must be at least 3 characters.

Example Request

Response

View More

python

```python
import requests

url = "https://frc-api.firstinspires.org/v3.0/2020/awards/ARLI/:teamNumber"

payload={}
headers = {
  'Authorization': 'Basic <credentials>',
  'If-Modified-Since': ''
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

200 OK

Example Response

-   Body
-   Headers (2)

View More

json

```
{
  "Awards": [
    {
      "awardId": 397,
      "teamId": 1023300,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Regional Chairman's Award",
      "series": 1,
      "teamNumber": 4265,
      "schoolName": "Oak Ridge High School",
      "fullTeamName": "Bechtel/UT Battelle & Oak Ridge National Labs/CNS, Consolidated Nucear Security LLC/Leidos/Oak Ridge Schools/Oak Ridge Public Schools Education Foundation/Oak Ridge Tool and Engineering/ARC Machining/RT Coating/ARMEC/Axis Fabrication & Machine/Technical Machining/Centrus/MS Technology, Inc./Engineering Services Group, Inc./UCOR URS CH2M Oak Ridge LLC/ORAU/Fastenal/Roane State Foundation/Bob Eby/FIRST Place Finish&Oak Ridge High School",
      "person": null
    },
    {
      "awardId": 635,
      "teamId": 1024008,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Regional Engineering Inspiration Award",
      "series": 1,
      "teamNumber": 5006,
      "schoolName": "Haas Hall Academy-Fayetteville",
      "fullTeamName": "RCAL Products Inc./American Electric Power/Pinnacle Energy & Haas Hall Academy-Fayetteville",
      "person": null
    },
    {
      "awardId": 233,
      "teamId": 1023658,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "FIRST Dean's List Finalist Award",
      "series": 1,
      "teamNumber": 4635,
      "schoolName": "PrepaTec Eugenio Garza Sada",
      "fullTeamName": "PrepaTec, Eugenio Garza Sada/General Motors/T-REX/Milwaukee/Risoul/Grupo Surman/Qualcomm /POISE&PrepaTec Eugenio Garza Sada",
      "person": "Alejandro Sánchez"
    },
    {
      "awardId": 233,
      "teamId": 1023434,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "FIRST Dean's List Finalist Award",
      "series": 2,
      "teamNumber": 4403,
      "schoolName": "PrepaTec Laguna",
      "fullTeamName": "PEÑOLES&PrepaTec Laguna",
      "person": "Paulina Alamán"
    },
    {
      "awardId": 407,
      "teamId": 1020070,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Regional Winners",
      "series": 1,
      "teamNumber": 16,
      "schoolName": "Mountain Home HS Career Acad",
      "fullTeamName": "Baxter Healthcare Corporation & Mountain Home HS Career Acad",
      "person": null
    },
    {
      "awardId": 407,
      "teamId": 1023122,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Regional Winners",
      "series": 2,
      "teamNumber": 4087,
      "schoolName": "Benjamin Franklin High School",
      "fullTeamName": "NASA/Laitram/Intralox/Department of the Defense (DoD) STEM/Lockheed Martin/Leidos/DOW (GLAD)/Bayer-Monsanto/Friends of Falcon Robotics /Entergy/Abbott/Kettering University/Cornerstone/Boardwalk Pipeline/Shell Exploration and Production/Shell Convent Refinery/Freeport McMoran/Benjamin Franklin High School/Fab Lab NOLA/Donors Choose&Benjamin Franklin High School",
      "person": null
    },
    {
      "awardId": 407,
      "teamId": 1023588,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Regional Winners",
      "series": 3,
      "teamNumber": 4576,
      "schoolName": "Powell High School & Halls High School",
      "fullTeamName": "Knox County Schools / Wall Praise / Panda Enterprises, Inc. / Tru-Design, LLC & Powell High School & Halls High School",
      "person": null
    },
    {
      "awardId": 403,
      "teamId": 1022992,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Regional Finalists",
      "series": 1,
      "teamNumber": 3959,
      "schoolName": "Albert P Brewer HS Career Tech",
      "fullTeamName": "NASA Marshall Space Flight Center / Morgan County, AL Schools / Missle Defense Agency / Northrop Grumman / Redstone Federal Credit Union / G & J Automatic Screw / AIAA / ULA & Albert P Brewer HS Career Tech",
      "person": null
    },
    {
      "awardId": 403,
      "teamId": 1022964,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Regional Finalists",
      "series": 2,
      "teamNumber": 3937,
      "schoolName": "Harding Academy",
      "fullTeamName": "Ryerson/Harding University Center for Distance Learning/Custom Colors/Eaton Corporation & Harding Academy",
      "person": null
    },
    {
      "awardId": 403,
      "teamId": 1021226,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Regional Finalists",
      "series": 3,
      "teamNumber": 1723,
      "schoolName": "William Chrisman High School & Truman High School & Van Horn High School",
      "fullTeamName": "Independence School District/Ronson Manufacturing/L & K Hardwoods/KC STEM Alliance/Bennett Tool & Die&William Chrisman High School&Truman High School&Van Horn High School",
      "person": null
    },
    {
      "awardId": 455,
      "teamId": 1021672,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Woodie Flowers Finalist Award",
      "series": 1,
      "teamNumber": 2393,
      "schoolName": "Knoxville Catholic High School",
      "fullTeamName": "Navus Automation, Inc. / Denso / Bertlekamp Automation Inc. / North Wind Group & Knoxville Catholic High School",
      "person": "Scott Palko"
    },
    {
      "awardId": 649,
      "teamId": 1022992,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Wildcard",
      "series": 1,
      "teamNumber": 3959,
      "schoolName": "Albert P Brewer HS Career Tech",
      "fullTeamName": "NASA Marshall Space Flight Center / Morgan County, AL Schools / Missle Defense Agency / Northrop Grumman / Redstone Federal Credit Union / G & J Automatic Screw / AIAA / ULA & Albert P Brewer HS Career Tech",
      "person": null
    },
    {
      "awardId": 649,
      "teamId": 1022964,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Wildcard",
      "series": 2,
      "teamNumber": 3937,
      "schoolName": "Harding Academy",
      "fullTeamName": "Ryerson/Harding University Center for Distance Learning/Custom Colors/Eaton Corporation & Harding Academy",
      "person": null
    },
    {
      "awardId": 657,
      "teamId": 1022698,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Safety Award sponsored by Underwriters Laboratories",
      "series": 1,
      "teamNumber": 3593,
      "schoolName": "Victory Christian School",
      "fullTeamName": "Boeing/DOD STEM/LDKerns Construction/Oral Roberts University/The Woodard Family/Verizon&Victory Christian School",
      "person": null
    },
    {
      "awardId": 289,
      "teamId": 1020070,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Industrial Design Award sponsored by General Motors",
      "series": 1,
      "teamNumber": 16,
      "schoolName": "Mountain Home HS Career Acad",
      "fullTeamName": "Baxter Healthcare Corporation & Mountain Home HS Career Acad",
      "person": null
    },
    {
      "awardId": 251,
      "teamId": 1070840,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Highest Rookie Seed",
      "series": 1,
      "teamNumber": 8043,
      "schoolName": "Kamen STEM",
      "fullTeamName": "Kamen STEM /Stanfield + O'Dell/NASA&Kamen STEM",
      "person": null
    },
    {
      "awardId": 329,
      "teamId": 1022158,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Judges' Award",
      "series": 1,
      "teamNumber": 2992,
      "schoolName": "Mandeville High School",
      "fullTeamName": "NASA/Bureau of Ocean Energy Management/Entergy/Chevron/Intralox/Ochsner/Livaudais Electrical & Construction/City of Mandeville Louisiana/St. Tammany Parish School Board&Mandeville High School",
      "person": null
    },
    {
      "awardId": 661,
      "teamId": 1022218,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Autonomous Award sponsored by Ford",
      "series": 1,
      "teamNumber": 3039,
      "schoolName": "Destrehan High School",
      "fullTeamName": "Shell Norco / Entergy - Waterford 3 Nuclear / Dow / St. Charles Parish Public Schools / Engine Monitor / Shirt Shack / Cospolich & Destrehan High School",
      "person": null
    },
    {
      "awardId": 277,
      "teamId": 1022996,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Imagery Award in honor of Jack Kamen",
      "series": 1,
      "teamNumber": 3966,
      "schoolName": "L&N STEM Academy",
      "fullTeamName": "L&N STEM Academy/Knox County Schools/NASA/Bechtel Corp./Leidos/ORNL/Clayton Family Foundation/Radio Systems/Arconic Foundation/Consolidated Nuclear Security/Cheddar's Scratch Kitchen/Amazon Smile&L&N STEM Academy",
      "person": null
    },
    {
      "awardId": 561,
      "teamId": null,
      "eventId": 44122,
      "eventDivisionId": null,
      "eventCode": "ARLI",
      "name": "Volunteer of the Year",
      "series": 1,
      "teamNumber": null,
      "schoolName": null,
      "fullTeamName": null,
      "person": "Pamela Mangrum"
    }
  ]
}
```

Last-Modified

sed in laboris

The date and time of when the response data was last modified on the server.

Content-Type

application/json

### GETScore Details

https://frc-api.firstinspires.org/v3.0/:season/scores/:eventCode/:tournamentLevel?matchNumber=&start=&end=

The score details API returns the score detail for all matches of a particular event in a particular season and a particular tournament level. Score details are only available once a match has been played, retrieving info about future matches requires the event schedule API. You cannot receive data about a match that is in progress.

**IMPORTANT: This endpoint returns differently depending on the season requested. The response details are listed multiple times, representing the different seasons possible in the return. Additionally, the scores shown in the example returns are not necessarily realistic- like the points may not add up.**

If you specify the `teamNumber` parameter, you cannot specify a `matchNumber` parameter. If you specify the `matchNumber`, you cannot define a `start` or `end`.

_**Note:**_ If you specify start, and it is higher than the maximum match number at the event, you will not receive any match results in the response. The same is true in reverse for the end parameter.

> _Click the "20XX Score Details" drop down in the example request/response pane (to the right or below) to view example score details responses for each of the available seasons._

AUTHORIZATIONBasic Auth

This request is using Basic Auth from collection[FRC Events](#auth-info-51a3938d-2026-4a5c-9f17-d87d035584cd)

HEADERS

If-Modified-Since

PARAMS

matchNumber

**(int)** Optional specific single matchNumber of result.

start

**(int)** Optional start match number for subset of results to return (includsive).

end

**(int)** Optional end match number for subset of results to return (inclusive).

PATH VARIABLES

season

2022

**\[REQUIRED\] (int)** Numeric year of the event from which the award listings are requested. Must be 4 digits and greater than or equal to 2015, and less than or equal to the current year.

eventCode

(Required) **\[REQUIRED\] (string)** Case insensitive alphanumeric eventCode of the event from which the details are requested. Must be at least 3 characters.

tournamentLevel

(Required) **\[REQUIRED\] (string)** Required tournamentLevel of desired score details.

Enum values:

Plain Text

```plain
1. None
2. Practice
3. Qualification
4. Playoff
```

Example Request

2015 Score Details

View More

python

```python
import requests

url = "https://frc-api.firstinspires.org/v3.0/2015/scores/ARFA/Playoff"

payload={}
headers = {
  'Authorization': 'Basic <credentials>',
  'If-Modified-Since': ''
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

200 OK

Example Response

-   Body
-   Headers (2)

View More

json

```
{
  "MatchScores": [
    {
      "matchLevel": "Playoff",
      "matchNumber": 1,
      "coopertition": "Unknown",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 8,
          "toteCountNear": 8,
          "containerCountLevel1": 0,
          "containerCountLevel2": 1,
          "containerCountLevel3": 0,
          "containerCountLevel4": 0,
          "containerCountLevel5": 1,
          "containerCountLevel6": 0,
          "litterCountLandfill": 2,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 2,
          "foulCount": 0,
          "autoPoints": 0,
          "totePoints": 32,
          "containerPoints": 28,
          "litterPoints": 10,
          "teleopPoints": 70,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 70
        },
        {
          "alliance": "Blue",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": true,
          "toteCountFar": 0,
          "toteCountNear": 12,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 2,
          "containerCountLevel5": 0,
          "containerCountLevel6": 0,
          "litterCountLandfill": 1,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 3,
          "foulCount": 0,
          "autoPoints": 20,
          "totePoints": 24,
          "containerPoints": 32,
          "litterPoints": 13,
          "teleopPoints": 69,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 89
        }
      ]
    },
    {
      "matchLevel": "Playoff",
      "matchNumber": 2,
      "coopertition": "Unknown",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": false,
          "containerSet": false,
          "toteSet": true,
          "toteStack": false,
          "toteCountFar": 15,
          "toteCountNear": 9,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 1,
          "containerCountLevel5": 1,
          "containerCountLevel6": 0,
          "litterCountLandfill": 4,
          "litterCountContainer": 1,
          "litterCountUnprocessed": 3,
          "foulCount": 1,
          "autoPoints": 6,
          "totePoints": 48,
          "containerPoints": 36,
          "litterPoints": 22,
          "teleopPoints": 106,
          "adjustPoints": 0,
          "foulPoints": 6,
          "totalPoints": 106
        },
        {
          "alliance": "Blue",
          "robotSet": true,
          "containerSet": true,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 6,
          "toteCountNear": 4,
          "containerCountLevel1": 0,
          "containerCountLevel2": 1,
          "containerCountLevel3": 1,
          "containerCountLevel4": 0,
          "containerCountLevel5": 0,
          "containerCountLevel6": 0,
          "litterCountLandfill": 0,
          "litterCountContainer": 2,
          "litterCountUnprocessed": 4,
          "foulCount": 0,
          "autoPoints": 12,
          "totePoints": 20,
          "containerPoints": 20,
          "litterPoints": 28,
          "teleopPoints": 68,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 80
        }
      ]
    },
    {
      "matchLevel": "Playoff",
      "matchNumber": 3,
      "coopertition": "None",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 9,
          "toteCountNear": 14,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 2,
          "containerCountLevel5": 1,
          "containerCountLevel6": 1,
          "litterCountLandfill": 0,
          "litterCountContainer": 1,
          "litterCountUnprocessed": 2,
          "foulCount": 0,
          "autoPoints": 0,
          "totePoints": 46,
          "containerPoints": 76,
          "litterPoints": 14,
          "teleopPoints": 136,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 136
        },
        {
          "alliance": "Blue",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 8,
          "toteCountNear": 4,
          "containerCountLevel1": 0,
          "containerCountLevel2": 1,
          "containerCountLevel3": 0,
          "containerCountLevel4": 0,
          "containerCountLevel5": 0,
          "containerCountLevel6": 1,
          "litterCountLandfill": 2,
          "litterCountContainer": 1,
          "litterCountUnprocessed": 4,
          "foulCount": 0,
          "autoPoints": 0,
          "totePoints": 24,
          "containerPoints": 32,
          "litterPoints": 24,
          "teleopPoints": 80,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 80
        }
      ]
    },
    {
      "matchLevel": "Playoff",
      "matchNumber": 4,
      "coopertition": "None",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": true,
          "toteCountFar": 7,
          "toteCountNear": 12,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 0,
          "containerCountLevel5": 0,
          "containerCountLevel6": 3,
          "litterCountLandfill": 0,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 2,
          "foulCount": 0,
          "autoPoints": 20,
          "totePoints": 38,
          "containerPoints": 72,
          "litterPoints": 8,
          "teleopPoints": 118,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 138
        },
        {
          "alliance": "Blue",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 7,
          "toteCountNear": 8,
          "containerCountLevel1": 0,
          "containerCountLevel2": 1,
          "containerCountLevel3": 0,
          "containerCountLevel4": 1,
          "containerCountLevel5": 1,
          "containerCountLevel6": 0,
          "litterCountLandfill": 0,
          "litterCountContainer": 3,
          "litterCountUnprocessed": 1,
          "foulCount": 0,
          "autoPoints": 0,
          "totePoints": 30,
          "containerPoints": 44,
          "litterPoints": 22,
          "teleopPoints": 96,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 96
        }
      ]
    },
    {
      "matchLevel": "Playoff",
      "matchNumber": 5,
      "coopertition": "None",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": true,
          "toteCountFar": 15,
          "toteCountNear": 5,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 1,
          "containerCountLevel4": 0,
          "containerCountLevel5": 0,
          "containerCountLevel6": 2,
          "litterCountLandfill": 2,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 4,
          "foulCount": 0,
          "autoPoints": 20,
          "totePoints": 40,
          "containerPoints": 60,
          "litterPoints": 18,
          "teleopPoints": 118,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 138
        },
        {
          "alliance": "Blue",
          "robotSet": true,
          "containerSet": true,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 6,
          "toteCountNear": 2,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 1,
          "containerCountLevel4": 0,
          "containerCountLevel5": 0,
          "containerCountLevel6": 0,
          "litterCountLandfill": 2,
          "litterCountContainer": 1,
          "litterCountUnprocessed": 4,
          "foulCount": 0,
          "autoPoints": 12,
          "totePoints": 16,
          "containerPoints": 12,
          "litterPoints": 24,
          "teleopPoints": 52,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 64
        }
      ]
    },
    {
      "matchLevel": "Playoff",
      "matchNumber": 6,
      "coopertition": "None",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 10,
          "toteCountNear": 5,
          "containerCountLevel1": 1,
          "containerCountLevel2": 0,
          "containerCountLevel3": 1,
          "containerCountLevel4": 0,
          "containerCountLevel5": 0,
          "containerCountLevel6": 0,
          "litterCountLandfill": 2,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 5,
          "foulCount": 0,
          "autoPoints": 0,
          "totePoints": 30,
          "containerPoints": 16,
          "litterPoints": 22,
          "teleopPoints": 68,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 68
        },
        {
          "alliance": "Blue",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 8,
          "toteCountNear": 13,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 2,
          "containerCountLevel5": 0,
          "containerCountLevel6": 0,
          "litterCountLandfill": 0,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 3,
          "foulCount": 0,
          "autoPoints": 0,
          "totePoints": 42,
          "containerPoints": 32,
          "litterPoints": 12,
          "teleopPoints": 86,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 86
        }
      ]
    },
    {
      "matchLevel": "Playoff",
      "matchNumber": 7,
      "coopertition": "None",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": true,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 5,
          "toteCountNear": 13,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 1,
          "containerCountLevel5": 0,
          "containerCountLevel6": 1,
          "litterCountLandfill": 0,
          "litterCountContainer": 1,
          "litterCountUnprocessed": 8,
          "foulCount": 0,
          "autoPoints": 4,
          "totePoints": 36,
          "containerPoints": 40,
          "litterPoints": 38,
          "teleopPoints": 114,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 118
        },
        {
          "alliance": "Blue",
          "robotSet": true,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 7,
          "toteCountNear": 6,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 1,
          "containerCountLevel4": 0,
          "containerCountLevel5": 1,
          "containerCountLevel6": 0,
          "litterCountLandfill": 0,
          "litterCountContainer": 2,
          "litterCountUnprocessed": 2,
          "foulCount": 0,
          "autoPoints": 4,
          "totePoints": 26,
          "containerPoints": 32,
          "litterPoints": 20,
          "teleopPoints": 78,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 82
        }
      ]
    },
    {
      "matchLevel": "Playoff",
      "matchNumber": 8,
      "coopertition": "None",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": true,
          "toteCountFar": 6,
          "toteCountNear": 12,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 0,
          "containerCountLevel5": 0,
          "containerCountLevel6": 3,
          "litterCountLandfill": 0,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 4,
          "foulCount": 0,
          "autoPoints": 20,
          "totePoints": 36,
          "containerPoints": 72,
          "litterPoints": 16,
          "teleopPoints": 124,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 144
        },
        {
          "alliance": "Blue",
          "robotSet": true,
          "containerSet": true,
          "toteSet": true,
          "toteStack": false,
          "toteCountFar": 4,
          "toteCountNear": 7,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 0,
          "containerCountLevel5": 0,
          "containerCountLevel6": 0,
          "litterCountLandfill": 2,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 7,
          "foulCount": 0,
          "autoPoints": 18,
          "totePoints": 22,
          "containerPoints": 0,
          "litterPoints": 30,
          "teleopPoints": 52,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 70
        }
      ]
    },
    {
      "matchLevel": "Playoff",
      "matchNumber": 9,
      "coopertition": "None",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": true,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 12,
          "toteCountNear": 10,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 1,
          "containerCountLevel4": 2,
          "containerCountLevel5": 0,
          "containerCountLevel6": 1,
          "litterCountLandfill": 0,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 7,
          "foulCount": 0,
          "autoPoints": 4,
          "totePoints": 44,
          "containerPoints": 68,
          "litterPoints": 28,
          "teleopPoints": 140,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 144
        },
        {
          "alliance": "Blue",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 10,
          "toteCountNear": 3,
          "containerCountLevel1": 0,
          "containerCountLevel2": 1,
          "containerCountLevel3": 0,
          "containerCountLevel4": 0,
          "containerCountLevel5": 1,
          "containerCountLevel6": 0,
          "litterCountLandfill": 0,
          "litterCountContainer": 2,
          "litterCountUnprocessed": 1,
          "foulCount": 0,
          "autoPoints": 0,
          "totePoints": 26,
          "containerPoints": 28,
          "litterPoints": 16,
          "teleopPoints": 70,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 70
        }
      ]
    },
    {
      "matchLevel": "Playoff",
      "matchNumber": 10,
      "coopertition": "None",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": true,
          "toteCountFar": 12,
          "toteCountNear": 12,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 0,
          "containerCountLevel5": 0,
          "containerCountLevel6": 4,
          "litterCountLandfill": 2,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 2,
          "foulCount": 0,
          "autoPoints": 20,
          "totePoints": 48,
          "containerPoints": 96,
          "litterPoints": 10,
          "teleopPoints": 154,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 174
        },
        {
          "alliance": "Blue",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": true,
          "toteCountFar": 7,
          "toteCountNear": 13,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 1,
          "containerCountLevel4": 0,
          "containerCountLevel5": 0,
          "containerCountLevel6": 1,
          "litterCountLandfill": 1,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 8,
          "foulCount": 0,
          "autoPoints": 20,
          "totePoints": 40,
          "containerPoints": 36,
          "litterPoints": 33,
          "teleopPoints": 109,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 129
        }
      ]
    },
    {
      "matchLevel": "Playoff",
      "matchNumber": 11,
      "coopertition": "None",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": true,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 10,
          "toteCountNear": 9,
          "containerCountLevel1": 1,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 1,
          "containerCountLevel5": 0,
          "containerCountLevel6": 0,
          "litterCountLandfill": 2,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 6,
          "foulCount": 0,
          "autoPoints": 4,
          "totePoints": 38,
          "containerPoints": 20,
          "litterPoints": 26,
          "teleopPoints": 84,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 88
        },
        {
          "alliance": "Blue",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": true,
          "toteCountFar": 5,
          "toteCountNear": 16,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 1,
          "containerCountLevel4": 0,
          "containerCountLevel5": 0,
          "containerCountLevel6": 2,
          "litterCountLandfill": 1,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 3,
          "foulCount": 0,
          "autoPoints": 20,
          "totePoints": 42,
          "containerPoints": 60,
          "litterPoints": 13,
          "teleopPoints": 115,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 135
        }
      ]
    },
    {
      "matchLevel": "Playoff",
      "matchNumber": 12,
      "coopertition": "None",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": true,
          "toteCountFar": 11,
          "toteCountNear": 12,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 0,
          "containerCountLevel5": 1,
          "containerCountLevel6": 3,
          "litterCountLandfill": 1,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 5,
          "foulCount": 0,
          "autoPoints": 20,
          "totePoints": 46,
          "containerPoints": 92,
          "litterPoints": 21,
          "teleopPoints": 159,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 179
        },
        {
          "alliance": "Blue",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 1,
          "toteCountNear": 7,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 0,
          "containerCountLevel5": 0,
          "containerCountLevel6": 1,
          "litterCountLandfill": 0,
          "litterCountContainer": 1,
          "litterCountUnprocessed": 5,
          "foulCount": 0,
          "autoPoints": 0,
          "totePoints": 16,
          "containerPoints": 24,
          "litterPoints": 26,
          "teleopPoints": 66,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 66
        }
      ]
    },
    {
      "matchLevel": "Playoff",
      "matchNumber": 13,
      "coopertition": "None",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": true,
          "toteCountFar": 13,
          "toteCountNear": 6,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 1,
          "containerCountLevel4": 1,
          "containerCountLevel5": 0,
          "containerCountLevel6": 1,
          "litterCountLandfill": 2,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 2,
          "foulCount": 0,
          "autoPoints": 20,
          "totePoints": 38,
          "containerPoints": 52,
          "litterPoints": 10,
          "teleopPoints": 100,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 120
        },
        {
          "alliance": "Blue",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 2,
          "toteCountNear": 9,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 2,
          "containerCountLevel5": 0,
          "containerCountLevel6": 0,
          "litterCountLandfill": 2,
          "litterCountContainer": 2,
          "litterCountUnprocessed": 2,
          "foulCount": 0,
          "autoPoints": 0,
          "totePoints": 22,
          "containerPoints": 32,
          "litterPoints": 22,
          "teleopPoints": 76,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 76
        }
      ]
    },
    {
      "matchLevel": "Playoff",
      "matchNumber": 14,
      "coopertition": "None",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": true,
          "toteCountFar": 10,
          "toteCountNear": 11,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 1,
          "containerCountLevel5": 1,
          "containerCountLevel6": 2,
          "litterCountLandfill": 0,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 5,
          "foulCount": 0,
          "autoPoints": 20,
          "totePoints": 42,
          "containerPoints": 84,
          "litterPoints": 20,
          "teleopPoints": 146,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 166
        },
        {
          "alliance": "Blue",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 7,
          "toteCountNear": 9,
          "containerCountLevel1": 1,
          "containerCountLevel2": 0,
          "containerCountLevel3": 2,
          "containerCountLevel4": 0,
          "containerCountLevel5": 1,
          "containerCountLevel6": 0,
          "litterCountLandfill": 0,
          "litterCountContainer": 1,
          "litterCountUnprocessed": 6,
          "foulCount": 0,
          "autoPoints": 0,
          "totePoints": 32,
          "containerPoints": 48,
          "litterPoints": 30,
          "teleopPoints": 110,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 110
        }
      ]
    },
    {
      "matchLevel": "Playoff",
      "matchNumber": 15,
      "coopertition": "None",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": true,
          "toteCountFar": 11,
          "toteCountNear": 11,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 0,
          "containerCountLevel5": 0,
          "containerCountLevel6": 2,
          "litterCountLandfill": 1,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 3,
          "foulCount": 0,
          "autoPoints": 20,
          "totePoints": 44,
          "containerPoints": 48,
          "litterPoints": 13,
          "teleopPoints": 105,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 125
        },
        {
          "alliance": "Blue",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 3,
          "toteCountNear": 16,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 1,
          "containerCountLevel4": 0,
          "containerCountLevel5": 0,
          "containerCountLevel6": 1,
          "litterCountLandfill": 1,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 2,
          "foulCount": 0,
          "autoPoints": 0,
          "totePoints": 38,
          "containerPoints": 36,
          "litterPoints": 9,
          "teleopPoints": 83,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 83
        }
      ]
    },
    {
      "matchLevel": "Playoff",
      "matchNumber": 16,
      "coopertition": "None",
      "coopertitionPoints": 0,
      "alliances": [
        {
          "alliance": "Red",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": true,
          "toteCountFar": 10,
          "toteCountNear": 11,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 1,
          "containerCountLevel5": 0,
          "containerCountLevel6": 2,
          "litterCountLandfill": 0,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 6,
          "foulCount": 0,
          "autoPoints": 20,
          "totePoints": 42,
          "containerPoints": 64,
          "litterPoints": 24,
          "teleopPoints": 130,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 150
        },
        {
          "alliance": "Blue",
          "robotSet": false,
          "containerSet": false,
          "toteSet": false,
          "toteStack": false,
          "toteCountFar": 5,
          "toteCountNear": 13,
          "containerCountLevel1": 0,
          "containerCountLevel2": 0,
          "containerCountLevel3": 0,
          "containerCountLevel4": 0,
          "containerCountLevel5": 0,
          "containerCountLevel6": 1,
          "litterCountLandfill": 3,
          "litterCountContainer": 0,
          "litterCountUnprocessed": 4,
          "foulCount": 0,
          "autoPoints": 0,
          "totePoints": 36,
          "containerPoints": 24,
          "litterPoints": 19,
          "teleopPoints": 79,
          "adjustPoints": 0,
          "foulPoints": 0,
          "totalPoints": 79
        }
      ]
    }
  ]
}
```

Last-Modified

sed in laboris

The date and time of when the response data was last modified on the server.

Content-Type

application/json

### GETQual Performance Points

https://frc-api.firstinspires.org/v3.0/:season/rankings/district/qualPerformanceCalculation

Qual Performance Points is one of three endpoints to assist teams in figuring out how to improve their performance to achieve the desired district ranking placement. It is to determine the Event Total points.

`tournamentType`, `sizeType`, `allianceNumber`, and `allianceRole` are all required parameters for the calculation to occur.

PARAMS

tournamentType

**\[REQUIRED\] (enum string)** Type of event to perform the calculation on.

Enum values:

View More

Plain Text

```plain
1. None
2. Regional
3. DistrictEvent
4. DistrictChampionship
5. DistrictChampionshipWithLevels
6. DistrictChampionshipDivision
7. ChampionshipSubdivision
8. ChampionshipDivision
9. Championship
10. OffSeason
11. OffSeasonWithAzureSync
12. Remote
```

qualificationRank

**\[REQUIRED\] (int)** Numbered rank of the desired team in the qualification matches.

teamsAtEvent

**\[REQUIRED\] (int)** Number of teams in the event.

PATH VARIABLES

season

2022

**\[REQUIRED\] (int)** Numeric year of the event from which the award listings are requested. Must be 4 digits and greater than or equal to 2015, and less than or equal to the current year.

Example Request

Qual Performance Points

View More

python

```python
import requests

url = "https://frc-api.firstinspires.org/v3.0/2022/rankings/district/qualPerformanceCalculation?tournamentType=Regional&qualificationRank=1&teamsAtEvent=64"

payload={}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

200 OK

Example Response

-   Body
-   Headers (4)

json

```json
22
```

Transfer-Encoding

chunked

Content-Type

application/json; charset=utf-8

Server

Microsoft-HTTPAPI/2.0

Date

Wed, 28 Jul 2021 19:40:53 GMT

### GETAlliance Selection Points

https://frc-api.firstinspires.org/v3.0/:season/rankings/district/allianceSelectionCalculation

Alliance Selection Points is one of three endpoints to assist teams in figuring out how to improve their performance to achieve the desired district ranking placement. It is to determine the Event Total points.

`tournamentType`, `sizeType`, `allianceNumber`, and `allianceRole` are all required parameters for the calculation to occur.

PARAMS

tournamentType

**\[REQUIRED\] (string)** Type of event to perform the calculation on.

Enum values:

Plain Text

```plain
1. None
2. Regional
3. DistrictEvent
4. DistrictChampionship
5. DistrictChampionshipWithLevels
6. DistrictChampionshipDivision
7. ChampionshipSubdivision
8. ChampionshipDivision
9. Championship
10. OffSeason
11. OffSeasonWithAzureSync
```

sizeType

**\[REQUIRED\] (string)** Number of alliances in the playoffs for the event.

Enum values:

Plain Text

```plain
1. TwoAlliance
2. FourAlliance
3. SixAlliance
4. EightAlliance
5. SixteenAlliance
```

allianceNumber

**\[REQUIRED\] (int)** The number of the playoff alliance the team is on.

allianceRole

**\[REQUIRED\] (string)** Team's role in the playoff alliance.

Enum values:

Plain Text

```plain
1. None
2. Captain
3. Round1
4. Round2
5. Round3
6. Backup
```

PATH VARIABLES

season

2022

**\[REQUIRED\] (int)** Numeric year of the event from which the award listings are requested. Must be 4 digits and greater than or equal to 2015, and less than or equal to the current year.

Example Request

Alliance Selection Points

View More

python

```python
import requests

url = "https://frc-api.firstinspires.org/v3.0/2022/rankings/district/allianceSelectionCalculation?tournamentType=Regional&sizeType=EightAlliance&allianceNumber=2&allianceRole=Captain"

payload={}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

200 OK

Example Response

-   Body
-   Headers (4)

json

```json
15
```

Transfer-Encoding

chunked

Content-Type

application/json; charset=utf-8

Server

Microsoft-HTTPAPI/2.0

Date

Wed, 28 Jul 2021 19:39:28 GMT

## 

Schedule

AUTHORIZATIONBasic Auth

This folder is using Basic Auth from collection[FRC Events](#auth-info-51a3938d-2026-4a5c-9f17-d87d035584cd)

### GETEvent Schedule

https://frc-api.firstinspires.org/v3.0/:season/schedule/:eventCode?tournamentLevel=&teamNumber=&start=&end=

The schedule API returns the match schedule for the desired tournament level of a particular event in a particular season. You must also specify a `tournamentLevel` from which to return the results. Alternately, you can specify a `teamNumber` to filter the results to only those in which a particular team is participating. There is no validation that the `teamNumber` you request is actually competing at the event, if they are not, the response will be empty. You can also specify the parameters together, but cannot make a request without at least one of the two.

AUTHORIZATIONBasic Auth

This request is using Basic Auth from collection[FRC Events](#auth-info-51a3938d-2026-4a5c-9f17-d87d035584cd)

HEADERS

If-Modified-Since

PARAMS

tournamentLevel

**(string)** tournamentLevel of desired match schedule.

Enum values:

Plain Text

```plain
1. None
2. Practice
3. Qualification
4. Playoff
```

teamNumber

**(int)** Optional teamNumber to search for within the schedule. Only returns matches in which the requested team participated.

start

**(int)** Optional start match number for subset of results to return (inclusive).

end

**(int)** Optional end match number for subset of results to return (inclusive).

PATH VARIABLES

season

2022

**\[REQUIRED\] (int)** Numeric year of the event from which the award listings are requested. Must be 4 digits and greater than or equal to 2015, and less than or equal to the current year.

eventCode

**\[REQUIRED\] (string)** Case insensitive alphanumeric eventCode of the event from which the schedule are requested. Must be at least 3 characters.

Example Request

Response

View More

python

```python
import requests

url = "https://frc-api.firstinspires.org/v3.0/2020/schedule/ARLI?tournamentLevel=Playoff"

payload={}
headers = {
  'Authorization': 'Basic <credentials>',
  'If-Modified-Since': ''
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

200 OK

Example Response

-   Body
-   Headers (2)

View More

json

```
{
  "Schedule": [
    {
      "field": "Primary",
      "tournamentLevel": "Playoff",
      "description": "Quarterfinal 1",
      "startTime": "2020-03-07T13:30:00",
      "matchNumber": 1,
      "teams": [
        {
          "teamNumber": 3937,
          "station": "Red1",
          "surrogate": false
        },
        {
          "teamNumber": 3959,
          "station": "Red2",
          "surrogate": false
        },
        {
          "teamNumber": 1723,
          "station": "Red3",
          "surrogate": false
        },
        {
          "teamNumber": 364,
          "station": "Blue1",
          "surrogate": false
        },
        {
          "teamNumber": 5006,
          "station": "Blue2",
          "surrogate": false
        },
        {
          "teamNumber": 2333,
          "station": "Blue3",
          "surrogate": false
        }
      ]
    },
    {
      "field": "Primary",
      "tournamentLevel": "Playoff",
      "description": "Quarterfinal 2",
      "startTime": "2020-03-07T13:37:00",
      "matchNumber": 2,
      "teams": [
        {
          "teamNumber": 5013,
          "station": "Red1",
          "surrogate": false
        },
        {
          "teamNumber": 537,
          "station": "Red2",
          "surrogate": false
        },
        {
          "teamNumber": 6055,
          "station": "Red3",
          "surrogate": false
        },
        {
          "teamNumber": 4265,
          "station": "Blue1",
          "surrogate": false
        },
        {
          "teamNumber": 4635,
          "station": "Blue2",
          "surrogate": false
        },
        {
          "teamNumber": 3250,
          "station": "Blue3",
          "surrogate": false
        }
      ]
    },
    {
      "field": "Primary",
      "tournamentLevel": "Playoff",
      "description": "Quarterfinal 3",
      "startTime": "2020-03-07T13:44:00",
      "matchNumber": 3,
      "teams": [
        {
          "teamNumber": 2992,
          "station": "Red1",
          "surrogate": false
        },
        {
          "teamNumber": 4336,
          "station": "Red2",
          "surrogate": false
        },
        {
          "teamNumber": 1912,
          "station": "Red3",
          "surrogate": false
        },
        {
          "teamNumber": 3039,
          "station": "Blue1",
          "surrogate": false
        },
        {
          "teamNumber": 1421,
          "station": "Blue2",
          "surrogate": false
        },
        {
          "teamNumber": 2080,
          "station": "Blue3",
          "surrogate": false
        }
      ]
    },
    {
      "field": "Primary",
      "tournamentLevel": "Playoff",
      "description": "Quarterfinal 4",
      "startTime": "2020-03-07T13:51:00",
      "matchNumber": 4,
      "teams": [
        {
          "teamNumber": 4087,
          "station": "Red1",
          "surrogate": false
        },
        {
          "teamNumber": 16,
          "station": "Red2",
          "surrogate": false
        },
        {
          "teamNumber": 4576,
          "station": "Red3",
          "surrogate": false
        },
        {
          "teamNumber": 2393,
          "station": "Blue1",
          "surrogate": false
        },
        {
          "teamNumber": 5568,
          "station": "Blue2",
          "surrogate": false
        },
        {
          "teamNumber": 6855,
          "station": "Blue3",
          "surrogate": false
        }
      ]
    },
    {
      "field": "Primary",
      "tournamentLevel": "Playoff",
      "description": "Quarterfinal 5",
      "startTime": "2020-03-07T13:58:00",
      "matchNumber": 5,
      "teams": [
        {
          "teamNumber": 3937,
          "station": "Red1",
          "surrogate": false
        },
        {
          "teamNumber": 3959,
          "station": "Red2",
          "surrogate": false
        },
        {
          "teamNumber": 1723,
          "station": "Red3",
          "surrogate": false
        },
        {
          "teamNumber": 364,
          "station": "Blue1",
          "surrogate": false
        },
        {
          "teamNumber": 5006,
          "station": "Blue2",
          "surrogate": false
        },
        {
          "teamNumber": 2333,
          "station": "Blue3",
          "surrogate": false
        }
      ]
    },
    {
      "field": "Primary",
      "tournamentLevel": "Playoff",
      "description": "Quarterfinal 6",
      "startTime": "2020-03-07T14:05:00",
      "matchNumber": 6,
      "teams": [
        {
          "teamNumber": 5013,
          "station": "Red1",
          "surrogate": false
        },
        {
          "teamNumber": 537,
          "station": "Red2",
          "surrogate": false
        },
        {
          "teamNumber": 6055,
          "station": "Red3",
          "surrogate": false
        },
        {
          "teamNumber": 4265,
          "station": "Blue1",
          "surrogate": false
        },
        {
          "teamNumber": 4635,
          "station": "Blue2",
          "surrogate": false
        },
        {
          "teamNumber": 3250,
          "station": "Blue3",
          "surrogate": false
        }
      ]
    },
    {
      "field": "Primary",
      "tournamentLevel": "Playoff",
      "description": "Quarterfinal 7",
      "startTime": "2020-03-07T14:12:00",
      "matchNumber": 7,
      "teams": [
        {
          "teamNumber": 2992,
          "station": "Red1",
          "surrogate": false
        },
        {
          "teamNumber": 4336,
          "station": "Red2",
          "surrogate": false
        },
        {
          "teamNumber": 1912,
          "station": "Red3",
          "surrogate": false
        },
        {
          "teamNumber": 3039,
          "station": "Blue1",
          "surrogate": false
        },
        {
          "teamNumber": 1421,
          "station": "Blue2",
          "surrogate": false
        },
        {
          "teamNumber": 6640,
          "station": "Blue3",
          "surrogate": false
        }
      ]
    },
    {
      "field": "Primary",
      "tournamentLevel": "Playoff",
      "description": "Quarterfinal 8",
      "startTime": "2020-03-07T14:19:00",
      "matchNumber": 8,
      "teams": [
        {
          "teamNumber": 4087,
          "station": "Red1",
          "surrogate": false
        },
        {
          "teamNumber": 16,
          "station": "Red2",
          "surrogate": false
        },
        {
          "teamNumber": 4576,
          "station": "Red3",
          "surrogate": false
        },
        {
          "teamNumber": 2393,
          "station": "Blue1",
          "surrogate": false
        },
        {
          "teamNumber": 5568,
          "station": "Blue2",
          "surrogate": false
        },
        {
          "teamNumber": 6855,
          "station": "Blue3",
          "surrogate": false
        }
      ]
    },
    {
      "field": "Primary",
      "tournamentLevel": "Playoff",
      "description": "Semifinal 1",
      "startTime": "2020-03-07T14:54:00",
      "matchNumber": 13,
      "teams": [
        {
          "teamNumber": 3937,
          "station": "Red1",
          "surrogate": false
        },
        {
          "teamNumber": 3959,
          "station": "Red2",
          "surrogate": false
        },
        {
          "teamNumber": 1723,
          "station": "Red3",
          "surrogate": false
        },
        {
          "teamNumber": 5013,
          "station": "Blue1",
          "surrogate": false
        },
        {
          "teamNumber": 537,
          "station": "Blue2",
          "surrogate": false
        },
        {
          "teamNumber": 6055,
          "station": "Blue3",
          "surrogate": false
        }
      ]
    },
    {
      "field": "Primary",
      "tournamentLevel": "Playoff",
      "description": "Semifinal 2",
      "startTime": "2020-03-07T15:01:00",
      "matchNumber": 14,
      "teams": [
        {
          "teamNumber": 2992,
          "station": "Red1",
          "surrogate": false
        },
        {
          "teamNumber": 4336,
          "station": "Red2",
          "surrogate": false
        },
        {
          "teamNumber": 1912,
          "station": "Red3",
          "surrogate": false
        },
        {
          "teamNumber": 4087,
          "station": "Blue1",
          "surrogate": false
        },
        {
          "teamNumber": 16,
          "station": "Blue2",
          "surrogate": false
        },
        {
          "teamNumber": 4576,
          "station": "Blue3",
          "surrogate": false
        }
      ]
    },
    {
      "field": "Primary",
      "tournamentLevel": "Playoff",
      "description": "Semifinal 3",
      "startTime": "2020-03-07T15:08:00",
      "matchNumber": 15,
      "teams": [
        {
          "teamNumber": 3937,
          "station": "Red1",
          "surrogate": false
        },
        {
          "teamNumber": 3959,
          "station": "Red2",
          "surrogate": false
        },
        {
          "teamNumber": 1723,
          "station": "Red3",
          "surrogate": false
        },
        {
          "teamNumber": 5013,
          "station": "Blue1",
          "surrogate": false
        },
        {
          "teamNumber": 537,
          "station": "Blue2",
          "surrogate": false
        },
        {
          "teamNumber": 6055,
          "station": "Blue3",
          "surrogate": false
        }
      ]
    },
    {
      "field": "Primary",
      "tournamentLevel": "Playoff",
      "description": "Semifinal 4",
      "startTime": "2020-03-07T15:15:00",
      "matchNumber": 16,
      "teams": [
        {
          "teamNumber": 2992,
          "station": "Red1",
          "surrogate": false
        },
        {
          "teamNumber": 4336,
          "station": "Red2",
          "surrogate": false
        },
        {
          "teamNumber": 1912,
          "station": "Red3",
          "surrogate": false
        },
        {
          "teamNumber": 4087,
          "station": "Blue1",
          "surrogate": false
        },
        {
          "teamNumber": 16,
          "station": "Blue2",
          "surrogate": false
        },
        {
          "teamNumber": 4576,
          "station": "Blue3",
          "surrogate": false
        }
      ]
    },
    {
      "field": "Primary",
      "tournamentLevel": "Playoff",
      "description": "Final 1",
      "startTime": "2020-03-07T15:36:00",
      "matchNumber": 19,
      "teams": [
        {
          "teamNumber": 3937,
          "station": "Red1",
          "surrogate": false
        },
        {
          "teamNumber": 3959,
          "station": "Red2",
          "surrogate": false
        },
        {
          "teamNumber": 1723,
          "station": "Red3",
          "surrogate": false
        },
        {
          "teamNumber": 4087,
          "station": "Blue1",
          "surrogate": false
        },
        {
          "teamNumber": 16,
          "station": "Blue2",
          "surrogate": false
        },
        {
          "teamNumber": 4576,
          "station": "Blue3",
          "surrogate": false
        }
      ]
    },
    {
      "field": "Primary",
      "tournamentLevel": "Playoff",
      "description": "Final 2",
      "startTime": "2020-03-07T15:43:00",
      "matchNumber": 20,
      "teams": [
        {
          "teamNumber": 3937,
          "station": "Red1",
          "surrogate": false
        },
        {
          "teamNumber": 3959,
          "station": "Red2",
          "surrogate": false
        },
        {
          "teamNumber": 1723,
          "station": "Red3",
          "surrogate": false
        },
        {
          "teamNumber": 4087,
          "station": "Blue1",
          "surrogate": false
        },
        {
          "teamNumber": 16,
          "station": "Blue2",
          "surrogate": false
        },
        {
          "teamNumber": 4576,
          "station": "Blue3",
          "surrogate": false
        }
      ]
    }
  ]
}
```

Last-Modified

sed in laboris

The date and time of when the response data was last modified on the server.

Content-Type

application/json