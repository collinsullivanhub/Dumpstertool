import sys
import csv
import json
import inquirer
import requests
from termcolor import colored, cprint
from thousandeyes_art import print_art
from dnsdumpster.DNSDumpsterAPI import DNSDumpsterAPI


def get_dumpster_results(user_input):
    vpn_list = []
    api_list = []
    print(f"[*] Populating results for: {user_input}")
    res = DNSDumpsterAPI(True).search(f'{user_input}')
    dns_results = res['dns_records']['dns']
    host_results = res['dns_records']['host']
    print("Authoritative Servers")
    for result in dns_results:
        domain = result['domain']
        ip = result['ip']
        print(colored(f'{domain}', 'yellow'), colored(f'{ip}', 'white'))
    print("Host Records")
    for result in host_results:
        domain = result['domain']
        ip = result['ip']
        print(colored(f'{domain}', 'yellow'), colored(f'{ip}', 'white'))
        domain_list.append(domain)


def create_tests():
    '''
    Create tests for target account group. There are common HTTP, Page Load, DNS Provider, and CDN Provider
    tests that are templated in this function. The target group of tests to be created are those which are
    scrubbed from DNSDumpster and then selected for use.
    '''
    http_server_endpoint = "https://api.thousandeyes.com/v6/tests/http-server/new.json?aid=1068226"
    page_load_endpoint = "https://api.thousandeyes.com/v6/tests/page-load/new.json"
    dns_server_endpoint = "https://api.thousandeyes.com/v6/tests/dns-server/new.json"

    #Google, AWS EC2+Console, Github, microsoftonline, Okta, Oracle Cloud, Salesforce, Webex, Zoom
    common_http_targets = ['https://www.google.com', 'https://console.aws.amazon.com/console/home', 'https://ec2.us-east-1.amazonaws.com',
    'https://ec2.us-east-2.amazonaws.com', 'https://ec2.us-west-1.amazonaws.com',
    'https://ec2.us-west-2.amazonaws.com', 'https://github.com', 'https://login.microsoftonline.com',
    'https://login.okta.com/', 'https://cloud.oracle.com/en_US/sign-in', 'https://ap0.salesforce.com']

    common_collab_targets = ['https://zoom.us/', 'http://global-nebulas.webex.com', 'https://teams.microsoft.com']
    common_cdn_provider_targets = ['https://dash.cloudflare.com/login', 'https://control.akamai.com/apps/auth', 'https://manage.fastly.com/auth/sign-in']
    common_dns_provider_targets = ['']

    for x in final_target_list_scrubbed:
        print(f"Creating test for: {x}")

        payload = {
                "testName": f"{x}",
                "interval": 300,
                "agents": [
                    {"agentId": 1120}
                ],
                "url": f"{x}"

        }
        headers = {"content-type": "application/json"}
        try:
            result = requests.post
            result = requests.post(
                http_server_endpoint,
                data=json.dumps(payload),
                headers=headers,
                auth=(email, api_token),
            )
            if result.status_code != 201:
                print("[*] Error: Non-201 response code...")
            else:
                print(f"[*] Test successfully created: {x}")
        except Exception as e:
            print("[*] Error creating test: {}".format(e))


def list_account_groups():
    #List Account Groups as SEs emails are likely tied to many
    api_endpoint = "https://api.thousandeyes.com/v6/account-groups.json"
    print("[*] Listing account groups...")
    ags = requests.get(api_endpoint, auth=(email, api_token))
    query = ags.json()['accountGroups']
    for ag in query:
        accountGroupName = ag['accountGroupName']
        aid = ag['aid']
        print(colored(f'{accountGroupName}', 'cyan'), colored(f'{aid}', 'white'))


def format_target_domains():
    #Adds proper URL formatting for HTTP-Server, Page Load, and Transaction Tests (Web Layer)
    for x in final_target_list:
        y = ("https://" + x)
        final_target_list_scrubbed.append(y)


if __name__ == '__main__':

    email = 'collsull@cisco.com'
    api_token = '2trbhwc2oyo072engbh9zaiogl3ipa7b'

    global domain_list
    domain_list = []

    east_coast_agents = [108963, 653646, 275, 63, 66, 67]
    central_agents = [64, 93732, 16769, 27674, 411061]
    west_coast_agents = [14410, 54581, 145, 59220, 9765]
    us_cloud_agents = [108963, 653646, 275, 63, 66, 67, 64, 93732, 16769, 27674, 411061, 14410, 54581, 145, 59220, 9765]
    eu_cloud_agents = [315226, 315221, 600196, 600201, 32, 1619, 721036]

    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help="Target Domain")
    parser.add_argument('-c', help="Create Tests In Target Account Group", action="store_true")
    parser.add_argument('-ag', help="Target Account Group", action="store_true")
    parser.add_argument('-ec', help="Assign East Coast Cloud Agents", action="store_true")
    parser.add_argument('-wc', help="Assign West Coast Cloud Agents", action="store_true")
    parser.add_argument('-us', help="Assign US Cloud Agents", action="store_true")
    parser.add_argument('-eu', help="Assign EU Cloud Agents", action="store_true")
    parser.add_argument('-ag', help="Target Account Group to Create Tests", action="store_true")
    args = parser.parse_args()
    '''
    api_endpoint = 'https://api.thousandeyes.com/v6/tests.json'
    print_art()
    list_account_groups()
    print(" ")
    ag_input = input("Please enter target Account Group ID: ")
    target_domain_input = input("Please enter target domain to scrape: ")
    get_dumpster_results(target_domain_input)
    print(" ")
    domain_choices = [inquirer.Checkbox('domainz', message="[*] Select which domains to create tests for: ",
    choices=domain_list)]
    answers = inquirer.prompt(domain_choices)
    questions = [inquirer.Checkbox('assigned_agents', message="[*] Select Agent options for tests: ",
    choices=['Assign East Coast Cloud Agents', 'Assign West Coast Cloud Agents', 'Assign Common SAAS Targets', 'Assign Common CDN Targets',
     'Assign US Cloud Agents','Assign EU Cloud Agents'])]
    print(answers['domainz'])
    final_target_list = answers['domainz']
    final_target_list_scrubbed = []
    answers = inquirer.prompt(questions)  # returns a dict
    print(answers['assigned_agents'])
    format_target_domains()
    print(final_target_list_scrubbed)

    #create_tests()
