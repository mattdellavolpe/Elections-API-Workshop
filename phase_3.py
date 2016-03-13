import requests
import json
from string import Template

api_key = 'YOUR_API_KEY_HERE'
request_url = 'http://api.ap.org/v2/elections/2012-11-06?level=fipscode&format=json&officeid=p&statepostal=ny'
template_filename = 'templates/new_york.html'
output_filename = 'output_phase_3.html'


def call_elections_api():
    # add our api key to the request url
    url_with_key = '{}&apikey={}'.format(request_url, api_key)

    # issue the request and return the response
    return requests.get(url_with_key)


def process_data(data):
    counties = {}
    for race in data['races']:
        for reporting_unit in race['reportingUnits']:
            if reporting_unit['level'] == 'FIPSCode':
                # find the candidate with the most votes
                leading_candidate = max(reporting_unit['candidates'], key=lambda candidate: candidate['voteCount'])

                # get the numeric fipscode
                fipscode = reporting_unit['fipsCode']

                # create a dictionary to hold the candidate details using the fipscode as the key
                counties[fipscode] = {}

                # add the formatted precincts reporting percent
                counties[fipscode]['precinctsReporting'] = '{}%'.format(reporting_unit['precinctsReportingPct'])

                if leading_candidate['voteCount'] > 0:

                    # map the fillKey of the fipscode to the party of the candidate with the most votes
                    counties[fipscode]['fillKey'] = leading_candidate['party']

                    # python string formatting => https://docs.python.org/2/library/string.html#format-examples
                    # add the candidates name
                    counties[fipscode]['candidate'] = '{} {}'.format(leading_candidate['first'], leading_candidate['last'])

                    # add the formatted vote count
                    counties[fipscode]['voteCount'] = '{:,}'.format(leading_candidate['voteCount'])

    # convert our dictionary to a JSON string
    json_string = json.dumps(counties, indent=2)

    # fetch the contents of the html template
    with open(template_filename, 'r') as template_file:
        html_template_string = template_file.read()

    # create the html template
    html_template = Template(html_template_string)

    # substitue $data with our json
    html_string = html_template.substitute(data=json_string)

    # save the html string to a file
    with open(output_filename, 'w') as output_file:
        output_file.write(html_string)


if __name__ == '__main__':
    # call the election's api
    response = call_elections_api()

    if response.status_code == requests.codes.ok:
        # load the data using request's builtin JSON decoder
        data = response.json()

        # process the data
        process_data(data)

    elif response.status_code == requests.codes.unauthorized:
        print('Statuscode: {} - Check your API key!'.format(response.status_code))

    else:
        print('Unexpected Statuscode: {}'.format(response.status_code))
