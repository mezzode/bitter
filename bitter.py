#!/usr/bin/python

# written by andrewt@cse.unsw.edu.au September 2015
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/bitter/

import cgi, cgitb, glob, os, datetime

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
            self.bleats = f.readlines()
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
    if parameters.getvalue('user') != None:
        print user_page(parameters, users_dir, bleats_dir)
    elif parameters.getvalue('search_term') != None:
        print search_page(parameters,users_dir,bleats_dir)
    else:
        print user_page(parameters, users_dir, bleats_dir)
    print page_trailer(parameters)

def main_form():
    return """<form method="POST" action="" id="main">
</form>"""

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
    bleat_details += '<div class="panel panel-default">\n'
    bleat_details += '<div class="list-group">\n'
    bleat_details += '<div class="list-group-item">\n'
    bleat_details += '<h4 class="list-group-item-heading">%s</h4>\n' % curr_bleat['username']
    bleat_details += '<p class="lead">%s</p>\n' % curr_bleat['bleat']
    bleat_details += '<ul class="list-inline">\n'
    bleat_details += datetime.datetime.fromtimestamp(int(curr_bleat['time'])).strftime('<li><small>%I:%M:%S %p</small></li>\n<li><small>%A, %d %B %Y</small></li>\n')
    if 'latitude' in curr_bleat and 'longitude' in curr_bleat:
        bleat_details += '<li><small>Location: %s, %s</small></li>\n' % (curr_bleat['latitude'],curr_bleat['longitude'])
    bleat_details += "</ul>\n"
    bleat_details +='<p><a data-toggle="collapse" href="#%s"><small>View conversation</small></a></p>\n' % bleat_id
    # bleat_details += "</li>\n"
    bleat_details += "</div>\n</div>\n"
    # bleat_details += "</button>\n"
    # bleat_details += "</div>"
    # previous bleats in conversation:
    bleat_details += """<div class="collapse panel-collapse" id="%s">
    <div class="list-group">
        <button type="submit" form="main" name="user" value="VitaliKlitschko" class="list-group-item">
        <h4 class="list-group-item-heading">Bleat</h4>
        <p>Bleat here</p>
        </button>
        <button type="submit" form="main" name="user" value="VitaliKlitschko" class="list-group-item">
        <h4 class="list-group-item-heading">Bleat</h4>
        <p>Bleat here</p>
        </button>
    </div>
</div></div>""" % bleat_id
    return bleat_details

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
    if curr_user.details["full_name"] != None:
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
        listen_details += '<button type="submit" form="main" name="user" value=%s class="list-group-item">\n'% listen
        listen_details += '<div class="media">\n'
        listen_details += '    <div class="media-left">\n'
        listen_details += '        <img class="media-object" src="%s" height="64" width="64">\n' % curr_listen.pic
        listen_details += '    </div>\n'
        listen_details += '    <div class="media-body">\n'
        listen_details += '        <h4 class="media-heading">%s<br><small>%s</small></h4>\n' % (curr_listen.details["full_name"],listen)
        listen_details += '    </div>\n'
        listen_details += '</div>\n'
        listen_details += '</button>\n'
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
            <form method="POST" action=""><!-- id="main"> -->
                <input type="hidden" name="n" value="%s">
                <input type="submit" value="Next user" class="btn btn-default">
            </form>
        </div>
        <div class="col-md-6 col-sm-7">
            <div class="panel panel-primary">
                <div class="panel-body">
                    <h1 class="list-group-item-heading">Bleats</h1>
                </div>
            </div>
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
""" % (curr_user.pic, details, listen_details,home_details, n + 1,bleat_panels(curr_user.bleats,bleats_dir)) 

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
    bleat_results = ""
    for match in matches:
        # put bleat parsing here or use function
        bleat_results += """<button type="submit" form="main" name="user" value=%s class="list-group-item">
<p>%s</p>
</button>            
""" % (match,match)
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
                    <ul class="nav nav-pills">
                        <li role="presentation" class="active"><a href="#users" data-toggle="pill">Users</a></li>
                        <li role="presentation"><a href="#bleats" data-toggle="pill">Bleats</a></li>
                        <!-- <li role="presentation"><a href="#">All</a></li> -->
                    </ul>    
                </div>
                <ul class="list-group">
                <div class="tab-content">
                    <div role="tabpanel" class="tab-pane fade in active" id="users">
                        %s
                    </div>
                    <div role="tabpanel" class="tab-pane fade" id="bleats">
                        <!-- <li class="list-group-item"><h3>No results</h3></li> -->
                        %s
                    </div>
                </div>
                </ul>
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
""" % (search_term,user_results,bleat_results)

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
        <!-- Bootstrap -->
        <link href="css/bootstrap.min.css" rel="stylesheet">
        <!-- <link href="bitter.css" rel="stylesheet"> -->
        <style>
        body { padding-top: 80px; }
        </style>
    </head>
    <body>
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
    <script src="js/bootstrap.min.js"></script>"""
    html += "</body>\n</html>"
    return html

if __name__ == '__main__':
    debug = 1
    main()
