# -*- coding: utf-8 -*-

import requests
import pprint

headers = {'content-type': 'application/json;charset=UTF-8'}

def get_issues(creds, url, data):
	params = {
			'jql': 'issuekey in (' + ', '.join(data) + ')',
			'maxResults': len(data)
		}

	response = requests.get(url, headers=headers, auth=(creds['uname'], creds['pword']), params=params)

	return response.json()


def get_sprints(creds, url, board, excluded):
	sprints = [95, 104, 105, 106, 109]
	params = {'rapidViewId': board}
	response = requests.get(url, headers=headers, auth=(creds['uname'], creds['pword']), params=params)

	for entry in response.json()['sprints']:
		if ((entry['id'] not in sprints) and (entry['id'] not in excluded)):
			sprints.append(entry['id'])

	print sorted(sprints)
	return sorted(sprints)


def get_sprint_issues(creds, url, board, sprint):
	"""
		Takes:
			creds as a dict with uname, and pword
			url of the agile jira api
			board id of interest
			sprint id of interest
		Returns:
			Json response containing all the sprint issues and their metadata
	"""
	url = url + '/rapid/charts/sprintreport'
	params = {'rapidViewId': board, 'sprintId': sprint}
	response = requests.get(url, headers=headers, auth=(creds['uname'], creds['pword']), params=params)
	
	return response.json()['contents']


def sum_issues(issues):
	issue_sum = 0.0
	for issue in issues['issues']:
		try:
			issue_sum += float(issue['fields']['customfield_10004'])
		except Exception as e:
			pass

	return issue_sum