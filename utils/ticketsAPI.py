import requests
import config
import urllib3
import json

import cairosvg
from bs4 import BeautifulSoup
from utils.filesAPI import read_schedule
from loguru import logger
from datetime import datetime as dt
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Ticket():
    def __init__(self, id, context, current_time_till_sla):
        self.context = context
        self.id = id
        self.url = f"https://tracker.ntechlab.com/tickets/{self.id}"
        self.sla_time = dt.fromtimestamp(current_time_till_sla / 1000)
        self.sla_state = current_time_till_sla > dt.timestamp(dt.now()) * 1000

def fromate_to_ticket(response):
    tickets = []
    for item in response:
        id = item.get('idReadable')
        summary = item.get('summary')
        SLA_time = item.get("fields", [{}])[0].get("value", None)
        if not(isinstance(SLA_time, int)): SLA_time = 0
        tickets.append(Ticket(id,summary,SLA_time))
    return tickets

def get_tickets(name, url = ""):
    if url == "" : url = f'https://tracker.ntechlab.com/api/issues?fields=id,idReadable,summary,fields(value),description&query=Assignee: {name} State: -Closed'
    logger.info(f"Making request to get tickets: {url}")
    url_headers = {
        'Accept': 'application/json',
        f'Authorization': f'Bearer {config.token}',
        'Content-Type': 'application/json'
    }
    request = requests.get(url=url, headers=url_headers, verify=False)
    return request.json()

def send_assigne_to_request(json, next_user):
    tickets = fromate_to_ticket(json)
    logger.debug(f"Count of tikcets ready to assignee: {len(tickets)}")
    for ticket in tickets:
        request_url = f"https://tracker.ntechlab.com/api/issues/{ticket.id}/fields/159-2506"
        url_headers = {
            'Accept': 'application/json',
            f'Authorization': f'Bearer {config.token}',
            'Content-Type': 'application/json'
        }
        data = {
        "id": "159-2506",
        "value": {
            "ringId": f"{config.user_ring_id[next_user]}"
            }
        }
        logger.debug(f"Trying send request to assignee on ticket: {ticket.id}")
        response = requests.post(request_url, json=data, headers=url_headers, verify=False)
        logger.debug(f"Get result: {response.status_code, response.text}")

def assigne_to_next(old_user_param : str = "",next_user_param : str = "") -> str:
    current_user, next_user = read_schedule()
    if next_user_param != "":
        next_user = config.tg_user[next_user_param]
    if old_user_param != "":
        current_user = config.tg_user[old_user_param]
    logger.info(f"Started assignee from {current_user} to {next_user}")
    tickets = get_tickets(current_user)
    send_assigne_to_request(tickets, next_user)
    return config.user_tg[next_user]

def send_change_request_ticket(ticket_id, data, field):
    url = f"https://tracker.ntechlab.com/api/issues/{ticket_id}/fields/{field}"
    url_headers = {
        'Accept': 'application/json',
        f'Authorization': f'Bearer {config.token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=data, headers=url_headers, verify=False)
    return response.status_code, response.text

def spam_ticket(ticket_id):
    current_user, _ = read_schedule()

    data = { "id": "159-2506", "value": {"ringId": f"{config.user_ring_id[current_user]}" } }
    status, text = send_change_request_ticket(ticket_id, data, "159-2506")
    logger.info(f"Send request to assignee on ticket: {ticket_id} | {status, text}")

    data = {"id": "158-10832","value": {"description": f"","id": "138-5442", "kind": "enum","label": "Спам","name": "Спам"}}
    status, text = send_change_request_ticket(ticket_id, data, "158-10832")
    logger.info(f"Send request to customer on ticket: {ticket_id} | {status, text}")
    
    data = {"id": "517-16752","value": f"Спам"}
    status, text = send_change_request_ticket(ticket_id, data, "517-16752")
    logger.info(f"Send request to solution on ticket: {ticket_id} | {status, text}")

    data = {"id": "158-10166","value": [{"description": None,"id": "166-796","kind": "enum","label": "Spam","name": "Spam"}]}
    status, text = send_change_request_ticket(ticket_id, data, "158-10166")
    logger.info(f"Send request to subsystem on ticket: {ticket_id} | {status, text}")

    data = {"id": "158-10165","event": {"id": "resolved"}}
    status, text = send_change_request_ticket(ticket_id, data, "158-10165")
    logger.info(f"Send request to state on ticket: {ticket_id} | {status, text}")

    data = {"id": "158-10165","event": {"id": "closed"}}
    status, text = send_change_request_ticket(ticket_id, data, "158-10165")
    logger.info(f"Send request to state on ticket: {ticket_id} | {status, text}")

    logger.info(f"Spam requests ended for {ticket_id}")

#TODO: укоротить реквест
def get_ticket_content(ticket_id):
    logger.info(f"Making request to get info about {ticket_id}")
    url = f"https://tracker.ntechlab.com/api/issues/{ticket_id}/activitiesPage?categories=IssueCreatedCategory,CommentsCategory&reverse=true&fields=activities(category(id()),added(id,ringId,login,name,email,isEmailVerified,guest,fullName,avatarUrl,online,banned,banBadge,canReadProfile,isLocked,userType(id),localizedName,numberInProject,project(name,shortName),author(ringId,avatarUrl,canReadProfile,isLocked,login,name,id,email,isEmailVerified,guest,fullName,online,banned,banBadge,userType(id)),created,updated,mimeType,url,size,visibility(%40visibility),imageDimensions(width,height),thumbnailURL,recognizedText,searchResults(%40searchResults),comment(%40comment),embeddedIntoDocument(id),embeddedIntoComments(id),resolved,idReadable,summary,mentionedUsers(%40author),mentionedIssues(id,reporter(%40author),resolved,updated,created,unauthenticatedReporter,fields(value(id,minutes,presentation,name,description,localizedName,isResolved,color(%40color),buildIntegration,buildLink,text,issueRelatedGroup(%40issueRelatedGroup),ringId,login,email,isEmailVerified,guest,fullName,avatarUrl,online,banned,banBadge,canReadProfile,isLocked,userType(id),allUsersGroup,icon,teamForProject(name,shortName)),id,$type,hasStateMachine,isUpdatable,projectCustomField($type,id,field(id,name,ordinal,aliases,localizedName,fieldType(id,presentation,isBundleType,valueType,isMultiValue)),bundle(id,$type),canBeEmpty,emptyFieldText,hasRunningJob,ordinal,isSpentTime,isPublic),searchResults(id,textSearchResult(highlightRanges(%40highlightRanges),textRange(%40highlightRanges))),pausedTime),project(%40project),visibility(%40visibility),tags(%40tags),votes,voters(hasVote),watchers(hasStar),usersTyping(timestamp,user(%40value1)),canUndoComment,idReadable,summary),mentionedArticles(id,idReadable,reporter(%40value1),summary,project(%40project),parentArticle(idReadable),ordinal,visibility(%40visibility),hasUnpublishedChanges,hasChildren,tags(%40tags)),creator(%40value1),text,type(%40value),duration(minutes,presentation),textPreview,date,usesMarkdown,attributes(id,name,value(%40value)),files,commands(errorText,hasError,start,end),noHubUserReason($type,id),noUserReason($type,id),pullRequest($type,author(%40value1),date,fetched,processor(id,$type),files,id,branch,idExternal,noHubUserReason($type,id),noUserReason($type,id),title,text,url),urls,processors(id,$type),state($type,id()),version,deleted,pinned,attachments(id,name,author(%40author1),created,updated,mimeType,url,size,visibility(%40visibility),imageDimensions(width,height),thumbnailURL,recognizedText,searchResults(%40searchResults),comment(%40comment),embeddedIntoDocument(id),embeddedIntoComments(id)),reactions(id,reaction,author(%40value1)),reactionOrder,hasEmail,canUpdateVisibility,suspiciousEmail,issue(id,project(id)),markdownEmbeddings(key,settings,widget(id)),reaction,profileUrl,membership(id,name,avatarUrl,__entityId),unverifiedEmail,isReporter,isAgent,presentation),removed(id,ringId,login,name,email,isEmailVerified,guest,fullName,avatarUrl,online,banned,banBadge,canReadProfile,isLocked,userType(id),localizedName,numberInProject,project(name,shortName),author(%40author1),created,updated,mimeType,url,size,visibility(%40visibility),imageDimensions(width,height),thumbnailURL,recognizedText,searchResults(%40searchResults),comment(%40comment),embeddedIntoDocument(id),embeddedIntoComments(id),resolved,idReadable,summary,presentation),issue(description,customFields(name,projectCustomField(emptyFieldText,field(id,localizedName,name,fieldType(%40fieldType))),value(%40value1))),id,author(%40author),authorGroup(ringId),timestamp,field(id,presentation,customField(fieldType(%40fieldType))),target(id,$type),targetMember,type,pseudo,emptyFieldText),hasBefore,hasAfter,beforeCursor,afterCursor,cursor%3B%40comment%3Aid,visibility(%40visibility)%3B%40visibility%3A$type,implicitPermittedUsers(%40value1),permittedGroups(%40issueRelatedGroup),permittedUsers(%40value1)%3B%40project%3Aid,ringId,name,shortName,iconUrl,template,pinned,archived,isDemo,organization(),hasArticles,team(%40issueRelatedGroup),fieldsSorted,restricted,plugins(timeTrackingSettings(id,enabled),helpDeskSettings(id,enabled,defaultForm(uuid,title)),vcsIntegrationSettings(hasVcsIntegrations),grazie(disabled))%3B%40author%3AissueRelatedGroup(%40issueRelatedGroup),id,ringId,login,name,email,isEmailVerified,guest,fullName,avatarUrl,online,banned,banBadge,canReadProfile,isLocked,userType(id)%3B%40value%3Aid,name,autoAttach,description,hasRunningJobs,color(%40color),attributes(id,timeTrackingSettings(id,project(id)))%3B%40value1%3Aid,ringId,login,name,email,isEmailVerified,guest,fullName,avatarUrl,online,banned,banBadge,canReadProfile,isLocked,userType(id)%3B%40issueRelatedGroup%3Aid,name,ringId,allUsersGroup,icon,teamForProject(name,shortName)%3B%40searchResults%3AtextSearchResult(highlightRanges(%40highlightRanges))%3B%40author1%3AringId,avatarUrl,canReadProfile,isLocked,login,name%3B%40tags%3Aid,name,color(%40color)%3B%40color%3Aid,background,foreground%3B%40fieldType%3AvalueType,isMultiValue%3B%40highlightRanges%3AstartOffset,endOffset"
    url_headers = {
        'Accept': 'application/json',
        f'Authorization': f'Bearer {config.token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url=url, headers=url_headers, verify=False)
    logger.info(f"Get response {response.status_code}")
    return response

#TODO: split полумера. Можно подумать о более качественном форматировании
def get_contents_of_messages(ticket_id, internal_visibility = False):
    response = get_ticket_content(ticket_id)
    if response.status_code != 200: 
        return False
    json_data = response.json()
    logger.info(f"Get messages from ticket {ticket_id} : {len(json_data['activities'])}")
    resulted_json = {"ticket_id" : ticket_id}
    comments = {}
    avatars = {}
    body = BeautifulSoup(json_data['activities'][len(json_data['activities'])-1]['issue']['description'], 'html.parser').get_text(separator='\n', strip=True)
    status = json_data['activities'][len(json_data['activities'])-1]['issue']['customFields'][3]['value']['name']
    resulted_json.update({'body': body})
    resulted_json.update({'status' : status})
    for i in range(len(json_data['activities'])-1):
        author = json_data['activities'][i]['author']['email']
        author_avatar_url = json_data['activities'][i]['author']['avatarUrl']
        soup = BeautifulSoup(json_data['activities'][i]['added'][0]['text'], 'html.parser')
        text = soup.get_text(separator='\n', strip=True).split("##- Please enter your reply above this line -##")[0]
        visibility = json_data['activities'][i]['added'][0]['visibility']['$type']
        if author != None:
            if visibility != "LimitedVisibility" or internal_visibility:
                comments.update({i : {author : text}})
            avatars.update({author: __get_avatar(author, author_avatar_url)})
    resulted_json.update({"comments" : comments})
    resulted_json.update({"avatars" : avatars})
    file_path = f"comments_files/{ticket_id}_comments.json"
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(resulted_json,file,ensure_ascii=False,indent=4)
    logger.info(f'Json file saved as comments_files/{ticket_id}_comments.json')
    return file_path

def __get_avatar(author_name,avaratar_url):
    path_to_avatar = f"users_avatars/{author_name}_avatar.png"
    url = f"https://tracker.ntechlab.com{avaratar_url}"
    url_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        f'Authorization': f'Bearer {config.token}',
        'Content-Type': 'multipart/form-data'
    }
    request = requests.get(url,headers=url_headers, verify=False)
    if request.status_code != 200:
        logger.error(f"Failed to download photo! Status code: {request.status_code}")
        return
    if request.headers.get("content-type") == "image/svg+xml":
        file = cairosvg.svg2png(bytestring=request.content, write_to=path_to_avatar)
    else:
        with open(path_to_avatar, 'wb') as file:
            file.write(request.content)
    return path_to_avatar
    