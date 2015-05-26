# -*- coding: utf-8 -*-
""" Sprint stats test script """

from IPython import embed
import json
from os import path
from pprint import pprint
import requests
from sys import exit
import yaml

### CONFIGURATION ###
#TODO accept the config.yml from the command line
config_file = path.join(path.dirname(path.realpath(__file__)), 'config/config_hc.yml')
if path.exists(config_file):
	config = yaml.load(open(config_file, 'r'))
else:
	print config_file + ' not found'
	exit()
#TODO verify the contents of the yaml file
server = config['server']
credentials = {'uname': config['username'], 'pword': config['password']}
api_url = server + '/api/latest'
search_url = api_url + '/search?'
agile_url = server + '/greenhopper/1.0'
rapid_url = agile_url + '/rapid/charts/velocity'
headers = {'content-type': 'application/json;charset=UTF-8'}
excluded_sprints = config['excluded_sprints']
filename = config['filename']
min_sprint = 0
board = config['board_id']

### METHODS ###
#TODO EXTRACT
def extract_sprint_data(url, creds, board, sprint):
	data_temp = {}
	url = url + '/rapid/charts/velocity'
	response = requests.get(url, headers=headers, auth=(creds['uname'], creds['pword']), params={'rapidViewId': board})
	if str(sprint) in response.json()['velocityStatEntries'].keys():
				for entry in response.json()['sprints']:
					if entry['id'] == int(sprint):
						data_temp['name'] = entry['name'].replace(' Sprint', '')
				data_temp['committed'] = response.json()['velocityStatEntries'][str(sprint)]['estimated']['value']
				data_temp['completed'] = response.json()['velocityStatEntries'][str(sprint)]['completed']['value']

	sprint_issues = get_sprint_issues(credentials, agile_url, board, sprint)

	data_dict = {
			'incomplete': 'incompletedIssues',
			'removed': 'puntedIssues',
			'added': 'issueKeysAddedDuringSprint'
		}
	
	for key, value in data_dict.iteritems():
		#TODO create a class for this
		try:
			if key == 'added':
				data_temp[key] = sum_issues(get_issues(credentials, search_url, sprint_issues, value))
			else:
				data_temp[key] = sum_issues(get_issues(credentials, search_url, sprint_issues, value))
		except Exception as e:
			data_temp[key] = 0
	return data_temp


def get_issues(creds, url, data, field):
	if isinstance(data[field], dict):
		params = {
			'jql': 'issuekey in (' + ', '.join(data[field]) + ')',
			'maxResults': len(data[field])
		}
		
	elif isinstance(data[field], list):
		key_list = []
		for entry in data[field]:
			key_list.append(entry['key'])
		params = {
			'jql': 'issuekey in (' + ', '.join(key_list) + ')',
			'maxResults': len(data[field])
		}
	else:
		return
	return requests.get(url, headers=headers, auth=(creds['uname'], creds['pword']), params=params).json()


def get_keys(data, value):
	issues = []
	for entry in data[value]:
		issues.append(entry['key'])
	return issues


def get_sprints(creds, url, board, sprints, excluded, sprint_min):
	for entry in requests.get(url, headers=headers, auth=(creds['uname'], creds['pword']), params={'rapidViewId': board}).json()['sprints']:
		if ((entry['id'] >= sprint_min) and (entry['id'] not in excluded) and entry['id'] not in sprints):
			sprints.append(entry['id'])
	return sorted(sprints)


def get_sprint_issues(creds, url, board, sprint):
	url = url + '/rapid/charts/sprintreport'
	params = {'rapidViewId': board, 'sprintId': sprint}
	return requests.get(url, headers=headers, auth=(creds['uname'], creds['pword']), params=params).json()['contents']


def sum_issues(issues):
	issue_sum = 0.0
	for issue in issues['issues']:
		try:
			issue_sum += float(issue['fields']['customfield_10004'])
		except Exception as e:
			pass
	return int(issue_sum)


### MAIN ###
if __name__ == '__main__':
	### Load cached data
	filename = path.join(path.dirname(path.realpath(__file__)), 'sprint_stats/data/' + filename)
	if path.exists(filename):
		with open(filename, 'rb') as data_file:
			import_data = json.load(data_file)
	else:
		print filename + ' not found, creating.'
		import_data = {}

	### Get the sprint data
	sprints = []
	# sprints = [53, 58, 59, 69, 72, 80, 85, 92, 96, 98, 99, 107, 110, 115, 118]

	if len(import_data) > 0:
		for key in import_data.keys():
			sprints.append(int(key))

	sprint_ids = sorted(list(set(sprints + get_sprints(credentials, rapid_url, board, sprints, excluded_sprints, min_sprint))))

	sprint_info = {}
	for sprint in sprint_ids:
		print 'Processing sprint ' + str(sprint)
		### Get the sprit data	
		sprint_data = extract_sprint_data(agile_url, credentials, board, sprint)

		### Calculate the sprint stats
		sprint_stats = {}

		### Add it to the info
		#TODO check if it is present first
		sprint_info[sprint] = {'data': sprint_data, 'stats': sprint_stats}

	pprint(sprint_info)
