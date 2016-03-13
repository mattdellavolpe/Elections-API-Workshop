import requests
import json

api_key = 'YOUR_API_KEY_HERE'
request_url = 'http://api.ap.org/v2/elections/2012-11-06?level=fipscode&format=json&officeid=p&statepostal=ny'
output_filename = 'output_phase_1.json'


def call_elections_api():
    # add our api key to the request url
    url_with_key = '{}&apikey={}'.format(request_url, api_key)

    # issue the request and return the response
    return requests.get(url_with_key)


def process_data(data):
    # convert our dictionary to a JSON string
    json_string = json.dumps(data, indent=2)

    # save the html string to a file
    with open(output_filename, 'w') as output_file:
        output_file.write(json_string)


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
