Pulls sprint data from Jira (Only, currently), and then calculates statistics about the sprints.

Configuration
1. Change the name of the "config.YAML" file in the /config folder to "config.yml"
2. Open the config.yml file and add
* 	The base URL of your jira server
* 	Your Jira username into "username"
* 	Your Jira password into "password"
* 	The sprint board you are interested into board_id
* 	Any sprint ids that you want to exclude from the calcs into excluded_sprints