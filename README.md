Welcome to the ![AP Logo](https://s3.amazonaws.com/elapi.workshop/ap_logo.png) **Elections API** workshop!
====================================
**Table of contents:**

 - [Overview](#overview)
 - [Contact Information](#contact-information)
 - [Links](#links)
 - [Working with the Elections API](#working-with-the-elections-api)
 - [Why DataMaps?](#why-datamaps)
 - [Anatomy of a Choropleth](#anatomy-of-a-choropleth)
 - [Coding Exercise](#coding-exercise)
	- [Phase 1](#phase-1)
	- [Phase 2](#phase-2)
	- [Phase 3](#phase-3)
	- [Phase 4](#phase-4)

### Overview
**Disclaimer:** This workshop is intended to be accessible by anyone regardless of background or technical ability.

In this workshop we will be using Python to call AP's Elections API to fetch real-time election results and use the resulting data to render a static HTML page.

We will use an open-source library called [DataMaps](http://datamaps.github.io/) to display a [Choropleth](https://en.wikipedia.org/wiki/Choropleth_map) map.  
Choropleth maps are a great way of visualizing variance in a data set with regard to region.  

<p align="center">
	<img src="https://s3.amazonaws.com/elapi.workshop/ny_ge_2012_example.png" />
</p>

### Contact Information
Sam Cohen (sacohen@ap.org)  
John Young (jyoung@ap.org)  
Matt Della Volpe (mdellavolpe@ap.org)  

### Links
 [AP Developer Portal](https://developer.ap.org/ap-elections-api)  
 [Elections API 2.0 Documentation](http://customersupport.ap.org/doc/eln/AP_Elections_API_Developer_Guide.pdf)  
 [Elections API Query Explorer  - Requires an API Key](https://api.ap.org/v2/elections/xplor?apikey=YOUR_API_KEY_HERE)  
 [DataMaps](http://datamaps.github.io/)  
 [TopoJSON Details](https://github.com/mbostock/topojson)  
 [TopoJSON for each US State and it's counties](https://github.com/mattdellavolpe/US-Counties-TopoJSON)  
 [Hosting a Static Website from an Amazon S3 bucket](https://blog.hartleybrody.com/static-site-s3/)

### Working with the Elections API
**Basic Request Syntax**
```
https://api.ap.org/v2/elections/{electionDate}?apiKey={apiKey}[{OtherParameters}]
```

**Filtering by State**
```
https://api.ap.org/v2/elections/{electionDate}?apiKey={apiKey}&statepostal=ny,nj,ma
```
*Omitting state postal will return results for all states.*  

**Specifying Result Level**
```
https://api.ap.org/v2/elections/{electionDate}?apiKey={apiKey}&level=fipscode
```
Valid Levels:

- **State**: Returns the races for each of the specified
states, without the details for each of the reporting units.
- **RU**: Returns the races for both the specified states and each of the
reporting units within each state.
- **FIPScode**: Returns the races for both the specified states and each of the
FIPS codes within each state.
- **District**: Returns the races for both the specified states and each of the
districts within each state.

*Omitting level will return results at the state level*  

**Next Request Links**  
Every successful response includes a next-link.  

![Next Request Link](https://s3.amazonaws.com/elapi.workshop/next_request.png)

The next-link includes a timestamp indicating the update time of the results returned in the response.  Using next-links when making subsequent requests allows the API to return only the reporting unit elements that have been updated since the time of the previous request.


**Conditional Requests**  
Every successful request also includes the [HTTP headers](https://en.wikipedia.org/wiki/List_of_HTTP_header_fields) **ETag** and **Last-Modified**.

![Conditional Request Headers](https://s3.amazonaws.com/elapi.workshop/conditional_headers.png)

Passing these values as the headers **If-None-Match** and **If-Modified-Since** on subsequent requests allows the API to determine if any data has updated. If nothing has been updated, the API will return an empty response with a [status code 304 (Not Modified)](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes). If any results have been updated, the API will return the full payload with updated **ETag** and **Last-Modified** headers.

### Why DataMaps?
DataMaps is built upon the data driven visualization library [D3.js](https://github.com/mbostock/d3).  
While it is 100% reasonable to [use D3 directly for creating a Choropleth](http://bl.ocks.org/mbostock/4060606), DataMaps simplifies the process and can yield excellent results with minimal effort.  

### Anatomy of a Choropleth
Out of the box DataMaps supports the display of a US Choropleth at the state level as seen [here](https://github.com/markmarkoh/datamaps/blob/master/README.md#creating-a-choropleth).
However, our Choropleth will display the results of an on-going election at the county/FIPS code level.  This will require using a custom map with DataMaps as described [here](https://github.com/markmarkoh/datamaps/blob/master/README.md#using-custom-maps) and demonstrated [here](http://bl.ocks.org/markmarkoh/8856417).  

We will ultimately require 2 [JSON](https://en.wikipedia.org/wiki/JSON) documents to render our Choropleth:

 - **To render the map** we will need a [TopoJSON](https://en.wikipedia.org/wiki/GeoJSON#TopoJSON) document which describes the physical topology of the area.
  + The TopoJSON we will be using can be found [here](https://github.com/mattdellavolpe/US-Counties-TopoJSON/blob/master/5m/new_york.json).
 - **To shade the features of the map** we will need the election results for each FIPS Code/County in the region.

**Determing the fill color of the region**  
Each topological feature in our TopoJson uses the FIPS code of the county as it's ID.  
```json
{
   "type":"Polygon",
   "id":"36067",
   "properties": {
      "stateFIPS":"36",
      "state":"New York",
      "countyFIPS":"067",
      "name":"Onondaga",
      "statePostal":"NY"
   },
   "arcs": [
      [
         -110,
         169,
         -93,
         170
      ]
   ]
}
```

DataMaps uses the feature ID to determine the data object associated with the region/feature.  
The feature specific data will contain a 'fillKey' property which maps to a fill color.
```json
"data": {
  "36067": {
    "fillKey": "Dem",
    "precinctsReporting": "100.0%",
    "voteCount": "112,664",
    "candidate": "Barack Obama"
  }
}
```
*Any property in this object or in the TopoJSON feature can be referenced in the on-hover popup*  

The fill colors for each 'fillKey', as well as the default fill color, are defined in the options passed to DataMaps when the map is initialized.
```json
"fills": {
  "defaultFill": "#777777",
  "Dem": "#00B4FF",
  "GOP": "#FF4040"
}
```

### Coding Exercise
The Python script will go through several phases.  
Each phase will incrementally add a piece of functionality until we a have a script continuously and efficiently rendering our static HTML page only when the results have been updated.

### Phase 1
In this first phase, we will use the Python library [Requests](http://docs.python-requests.org/en/master/), to make an [HTTP GET](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods) request to the Elections API.  
*To install Requests, run '**pip install requests**' from the command line.*  

*Note: We will need to add an [API key](https://en.wikipedia.org/wiki/Application_programming_interface_key) to the URL to authenticate our request.*

### Phase 2
In this phase, we will update our script to transform the results returned from the Elections API into our own JSON which will be used in the next phase.

Our processing will have 3 steps:

- Create a [dictionary](https://en.wikipedia.org/wiki/Associative_array) to store our data for each county.
- Iterate through each FIPS code reporting unit object in the response
	+ Find the candidate with the most votes in that county
	+ Create another dictionary to store the candidate details and add it to the county dictionary using the FIPS code as the key
	+ Populate the second dictionary with details about the leading candidate
- Serialize the county dictionary into a JSON string and save it to a file

### Phase 3
In this phase, instead of saving the JSON to a file, we will inject the JSON into an HTML template and save the resulting HTML to a file.  
We will use Python's built in [string templating](https://docs.python.org/3.4/library/string.html#template-strings) to replace '$data' in the HTML template with the JSON string we are already producing.  

Once complete, you can preview the generated HTML by opening it with a web browser of your choice.

### Phase 4
Since we want to update our HTML as the results are updated, we will wrap our current workflow in a [While loop](https://en.wikipedia.org/wiki/While_loop).  
At the tail end of our loop, we will sleep long enough to keep us within our API quota limit.  
*Note: To throttle our calls more efficiently we could use something along the lines of  [this](https://gist.github.com/gregburek/1441055#gistcomment-1294264).*  

To avoid updating the HTML when results have not been updated since the previous iteration of the loop, we will use a conditional request when making our API calls.
