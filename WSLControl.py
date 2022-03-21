from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin
from zeep import helpers
from requests import Session
from requests.auth import HTTPBasicAuth
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from lxml import etree
import json
from pykeepass import PyKeePass

#I keep the password stored in a keepass database, so just change this to your information or you can put the username and password directly in the script
database = PyKeePass('database.kdbx', keyfile='key.key')
entry = database.find_entries(title="Cisco Call Manager", first=True)
ucHost = "hostname"
ucAdmin = entry.username
ucPswd = entry.password
disable_warnings(InsecureRequestWarning)
# If you're not disabling SSL verification, host should be the FQDN of the server rather than IP
 
#I have the WSDL file linked to the current folder -> schema -> current -> AXLAPI.wsdl and you will need to download this from call manager, there should be a guide online. 	
wsdl = './schema/current/AXLAPI.wsdl'
location = 'https://{host}:8443/axl/'.format(host=ucHost)
binding = "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding"
 
# Create a custom session to disable Certificate verification.
# In production you shouldn't do this, 
# but for testing it saves having to have the certificate in the trusted store.
session = Session()
session.verify = False
session.auth = HTTPBasicAuth(ucAdmin, ucPswd)
 
transport = Transport(cache=SqliteCache(), session=session, timeout=20)
history = HistoryPlugin()
client = Client(wsdl=wsdl, transport=transport, plugins=[history])
service = client.create_service(binding, location)
 
def show_history():
    for item in [history.last_sent, history.last_received]:
        print(etree.tostring(item["envelope"], encoding="unicode", pretty_print=True))
    #return etree.tostring(item["envelope"], encoding="unicode", pretty_print=True)
#try:
#    resp = service.listPhone(searchCriteria={'name': devicename}, 
#                             returnedTags={'name': '', 'description': ''})
#    print(resp)
#except Fault:
#    show_history()

def update_hookswitch(devicename):
    """#update_hookswitch("FFFF2222FF22")
    """
    try:
        hookswitch = etree.fromstring('<ehookEnable>1</ehookEnable>')
        resp = service.updatePhone(**{'name':devicename, 'vendorConfig': hookswitch})
        #print(resp)
    except Fault:
        show_history()
    return resp
def getline():
  #this was a test and not used
    try:
        resp = service.getLine(**{'pattern':"5432", 'routePartitionName': {
                '_value_1': 'route_IL',}})
        #print(resp)
    except Fault:
        show_history()
    return resp
def getphone_Description(desc):
  #still working on this one
    resp = ''

    try:
        resp = service.listPhone(searchCriteria={'description': "%" + desc + "%"}, returnedTags={'dnOrPattern':"%", "name":"%" ,'partition':"%",'type':"%",'routeDetail':"%"})
        #searchCriteria={'dnOrPattern': "%",'partition':"%", 'type':"%"}, returnedTags={'dnOrPattern':"%",'partition':"%",'type':"%",'routeDetail':"%"}
        #print(resp)
        return helpers.serialize_object(resp)
    except Fault:
        print("There was an error, show_history() to display this")
    return resp
def getphone(mac):
    resp = ''
    try:
        resp = service.getPhone(**{'name': mac})

        #print(resp)
        return helpers.serialize_object(resp)
    except Fault:
        print("There was an error, show_history() to display this")
    return resp
def phoneModel(phone_model):
    try:
        if "7912" in phone_model:
            print("7912")
            phone_model = "7912"
        elif "7821" in phone_model:
            print("7821")
            phone_model = "7821"
        elif "7942" in phone_model:
            print("7942")
            phone_model = "7942"
        elif "7962" in phone_model:
            print("7962")
            phone_model = "7962"
        elif "8811" in phone_model:
            print("8811")
            phone_model = "8811"
        elif "8841" in phone_model:
            print("8841")
            phone_model = "8841"
        elif "8851" in phone_model:
            print("8851") 
            phone_model = "8851"
        elif not phone_model:
            phone_model = "8811"
        else:
            print(phone_model)
            raise ValueError("not a valid model: " + phone_model)
        return phone_model
    except Exception as e:
        print(e)
        print("no model")
def getRouteList():
    searchCriteria = {
    'searchCriteria': {
        'dnOrPattern': "%"
    },
    'returnedTags': {
            'dnOrPattern':"?",
            'partition':"?",
            'type':"?",
            'routeDetail':"?"
        }
    }
    try:
        #resp = service.RoutePlan()
        resp = service.listRoutePlan(searchCriteria={'dnOrPattern': "%",'partition':"%", 'type':"%"}, returnedTags={'dnOrPattern':"%",'partition':"%",'type':"%",'routeDetail':"%"})
        return(resp)
    except Fault:
        show_history()
    return resp

def add_Line(pattern, line_desc, ILPartition, forwarding_css, phone_desc, location, calling_rights):
    #print("add line")
    
    #'routePartitionName': {'_value_1': 'USWLK_IL1'}

    addline = {
    'line': {
        'pattern': pattern,
        'description': phone_desc,
        'usage': 'Device',
        'routePartitionName': ILPartition,
        'callForwardAll': {
                'forwardToVoiceMail': 'false',
                'callingSearchSpaceName': {
                    '_value_1': forwarding_css
                }
        },
        'alertingName': line_desc,
        'shareLineAppearanceCssName': {
                '_value_1': calling_rights
            },
            'voiceMailProfileName': {
                '_value_1': location
            },
        'callForwardBusy': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardBusyInt': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardNoAnswer': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardNoAnswerInt': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardNoCoverage': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardNoCoverageInt': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardOnFailure': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardNotRegistered': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardNotRegisteredInt': {
                'forwardToVoiceMail': 'true'
            }
    }
    }
    updateline = {
        'pattern': pattern,
        'description': phone_desc,
        'routePartitionName': ILPartition,
        'callForwardAll': {
                'forwardToVoiceMail': 'false',
                'callingSearchSpaceName': {
                    '_value_1': forwarding_css
                }
        },
        'alertingName': line_desc,
        'asciiAlertingName': '',
        'shareLineAppearanceCssName': {
                '_value_1': calling_rights
            },
            'voiceMailProfileName': {
                '_value_1': location
            },
        'callForwardBusy': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardBusyInt': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardNoAnswer': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardNoAnswerInt': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardNoCoverage': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardNoCoverageInt': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardOnFailure': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardNotRegistered': {
                'forwardToVoiceMail': 'true'
            },
            'callForwardNotRegisteredInt': {
                'forwardToVoiceMail': 'true'
            }
    }
    req = ""
    try:
        req = service.addLine(**addline)
        #print("Successfully created phone line")
    except Fault:
        show_history()
        try:
            req = service.updateLine(**updateline)
            #print("Successfully updated the existing phone line")
        except Fault:
            show_history()
    return req
def add_Phone(mac_address, ext, phone_desc, line_desc, line_label, ILPartition, calling_rights, device_pool, location, username, mask, phonetype):
    #print("add phone")
	
	#//set the route partition to the desired one
    hookswitch = etree.fromstring('<ehookEnable>1</ehookEnable>')
  	#//Create request variable
    #AddLineReq createLineReq = new AddLineReq();
    phoneTemplateName = ""
    securityProfileName = ""
    sipProfileName = ""
    protocol = ""
    product = ""
    if username == "":
        username = None
    
    if phonetype == "7912":
        securityProfileName = 'Security Profile-3'
        sipProfileName = ''
        phoneTemplateName = 'Standard 7912 SCCP'
        hookswitch = ""
        product = "Cisco 7912"
        protocol = "SCCP"
    elif phonetype == "7942":
        securityProfileName = 'Cisco 7942 - Standard SCCP Non-Secure Profile'
        sipProfileName = ''
        phoneTemplateName = '7942 1L1S'
        product = "Cisco 7942"
        protocol = "SCCP"
    elif phonetype == "7962":
        securityProfileName = 'Cisco 7962 - Standard SCCP Non-Secure Profile'
        sipProfileName = ''
        phoneTemplateName = 'HBF 7962G 1L-5S'
        product = "Cisco 7962"
        protocol = "SCCP"
    elif phonetype == "7821":
        securityProfileName = 'Cisco 7821 - Standard SIP Non-Secure Profile'
        sipProfileName = "Standard SIP Profile"
        phoneTemplateName = 'Standard 7821 SIP'
        product = "Cisco 7821"
        protocol = "SIP"
    elif phonetype == "8811":
        phoneTemplateName = "HBF 8811 SIP 1L 4S"
        securityProfileName = "Cisco 8811 - Standard SIP Non-Secure Profile"
        sipProfileName = "Standard SIP Profile"
        product = "Cisco 8811"
        protocol = "SIP"
    elif phonetype == "8841":
        phoneTemplateName = "HBF 8811 SIP 1L 4S"
        securityProfileName = 'Cisco 8841 - Standard SIP Non-Secure Profile'
        sipProfileName = "Standard SIP Profile"
        product = "Cisco 8841"
        protocol = "SIP"
    elif phonetype == "8851":
        phoneTemplateName = "HBF 8811 SIP 1L 4S"
        securityProfileName = 'Cisco 8851 - Standard SIP Non-Secure Profile'
        sipProfileName = "Standard SIP Profile"
        product = "Cisco 8851"
        protocol = "SIP"
    elif phonetype == "IP COMMUNICATOR":
        phoneTemplateName = 'Standard CIPC SCCP'
        securityProfileName = 'Cisco IP Communicator - Standard SCCP Non-Secure Profile'
        sipProfileName = None
        product = "Cisco IP Communicator"
        protocol = "SCCP"
        hookswitch = ""
    elif phonetype == "JABBER":
        securityProfileName = 'Cisco Unified Client Services Framework - Standard SIP Non-Secure Profile'
        sipProfileName = 'Standard SIP Profile'
        phoneTemplateName = 'Standard Client Services Framework'
        hookswitch = ""
        product = "Cisco Unified Client Services Framework"
        protocol = "SIP"
    else:
        securityProfileName = "HBF 8811 SIP 1L 4S"
        sipProfileName = 'Cisco 8811 - Standard SIP Non-Secure Profile'
        phoneTemplateName = "HBF 8811 SIP 1L 4S"
        product = "Cisco 8811"
        protocol = "SIP"

    if phonetype == "JABBER" or phonetype == "IP COMMUNICATOR":
        phone = {
                'phone': {
                "name": mac_address,
                "description": phone_desc,
                "product": product,
                "class": "Phone",
                "protocol": protocol,
                "protocolSide": "User",
                'ownerUserName': username,
                "callingSearchSpaceName": calling_rights,
                "devicePoolName": device_pool,
                "lines": {"line": {"index": 1,
                                "label": line_label,
                                "display": line_desc,
                                "dirn": {"pattern": ext,
                                            "routePartitionName": ILPartition},
                                'e164Mask': mask,
                                'mwlPolicy': 'Use System Policy',
                                'maxNumCalls': 6,
                                'busyTrigger': 2,
                                'displayAscii': ' ',
                                            
                                            }
                                            },
                "commonPhoneConfigName": "Standard Common Phone Profile",
                'locationName': location,
                "useTrustedRelayPoint": "Default",
                "phoneTemplateName": phoneTemplateName,
                "primaryPhoneName": None,
                "softkeyTemplateName": "Standard User IDivert",
                "securityProfileName": securityProfileName,
                "sipProfileName": sipProfileName,
                "builtInBridgeStatus": "Default",
                "packetCaptureMode" : '',
                "certificateOperation": "No Pending Operation",
                "deviceMobilityMode": "Default",
            }
            }
    else:
        phone = {
                'phone': {
                "name": mac_address,
                "description": phone_desc,
                "product": product,
                "class": "Phone",
                "protocol": protocol,
                "protocolSide": "User",
                'ownerUserName': username,
                "callingSearchSpaceName": calling_rights,
                "devicePoolName": device_pool,
                "lines": {"line": {"index": 1,
                                "label": line_label,
                                "display": line_desc,
                                "dirn": {"pattern": ext,
                                            "routePartitionName": ILPartition},
                                'e164Mask': mask,
                                'mwlPolicy': 'Use System Policy',
                                'maxNumCalls': 6,
                                'busyTrigger': 2,
                                'displayAscii': ' ',
                                            
                                            }
                                            },
                "commonPhoneConfigName": "Standard Common Phone Profile",
                'locationName': location,
                "useTrustedRelayPoint": "Default",
                "phoneTemplateName": phoneTemplateName,
                "primaryPhoneName": None,
                "softkeyTemplateName": "Standard User IDivert",
                "securityProfileName": securityProfileName,
                "sipProfileName": sipProfileName,
                "builtInBridgeStatus": "Default",
                "packetCaptureMode" : '',
                "certificateOperation": "No Pending Operation",
                "deviceMobilityMode": "Default",
                'vendorConfig': hookswitch
            }
            }
    req = ''
    print("Here's the phone we are creating:")
    print(phone)
    try:
        req = service.addPhone(**phone)
        #print(req)
    except Fault:
        show_history()
    return req
def remove_Phone(name):
    req = ''
    try:
        req = service.removePhone(**{'name':name})
        #print(req)
    except Fault:
        show_history()
    return req
def update_Phone(mac_address, ext, phone_desc, line_desc, line_label, ILPartition, calling_rights, device_pool, location, username, mask, phonetype):
    hookswitch = etree.fromstring('<ehookEnable>1</ehookEnable>')
    #//Create request variable
    #AddLineReq createLineReq = new AddLineReq();
    phoneTemplateName = ""
    securityProfileName = ""
    sipProfileName = ""
    if phonetype == "7912":
        securityProfileName = 'Security Profile-3'
        sipProfileName = ''
        phoneTemplateName = 'Standard 7912 SCCP'
        hookswitch = ""
    elif phonetype == "7942":
        securityProfileName = 'Cisco 7942 - Standard SCCP Non-Secure Profile'
        sipProfileName = ''
        phoneTemplateName = '7942 1L1S'
    elif phonetype == "7962":
        securityProfileName = 'Cisco 7962 - Standard SCCP Non-Secure Profile'
        sipProfileName = ''
        phoneTemplateName = 'HBF 7962G 1L-5S'
    elif phonetype == "7821":
        securityProfileName = 'Cisco 7821 - Standard SIP Non-Secure Profile'
        sipProfileName = "Standard SIP Profile"
        phoneTemplateName = 'Standard 7821 SIP'
    elif phonetype == "8811":
        phoneTemplateName = "HBF 8811 SIP 1L 4S"
        securityProfileName = "Cisco 8811 - Standard SIP Non-Secure Profile"
        sipProfileName = "Standard SIP Profile"
    elif phonetype == "8841":
        phoneTemplateName = "HBF 8811 SIP 1L 4S"
        securityProfileName = 'Cisco 8841 - Standard SIP Non-Secure Profile'
        sipProfileName = "Standard SIP Profile"
    elif phonetype == "8851":
        phoneTemplateName = "HBF 8811 SIP 1L 4S"
        securityProfileName = 'Cisco 8851 - Standard SIP Non-Secure Profile'
        sipProfileName = "Standard SIP Profile"
    elif phonetype == "CIPC":
        securityProfileName = 'Cisco IP Communicator - Standard SCCP Non-Secure Profile'
        sipProfileName = ''
        phoneTemplateName = 'Standard CIPC SCCP'
        hookswitch = ""
        product = "Cisco IP Communicator"
        protocol = "SCCP"
    elif phonetype == "Jabber":
        securityProfileName = 'Cisco Unified Client Services Framework - Standard SIP Non-Secure Profile'
        sipProfileName = 'Standard SIP Profile'
        phoneTemplateName = 'Standard Client Services Framework'
        hookswitch = ""
        product = "Cisco Unified Client Services Framework"
        protocol = "SIP"
    else:
        securityProfileName = "HBF 8811 SIP 1L 4S"
        sipProfileName = 'Cisco 8811 - Standard SIP Non-Secure Profile'
        phoneTemplateName = "HBF 8811 SIP 1L 4S"
    if phonetype == "CIPC" or phonetype == "Jabber":
        phone = {
            "name": mac_address,
            "description": phone_desc,
            'ownerUserName': username,
            "callingSearchSpaceName": calling_rights,
            "devicePoolName": device_pool,
            "lines": {"line": {"index": 1,
                            "label": line_label,
                            "display": line_desc,
                            "dirn": {"pattern": ext,
                                        "routePartitionName": ILPartition},
                            'e164Mask': mask,
                            'mwlPolicy': 'Use System Policy',
                            'maxNumCalls': 6,
                            'busyTrigger': 2,
                            'displayAscii': ' ',
                                        }
                                        },
            "commonPhoneConfigName": "Standard Common Phone Profile",
            'locationName': location,
            "useTrustedRelayPoint": "Default",
            "phoneTemplateName": phoneTemplateName,
            "primaryPhoneName": None,
            "softkeyTemplateName": "HBF Standard User IDivert",
            "securityProfileName": securityProfileName,
            "sipProfileName": sipProfileName,
            "builtInBridgeStatus": "Default",
            "packetCaptureMode" : '',
            "certificateOperation": "No Pending Operation",
            "deviceMobilityMode": "Default",
        }
    else:
        phone = {
        "name": mac_address,
        "description": phone_desc,
        'ownerUserName': username,
        "callingSearchSpaceName": calling_rights,
        "devicePoolName": device_pool,
        "lines": {"line": {"index": 1,
                           "label": line_label,
                           "display": line_desc,
                           "dirn": {"pattern": ext,
                                    "routePartitionName": ILPartition},
                           'e164Mask': mask,
                           'mwlPolicy': 'Use System Policy',
                           'maxNumCalls': 6,
                           'busyTrigger': 2,
                           'displayAscii': ' ',
                                    }
                                    },
        "commonPhoneConfigName": "Standard Common Phone Profile",
        'locationName': location,
        "useTrustedRelayPoint": "Default",
        "phoneTemplateName": phoneTemplateName,
        "primaryPhoneName": None,
        "softkeyTemplateName": "Standard User IDivert",
        "securityProfileName": securityProfileName,
        "sipProfileName": sipProfileName,
        "builtInBridgeStatus": "Default",
        "packetCaptureMode" : '',
        "certificateOperation": "No Pending Operation",
        "deviceMobilityMode": "Default",
        'vendorConfig': hookswitch
    }
    req = ''
    try:
        req = service.updatePhone(**phone)
        #print(req)
        #print("Successfully updated phone!")
    except Fault:
        show_history()
    return req
def add_extension_mobility(mac_address):
    phone = {
        "name": mac_address,
        'services': {
            'service': [
                {
                    'telecasterServiceName': {
                        '_value_1': 'Extension Mobility'
                    },
                    'name': 'Extension Mobility',
                    'url': 'http://10.16.8.140:8080/emapp/EMAppServlet?device=#DEVICENAME#',
                    'urlButtonIndex': 0,
                    'urlLabel': None,
                    'serviceNameAscii': 'Extension Mobility'
                }
            ]
        }
    }
    req = ''
    try:
        req = service.updatePhone(**phone)
        #print(req)
        #print("Successfully added extension mobility")
    except Fault:
        show_history()
    return req
def update_user(user):
    updateuser = {'userid' : user,
        'serviceProfile': 'CiscoJabberUsers',
        'enableMobility': 'true',
        'enableMobileVoiceAccess': 'true',
        'homeCluster': 'true',
        'imAndPresenceEnable': 'true',
        'associatedGroups': {
                'userGroup': [{'name': 'CTI for Jabber',
                "name" : "Standard CCM End Users"}]
        }
    }
    try:
        req = service.updateUser(**updateuser)
        #print(req)
    except Fault:
        show_history()
    return req
def get_user(user):
    try:
        req = service.getUser(**{"userid" : user})
        input_dict = helpers.serialize_object(req)
        output_dict = json.loads(json.dumps(input_dict))
        return output_dict
    except Fault:
        show_history()
    return req
#getline()
#getphone("mac")
#add_extension_mobility("FFFF2222FFFF")
#get_user({"userid" : "username"})
#update_user("username")



