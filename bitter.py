#!/usr/bin/python

# written by andrewt@cse.unsw.edu.au September 2015
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/bitter/

import cgi, cgitb, glob, os, datetime, time, re

class user(object):
    """Bitter user"""
    def __init__(self, user_dir):
        # super(user, self).__init__()
        # self.arg = arg
        self.details = {}
        self.pic = os.path.join(user_dir,"profile.jpg")
        with open(os.path.join(user_dir,"details.txt")) as f:
            # details = f.read()
            for line in f:
                field, _, value = line.rstrip().partition(": ")
                # if field == "listens":
                    # list?
                self.details[field] = value
        with open(os.path.join(user_dir,"bleats.txt")) as f:
            # self.bleats = f.readlines() # has newlines
            self.bleats = f.read().split()
            self.bleats.sort(reverse=True)

    def details_basic(self):
        details_formatted = ""
        # for field in vars(self):
        #     details += field + ": " + self.details[field]
        for field,_ in sorted(self.details.items()): # sorted
        # for field in self.details: # unsorted
            # details_formatted += field + ": " + self.details[field]
            if field not in ["email","password","username","full_name"]:
                details_formatted += "<p>%s: %s</p>\n" % (field,self.details[field])
        # return details # sorted(vars(self))
        return details_formatted

class bleat(object):
    'A bleat'
    def __init__(self,bleat_id):
        with open(os.path.join(bleats_dir,bleat_id)) as f:
            for line in f:
                field, _, value = line.rstrip().partition(": ")
                self.details[field] = value

def main():
    print page_header()
    cgitb.enable()
    dataset_size = "small" 
    users_dir = "dataset-%s/users"% dataset_size
    bleats_dir = "dataset-%s/bleats"% dataset_size
    bleat.bleats_dir = bleats_dir
    parameters = cgi.FieldStorage()
    print main_form()
    if parameters.getvalue('new-bleat') != None:
        # new bleat
        new_bleat(parameters,users_dir,bleats_dir)
    elif parameters.getvalue('listen') != None:
        add_listen(parameters,users_dir,bleats_dir)
    if parameters.getvalue('user') != None:
        print user_page(parameters, users_dir, bleats_dir)
    elif parameters.getvalue('search_term') != None:
        print search_page(parameters,users_dir,bleats_dir)
    else:
        print user_page(parameters, users_dir, bleats_dir)
    print page_trailer(parameters)

def new_bleat(parameters, users_dir, bleats_dir):
    text = parameters.getvalue('new-bleat')
    user = parameters.getvalue('new-bleat-user')
    reply = parameters.getvalue('new-bleat-reply',None)
    # text = cgi.escape(parameters['new-bleat'].value)
    # user = cgi.escape(parameters['new-bleat-user'].value)
    # reply = cgi.escape(parameters['new-bleat-reply'].value)
    curr_time = int(time.time())
    # print text,"by",user,"at",curr_time,"to",reply
    bleat_id = str(max([int(i) for i in os.listdir(bleats_dir)]) + 1)
    bleat_type = "Bleat"
    with open(os.path.join(users_dir,user,"bleats.txt"),"a") as f:
        f.write(bleat_id+"\n")
    with open(os.path.join(bleats_dir,bleat_id),"w") as f:
        f.write("time: %s\n" % curr_time)
        f.write("bleat: %s\n" % text)
        f.write("username: %s\n" % user)
        if reply != None:
            f.write("in_reply_to: %s\n" % reply)
            bleat_type = "Reply"
    print """<div class="alert alert-success alert-dismissible toast fade in" id="bleat-alert" role="alert">
<button type="button" class="close" data-dismiss="alert"><span>&times;</span></button>
%s successful!
</div>
    """ % bleat_type
    return

def main_form():
    return """<form method="POST" action="" id="main">
</form>"""

def add_listen(parameters,users_dir,bleats_dir):
    user = parameters.getvalue('listen')
    with open(os.path.join(users_dir,"test_user",'details.txt'),'r+') as f:
        lines = f.readlines()
        for index, line in enumerate(lines):
            field, _, value = line.rstrip().partition(": ")
            if field == "listens":
                lines[index] = field + ": " + value.rstrip() + " " + user + "\n" 
                # could use split and join?
                break
        # if field != "listens": # if no listens
        #    lines.append("listens: " + user + "\n")
        f.writelines(lines)

def bleat_panels(bleats,bleats_dir): # list of bleats
    bleat_details = ""
    for bleat_id in bleats:
            bleat_details += bleat_panel(bleat_id.rstrip(),bleats_dir)
    return bleat_details

def bleat_panel(bleat_id,bleats_dir):
    curr_bleat = {}
    bleat_details = ""
    with open(os.path.join(bleats_dir,bleat_id)) as f:
        for line in f:
            field, _, value = line.rstrip().partition(": ")
            curr_bleat[field] = value
    # bleat_details += '<li class="list-group-item">\n'
    # bleat_details += '<button class="panel panel-default" type="button" data-toggle="collapse" data-target="#%s" aria-expanded="false" aria-controls="%s">' % (bleat_id,bleat_id)
    bleat_details += '<div id="%s">' % bleat_id
    bleat_details += '<div class="panel panel-default">\n'
    bleat_details += '<div class="list-group">\n'
    bleat_details += '<div class="list-group-item">\n'
    # bleat_details += '<h4 class="list-group-item-heading">%s</h4>\n' % curr_bleat['username'] # user
    bleat_details += '<a style="color: inherit;" class="list-group-item-heading" href="?user=%s"><h4 class="list-group-item-heading">%s</h4></a>\n' % (curr_bleat['username'],curr_bleat['username']) # user
    bleat_details += '<p class="lead">%s</p>\n' % curr_bleat['bleat'] # bleat
    bleat_details += '<ul class="list-inline">\n' # metadata
    bleat_details += datetime.datetime.fromtimestamp(int(curr_bleat['time'])).strftime('<li><small>%I:%M:%S %p</small></li>\n<li><small>%A, %d %B %Y</small></li>\n')
    if 'latitude' in curr_bleat and 'longitude' in curr_bleat:
        bleat_details += '<li><small>Location: %s, %s</small></li>\n' % (curr_bleat['latitude'],curr_bleat['longitude'])
    bleat_details += "</ul>\n"
    precursors = bleat_conversation(bleat_id,bleats_dir)
    replies = bleat_replies(bleat_id,bleats_dir)
    bleat_details += '<div class="btn-group btn-group-sm">\n'
    bleat_details +='<a class="btn btn-link" data-toggle="collapse" data-parent="#%s" href="#%s-reply"><small>Reply</small></a>\n' % (bleat_id,bleat_id)
    if precursors:
        bleat_details +='<a class="btn btn-link" data-toggle="collapse" data-parent="#%s" href="#%s-conversations"><small>View conversation</small></a>\n' % (bleat_id,bleat_id)
    if replies:
        bleat_details +='<a class="btn btn-link" data-toggle="collapse" data-parent="#%s" href="#%s-replies"><small>View replies</small></a>\n' % (bleat_id,bleat_id)
    bleat_details += '</div>\n'
    # bleat_details += "</li>\n"
    bleat_details += "</div>\n" # list-group-item
    bleat_details += "</div>\n" # list-group
    # bleat_details += "</button>\n"
    # bleat_details += "</div>"
    bleat_details += """<div class="collapse panel-collapse" id="%s-reply">
    <ul class="list-group">
""" % (bleat_id)
    bleat_details += """<li class="list-group-item">
    <form id="bleat-reply" method="POST">
    <input type="hidden" name="new-bleat-user" value="test_user">
    <input type="hidden" name="new-bleat-reply" value="%s">
    <div class="form-group">
    <textarea name="new-bleat" placeholder="Your reply" class="form-control" rows="3" maxlength="142"></textarea>
    <span id="helpBlock" class="help-block pull-right">0/142</span>
    </div>
    <button type="submit" class="btn btn-default" data-toggle="tooltip" data-placement="right" title="Log in to reply" disabled="disabled">Submit</button>
</form>
</li>
</ul>
""" % bleat_id
    bleat_details += "</ul>\n</div>\n"
    # previous bleats in conversation:
    if precursors:
        bleat_details += """<div class="collapse panel-collapse" id="%s-conversations">
    <ul class="list-group">
""" % (bleat_id)
        for precursor in precursors:
            bleat_details += bleat_child(precursor,bleats_dir)
        bleat_details += "    </ul>\n</div>\n"
    if replies:
        bleat_details += """<div class="collapse panel-collapse" id="%s-replies">
    <ul class="list-group">
""" % (bleat_id)
        for reply in replies:
            bleat_details += bleat_child(reply,bleats_dir)
        bleat_details += "    </ul>\n</div>\n"
    bleat_details += "</div>\n" # panel
    bleat_details += "</div>\n"
    return bleat_details

# take a bleat and return a list of its replies
def bleat_replies(bleat_id,bleats_dir):
    replies = []
    for curr_bleat in os.listdir(bleats_dir): # sort by time first?
        with open(os.path.join(bleats_dir,curr_bleat)) as f:
            for line in f:
                field, _, value = line.rstrip().partition(": ")
                if field == "in_reply_to":
                    if value == bleat_id:
                        replies.append(curr_bleat)
                    else:
                        break
    return replies
    replies_details = ""
    for curr_bleat in replies:
         replies_details += bleat_child(curr_bleat,bleats_dir)
    return replies_details

# take a bleat and return a list of its precursors
def bleat_conversation(bleat_id,bleats_dir): # pass a dict/object instead of the id?
    curr_bleat = bleat_id
    precursors = []
    precursor = None
    bleat_precursor = ""
    with open(os.path.join(bleats_dir,bleat_id)) as f:
        for line in f:
            field, _, value = line.rstrip().partition(": ")
            if field == "in_reply_to":
                precursors.append(value)
                precursor = value
                break
    while precursor != None:
        with open(os.path.join(bleats_dir,precursor)) as f:
            precursor = None
            for line in f:
                field, _, value = line.rstrip().partition(": ")
                if field == "in_reply_to":
                    precursors.append(value)
                    precursor = value
                    break
    return precursors
    pre_details = ""
    for curr_bleat in precursors:
        pre_details += bleat_child(curr_bleat,bleats_dir)
    return pre_details

def bleat_child(bleat_id,bleats_dir):
    curr_bleat = {}
    with open(os.path.join(bleats_dir,bleat_id)) as f:
        for line in f:
            field, _, value = line.rstrip().partition(": ")
            curr_bleat[field] = value
    if "in_reply_to" not in curr_bleat:
        curr_bleat["in_reply_to"] = "N/A"
    bleat_details = ''
    bleat_details += '<li class="list-group-item">\n'
    bleat_details += '<a style="color: inherit;" class="list-group-item-heading" href="?user=%s"><h4 class="list-group-item-heading">%s</h4></a>\n' % (curr_bleat['username'],curr_bleat['username']) # user
    bleat_details += '<p class="lead">%s</p><!--this:%s in-reply-to:%s-->\n' % (curr_bleat['bleat'],bleat_id,curr_bleat['in_reply_to'])  # bleat
    bleat_details += '<ul class="list-inline">\n' # metadata
    bleat_details += datetime.datetime.fromtimestamp(int(curr_bleat['time'])).strftime('<li><small>%I:%M:%S %p</small></li>\n<li><small>%A, %d %B %Y</small></li>\n')
    if 'latitude' in curr_bleat and 'longitude' in curr_bleat:
        bleat_details += '<li><small>Location: %s, %s</small></li>\n' % (curr_bleat['latitude'],curr_bleat['longitude'])
    bleat_details += "</ul>\n"
    bleat_details += '</li>\n'
    return bleat_details
    return """
    <button type="submit" form="main" name="user" value="%s" class="list-group-item">
    <h4 class="list-group-item-heading">%s</h4>
    <p>%s</p> <!--this:%s in-reply-to:%s-->
    </button>
""" % (curr_bleat["username"], curr_bleat["username"],curr_bleat["bleat"],bleat_id, curr_bleat["in_reply_to"])

#
# Show unformatted details for user "n".
# Increment parameter n and store it as a hidden variable
#
def user_page(parameters, users_dir, bleats_dir):
    n = int(parameters.getvalue('n', 0))
    user_to_show = parameters.getvalue('user','')
    if user_to_show != '':
        user_to_show = os.path.join(users_dir,user_to_show)
    else:
        users = sorted(glob.glob(os.path.join(users_dir, "*")))
        user_to_show  = users[n % len(users)]
    curr_user = user(user_to_show)
    if "full_name" in curr_user.details:
        details = "<h1>%s<br><small>%s</small></h1>\n" % (curr_user.details["full_name"],curr_user.details["username"])
        # details += '<h1><small>%s</small></h1>\n' % curr_user.details["username"]
    else:
        details = "<h1>%s</h1>\n" % curr_user.details["username"]
    # details += curr_user.details_basic()
    details += curr_user.details.get('info','')
    # details += '<ul class="list-group">\n'
    # details += '<li class="list-group-item">\n'
    home_details = '<h3 class="list-group-item-heading">Home Details</h3>\n<dl>\n'
    for field,_ in sorted(curr_user.details.items()):
        if field.startswith("home_"):
            home_details += '<dt>%s</dt><dd>%s</dd>\n' % (field.replace("home_","",1).title(),curr_user.details[field])
    home_details += '</dl>\n'
    # details += '</li>\n'
    # details += '</ul>\n'
    listen_details = '<h3 class="list-group-item-heading">Listens</h3>\n'
    listen_details += '<div class="list-group">\n'
    listens = curr_user.details["listens"]
    for listen in listens.split(' '):
        curr_listen = user(os.path.join(users_dir,listen))
        listen_details += '<a href="?user=%s" class="list-group-item">\n'% listen
        listen_details += '<div class="media">\n'
        listen_details += '    <div class="media-left">\n'
        listen_details += '        <img class="media-object" src="%s" height="64" width="64">\n' % curr_listen.pic
        listen_details += '    </div>\n'
        listen_details += '    <div class="media-body">\n'
        listen_details += '        <h4 class="media-heading">%s<br><small>%s</small></h4>\n' % (curr_listen.details["full_name"],listen)
        listen_details += '    </div>\n'
        listen_details += '</div>\n'
        listen_details += '</a>\n'
    listen_details += '</div>\n'
#     bleat_details = ""
#     curr_bleat = {}
#     for bleat_id in curr_user.bleats:
#         bleat_id = bleat_id.rstrip()
#         with open(os.path.join(bleats_dir,bleat_id.rstrip())) as f:
#             for line in f:
#                 field, _, value = line.rstrip().partition(": ")
#                 curr_bleat[field] = value
#         # bleat_details += '<li class="list-group-item">\n'
#         # bleat_details += '<button class="panel panel-default" type="button" data-toggle="collapse" data-target="#%s" aria-expanded="false" aria-controls="%s">' % (bleat_id,bleat_id)
#         bleat_details += '<div class="panel panel-default">'
#         bleat_details += '<div class="list-group">'
#         bleat_details += '<div class="list-group-item">'
#         bleat_details += '<h4 class="list-group-item-heading">%s</h4>\n' % curr_bleat['username']
#         bleat_details += '<p class="lead">%s</p>' % curr_bleat['bleat']
#         bleat_details += '<ul class="list-inline">'
#         bleat_details += datetime.datetime.fromtimestamp(int(curr_bleat['time'])).strftime('<li><small>%I:%M:%S %p</small></li>\n<li><small>%A, %d %B %Y</small></li>\n')
#         bleat_details += '<li><small>Location: %s, %s</small></li>' % (curr_bleat['latitude'],curr_bleat['longitude'])
#         bleat_details += "</ul>\n"
#         bleat_details +='<p><a data-toggle="collapse" href="#%s"><small>View conversation</small></a></p>' % bleat_id
#         for field in sorted(curr_bleat): # sorted
#             if field not in ["time","username","bleat","latitude","longitude","in_reply_to"]:
#                 bleat_details += "<p>%s: %s</p>\n" % (field,curr_bleat[field])
#             # elif field == "time":
#                 # bleat_details += datetime.datetime.fromtimestamp(int(curr_bleat[field])).strftime('%I:%M:%S%p, %d %B %Y (%Z)') #'%Y-%m-%d %H:%M:%S')
#                 # bleat_details += datetime.datetime.fromtimestamp(int(curr_bleat[field])).strftime('<p>%I:%M:%S %p</p>\n<p>%A, %d %B %Y</p>\n')
#         # bleat_details += "</li>\n"
#         bleat_details += "</div></div>"
#         # bleat_details += "</button>\n"
#         # bleat_details += "</div>"
#         bleat_details += """<div class="collapse panel-collapse" id="%s">
#     <div class="list-group">
#         <button type="submit" form="main" name="user" value="VitaliKlitschko" class="list-group-item">
#         <h4 class="list-group-item-heading">Bleat</h4>
#         <p>Bleat here</p>
#         </button>
#         <button type="submit" form="main" name="user" value="VitaliKlitschko" class="list-group-item">
#         <h4 class="list-group-item-heading">Bleat</h4>
#         <p>Bleat here</p>
#         </button>
#     </div>
# </div></div>""" % bleat_id
        # curr_bleat = bleat(bleat_id)
        # for field,_ in sorted(vars(curr_bleat)): # sorted
        #     bleats += "<p>%s %s</p>" % (field, curr_bleat.)
    # details_filename = os.path.join(user_to_show, "details.txt")
    # with open(details_filename) as f:
    #     details = f.read()
    return """
<div class="container">
    <div class="row">
        <div class="col-sm-5 col-md-3">
            <div class="panel panel-primary">
                <div class="panel-body">
                    <img src="%s" class="img-responsive" alt="Profile Picture">
                    %s
                </div>
                <ul class="list-group">
                    <li class="list-group-item">
                        %s
                    </li>
                    <li class="list-group-item">
                        %s
                    </li>    
                </ul>
            </div>
            <p>
            <form method="POST"><!-- id="main"> -->
                <!-- <input type="hidden" name="n" value="%s">
                <input type="submit" value="Next user" class="btn btn-default">-->
                <button type="submit" name="listen" value="%s" class="btn btn-default toaster" href="#listen-alert">Listen</button> <!-- onclick="$('.alert').show()"> -->
            </form>
        </div>
        <div class="col-md-6 col-sm-7">
            <!-- <div class="panel panel-primary">
                <div class="panel-body">
                    <h1 class="list-group-item-heading">Bleats</h1>
                </div>
            </div> -->
                <!-- <ul class="list-group"> -->
                    <!-- <li class="list-group-item panel-primary">
                        <h1 class="list-group-item-heading">Bleats</h1>
                    </li> -->
                    %s
                <!-- </ul> -->
            <!-- </div> -->
            <nav>
              <ul class="pagination">
                <li class="disabled">
                  <a href="#" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                  </a>
                </li>
                <li class="active"><a href="#">1</a></li>
                <li><a href="#">2</a></li>
                <li><a href="#">3</a></li>
                <li><a href="#">4</a></li>
                <li><a href="#">5</a></li>
                <li>
                  <a href="#" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                  </a>
                </li>
              </ul>
            </nav>
        </div>
        <div class="col-md-3 col-sm-5">
            <div class="panel panel-primary">
                <div class="panel-body">
                    <p>Bleh</p>
                </div>
            </div>
        </div>
    </div>
</div>
""" % (curr_user.pic, details, listen_details,home_details, n+1, curr_user.details['username'],bleat_panels(curr_user.bleats,bleats_dir)) 

def search_page(parameters, users_dir, bleats_dir):
    search_term = parameters.getvalue('search_term','')
    matches = []
    # matches = ""
    for curr_user in os.listdir(users_dir):
        if search_term.lower() in curr_user.lower():
            matches.append(curr_user)
            # matches += '<li class="list-group-item">%s</li>\n' % curr_user
        else:
            with open(os.path.join(users_dir,curr_user,"details.txt")) as f:
                for line in f:
                    field, _, value = line.rstrip().partition(": ")
                    if field == "full_name":
                        if search_term.lower() in value.lower():
                            matches.append(curr_user)
                            # matches += '<li class="list-group-item">%s</li>\n' % curr_user
                        else:
                            break
    user_results = ""
    for match in matches:
        curr_user = user(os.path.join(users_dir,match))
        user_results += """<button type="submit" form="main" name="user" value=%s class="list-group-item">
<div class="media">
    <div class="media-left">
        <img class="media-object" src="%s" height="100" width="100">
    </div>
    <div class="media-body">
        <h3 class="media-heading">%s<br><small>%s</small></h3>
    </div>
</div>
</button>
""" % (match,curr_user.pic,curr_user.details["full_name"],match)
    matches = []
    for curr_bleat in os.listdir(bleats_dir):
        with open(os.path.join(bleats_dir,curr_bleat)) as f:
            for line in f:
                field, _, value = line.rstrip().partition(": ")
                if field == "bleat":
                    if search_term.lower() in value.lower():
                        matches.append(curr_bleat)
                    else:
                        break
    # bleat_results = ""
    # for match in matches:
        # # put bleat parsing here or use function
        # bleat_results += """<button type="submit" form="main" name="user" value=%s class="list-group-item">
# <p>%s</p>
# </button>            
# """ % (match,match)
    return """
<div class="container">
    <div class="row">
        <!-- <div class="col-sm-5 col-md-3">
            <div class="panel panel-primary">
                <div class="panel-body">
                    <img src="" class="img-responsive" alt="Profile Picture">
                    
                </div>
            </div>
            <p>
            <form method="POST" action="">
                <input type="hidden" name="n" value="">
                <input type="submit" value="Next user" class="btn btn-default">
            </form>
        </div> -->
        <div class="col-md-12 col-sm-12">
            <div class="panel panel-primary">
                <div class="panel-body">
                    <h2 class="list-group-item-heading">Search Results: <small>%s</small></h2>
                </div>
            </div>
            <ul class="nav nav-pills">
                <li role="presentation" class="active"><a href="#users" data-toggle="pill">Users</a></li>
                <li role="presentation"><a href="#bleats" data-toggle="pill">Bleats</a></li>
                <!-- <li role="presentation"><a href="#">All</a></li> -->
            </ul>
            <div class="tab-content">
                <div role="tabpanel" class="tab-pane fade in active" id="users">
                    %s
                </div>
                <div role="tabpanel" class="tab-pane fade" id="bleats">
                    <!-- <li class="list-group-item"><h3>No results</h3></li> -->
                    %s
                </div>
            </div>
            <nav>
              <ul class="pagination">
                <li class="disabled">
                  <a href="#" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                  </a>
                </li>
                <li class="active"><a href="#">1</a></li>
                <li><a href="#">2</a></li>
                <li><a href="#">3</a></li>
                <li><a href="#">4</a></li>
                <li><a href="#">5</a></li>
                <li>
                  <a href="#" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                  </a>
                </li>
              </ul>
            </nav>
        </div>
        <!-- <div class="col-md-3 col-sm-5">
            <div class="panel panel-primary">
                <div class="panel-body">
                    <p>Bleh</p>
                </div>
            </div>
        </div> -->
    </div>
</div>
""" % (search_term,user_results,bleat_panels(matches,bleats_dir))

#
# HTML placed at the top of every page
#
def page_header():
    return """Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
        <title>Bitter</title>
        <!-- MDL -->
        <link href="./material.min.css" rel="stylesheet">
        <script src="./material.min.js"></script>
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <!-- Bootstrap -->
        <link href="css/bootstrap.min.css" rel="stylesheet">
        <!-- My CSS -->
        <link href="css/custom.css" rel="stylesheet">
        <!-- <link href="bitter.css" rel="stylesheet"> -->
        <style>
        body { padding-top: 80px; }
        </style>
    </head>
    <body>
        <button class="fab-fixed mdl-button mdl-js-button mdl-button--fab mdl-js-ripple-effect mdl-button--colored" data-toggle="modal" data-target="#new-bleat-dialog">
            <i class="material-icons">create</i>
        </button>
        <div class="modal fade" id="new-bleat-dialog" tabindex="-1" role="dialog">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal"><span>&times;</span></button>
                        <h4 class="modal-title">New Bleat</h4>
                    </div>
                    <div class="modal-body">
                        <!-- <p>Test</p> -->
                        <form id="bleat-reply" method="POST">
                        <input type="hidden" name="new-bleat-user" value="test_user">
                        <div class="form-group">
                        <textarea name="new-bleat" placeholder="Your reply" class="form-control" rows="3" maxlength="142"></textarea>
                        <span id="helpBlock" class="help-block pull-right">0/142</span>
                        </div>
                        <button type="submit" class="btn btn-default" data-toggle="tooltip" data-placement="right" title="Log in to reply" disabled="disabled">Submit</button>
                        </form>
                    </div>
                </div>
            </div>
        </div><!-- New Bleat Modal -->
        <!-- <div class="alert alert-info alert-dismissible toast fade in" id="listen-alert" role="alert">
            <button type="button" class="close" data-dismiss="alert"><span>&times;</span></button>
            You are now following <strong>this user</strong>.
        </div> -->
        <!-- <div class="bitter_heading">Bitter</div> -->
        <!-- <h1>Bitter</h1> -->
        <nav class="navbar navbar-default navbar-fixed-top">
            <div class="container-fluid">
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                        <span class="sr-only">Toggle nagivation</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>  
                        <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" href="#">Bitter</a>
                    <!-- <input type="reset" class="navbar-brand" value="Bitter"> -->
                </div>

                <div id="navbar" class="collapse navbar-collapse">
                    <!-- <ul class="nav navbar-nav">
                        <li class="active"><input type="reset" value="Home" class="btn btn-link navbar-btn"><span class="sr-only">(current)</span></a></li>
                        <li><a href="#">New Bleat</a></li>
                        <li class="active"><input type="submit" value="New Bleat" class="btn btn-link navbar-btn"><span class="sr-only">(current)</span></a></li>
                    </ul> -->
                    <form class="navbar-form navbar-left" id="search" role="search">
                    <input type="submit" value="Home" class="btn btn-link" name=".defaults">
                    <input type="submit" value="Bleats" class="btn btn-link">
                    <div class="input-group">
                        <!-- <div class="input-group-btn">
                            <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Users<span class="caret"></span></button>
                            <ul class="dropdown-menu">
                                <li><a href="#">Users</a></li>
                                <li><a href="#">Username</a></li>
                                <li><a href="#">Name</a></li>
                                <li role="separator" class="divider"></li>
                                <li><a href="#">Bleats</a></li>
                            </ul>
                        </div> --><!-- /btn-group -->
                        <input type="text" name="search_term" class="form-control" placeholder="Search">
                        <span class="input-group-btn">
                            <button type="submit" name="search" class="btn btn-link">
                                <span class="glyphicon glyphicon-search" aria-hidden="true"></span>
                            </button>
                        </span>
                    </div>
                    </form>
                    <ul class="nav navbar-nav navbar-right">
                        <li><a href="#">Log Out</a></li>
                    </ul>
                    <p class="navbar-text navbar-right">Signed in as <a href="#" class="navbar-link">John Doe</a></p>
                </div>
            </div>
        </nav>
"""


#
# HTML placed at the bottom of every page
# It includes all supplied parameter values as a HTML comment
# if global variable debug is set
#
def page_trailer(parameters):
    html = ""
    if debug:
        html += "".join("<!-- %s=%s -->\n" % (p, parameters.getvalue(p)) for p in parameters)
    html += """
    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="js/bootstrap.min.js"></script>
    <script>
    /*$('.collapse-link').mouseup(function(){
        id = this.getAttribute('data-id');
        ref = this.getAttribute('href');
        active_change($(this),id,ref);
    }); */
    
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })

    $('form').on('input', function () {
        var area = $("textarea",this);
        var count = $("textarea",this).val().length;
        if (count > 0) {
            $("button",this).attr("disabled",false);
        } else {
            $("button",this).attr("disabled","disabled");
        }
        $("span.help-block",this).text(count+'/142');
        // alert(">>"+count);
    })

    // if panel open, show associated button as active
    $('.collapse').on('show.bs.collapse', function () {
        var id = this.getAttribute('id');
        $('.btn[href="#'+id+'"').addClass('active');
    })
    
    // if panel closed, show associated button as inactive
    $('.collapse').on('hide.bs.collapse', function () {
        var id = this.getAttribute('id');
        $('.btn[href="#'+id+'"').removeClass('active');
    })

    // toggle hiding of toasts
    $('.toaster').click(function() {
        var alert = this.getAttribute('href');
        if ($(alert).hasClass('in')){
            $(alert).removeClass('in');
        } else {
            $(alert).addClass('in');
        }
    })

    /* function active_change(item,id,ref){
        collapser = item.getElementById("'"+ref.substring(1)+"'"); 
        if ($(item).hasClass('active')){
            $(item).removeClass('active');
        } else if $(collapser).hasClass('collapse'){   
            $(".collapse-link[data-id='"+id+"']").removeClass('active');
            $(item).addClass('active');
        }
    }*/
    </script>
    """
    html += "</body>\n</html>"
    return html

if __name__ == '__main__':
    debug = 1
    main()
