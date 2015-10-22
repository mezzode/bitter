#!/usr/bin/python

# written by andrewt@cse.unsw.edu.au September 2015
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/bitter/

import cgi, cgitb, glob, os, datetime, time, re, Cookie, random, uuid

dataset_size = "medium" 
users_dir = "dataset-%s/users"% dataset_size
bleats_dir = "dataset-%s/bleats"% dataset_size
active_user = None

class user(object):
    """Bitter user"""
    def __init__(self, user):
        # super(user, self).__init__()
        # self.arg = arg
        self.details = {}
        self.pic = os.path.join(users_dir,user,"profile.jpg")
        with open(os.path.join(users_dir,user,"details.txt")) as f:
            # details = f.read()
            for line in f:
                field, _, value = line.rstrip().partition(": ")
                # if field == "listens":
                    # list?
                self.details[field] = value
            if "listens" not in self.details:
                self.details['listens'] = ''
        with open(os.path.join(users_dir,user,"bleats.txt")) as f:
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
    global active_user
    print "Content-Type: text/html"
    cgitb.enable()
    parameters = cgi.FieldStorage()
    # active_user = None
    failed_login = False
    if "HTTP_COOKIE" in os.environ:
        cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
        if "session" in cookie:
            session = cookie["session"].value
            with open("sessions.txt") as f:
                lines = f.readlines()
                if (session + "\n") in lines:
                    active_user, session_id = session.split()
    if parameters.getvalue('logout') and active_user:
        with open('sessions.txt') as f:
            sessions = f.readlines()
        session = active_user + ' ' + session_id + '\n'
        if session in sessions:
            sessions.remove(session)
        with open('sessions.txt','w') as f:
            f.writelines(sessions)
        # disable cookie?
        active_user = None
    elif parameters.getvalue('password') != None and parameters.getvalue('username') != None:
        # need a page if incorrect username/password
        if authenticate(parameters):
            issue_token(parameters)
            active_user = parameters.getvalue('username')
        else:
            failed_login = True
    print # end header
    if active_user != None: # someone is logged in
        pass # so render pages to reflect their personal details
    page_header()
    print "<!-- active_user: %s -->" % active_user
    navbar()
    print main_form()
    if active_user != None: # someone is logged in
        print "<!-- %s is logged in -->" % active_user # so render pages to reflect their personal details
    # print os.getenv('QUERY_STRING')
    if False: #'new-bleat' in parameters: # parameters.getvalue('new-bleat') != None:
        # new bleat
        new_bleat(parameters)
    elif parameters.getvalue('listen') != None:
        if parameters.getvalue('listen') in os.listdir(users_dir):
            add_listen(parameters)
    elif parameters.getvalue('delete-bleat') != None:
        if parameters.getvalue('delete-bleat') in os.listdir(bleats_dir):
            delete_bleat(parameters.getvalue('delete-bleat'))
    global page
    page = int(parameters.getfirst('page','1'))
    if failed_login:
        print "Incorrect username/password."
    elif 'new-user' in parameters:
        new_user_page(parameters)
    elif parameters.getvalue('user') != None:
        if parameters.getvalue('user') in os.listdir(users_dir):
            user_page(parameters)
        else:
            user_missing(parameters.getvalue('user'))
    elif parameters.getvalue('bleat') != None:
        if parameters.getvalue('bleat') in os.listdir(bleats_dir):
            bleat_page(parameters)
        else:
            bleat_missing()
    elif 'search' in parameters: # parameters.getvalue('search') != None:
        # print search_page(parameters)
        # bleat_search(parameters)
        if parameters.getfirst('type') == 'bleat':
            bleat_search(parameters)
        else:
            user_search(parameters)
    else:
        if active_user:
            dashboard()
        else:
            landing_page()
    print page_trailer(parameters)

def new_user():
    # with open(os.path.join(users_dir,user,"details.txt"),'w') as f:
        pass

def new_user_page(parameters):
    valid = True
    if parameters.getfirst('new-username') in os.listdir(users_dir):
        valid = False # username taken
        username_msg = 'Username already taken.'
        username_class = ' has-error' # for if interpolating class, may be better?
    elif not re.match(r'^\w+$',parameters.getfirst('new-username','')): # if matches regex
        valid = False # username taken
        username_msg = 'Invalid username.'
        username_class = ' has-error' # for if interpolating class, may be better?
    else:
        username_msg = ''
        username_class = '' # for if interpolating class, may be better?
    if not re.match(r'^[A-Za-z\-]+( [A-Za-z\-]+)*$',parameters.getfirst('full-name','')): # if matches regex
        valid = False # username taken
        name_msg = 'Full name required.'
    else:
        name_msg = ''
    if not re.match(r'^[^@\s]+@[\w\-]+(\.[\w\-]+)+$',parameters.getfirst('email','')): # if matches regex
        valid = False # username taken
        email_msg = 'Invalid email address.'
    else:
        email_msg = ''
    if parameters.getfirst('new-password','') != parameters.getfirst('new-password-confirm',''):
        valid = False
        password_msg = 'Passwords do not match.'
    elif not parameters.getfirst('new-password') or not parameters.getfirst('new-password-confirm'):
        valid = False
        password_msg = 'Password is required.'
    else:
        password_msg = ''
    
    if valid == True:
        new_user()
        # and print page saying email confirmation has been sent
    else:
        print """<div class="container">
    <div class="row">
        <div class="col-md-3">
        </div>
        <div class="col-md-6 col-md-12">
            <h1>New Profile</h1>
            <form method="POST">
                <div id="new-user-required">
"""
        if name_msg:
            print '<div class="form-group has-error">\n'
        else:
            print '<div class="form-group">\n'
        print """<label>Full Name</label>
                    <input type="text" name="full-name" value="%s" class="form-control" placeholder="Full Name">
                    <span id="name-help" class="help-block">%s</span>
                </div>""" % (parameters.getfirst('full-name',''),name_msg)
        if email_msg:
            print '<div class="form-group has-error">\n'
        else:
            print '<div class="form-group">\n'
        print """<label>Email Address</label>
                    <input type="email" name="email" value="%s" class="form-control" placeholder="Email">
                    <span id="email-help" class="help-block">%s</span>
                </div>""" % (parameters.getfirst('email',''),email_msg)
        #if username_msg:
        #    print '<div class="form-group has-error">\n'
        #else:
        #    print '<div class="form-group">\n'
        print """<div class="form-group%s">
        <label>Username</label>
                    <input type="text" name="new-username" value="%s" class="form-control" placeholder="Username">
                    <span id="username-help" class="help-block">%s</span>
                </div>""" % (username_class,parameters.getfirst('new-username',''),username_msg)
        if password_msg:
            print '<div class="form-group has-error">\n'
        else:
            print '<div class="form-group">\n'
        print """<label>Password</label>
                    <input type="password" name="new-password" value="%s" class="form-control" placeholder="Password">
                </div>""" % (parameters.getfirst('new-password',''))
        if password_msg:
            print '<div class="form-group has-error">\n'
        else:
            print '<div class="form-group">\n'
        print """<label>Confirm Password</label>
                    <input type="password" name="new-password-confirm" value="%s" class="form-control" placeholder="Confirm Password">
                    <span id="password-help" class="help-block">%s</span>
                </div>""" % (parameters.getfirst('new-password-confirm',''),password_msg)
    
        print """<button id="new-user-submit" type="button" name="new-user" value="submit" class="btn btn-primary">Submit</button>
        </div>
        </form>
        </div>
        <div class="col-md-3">
        </div>
    </div>
</div>"""
    return
    print """<div class="container">
    <div class="row">
        <div class="col-md-3">
        </div>
        <div class="col-md-6 col-md-12">
            <h1>New Profile</h1>
            <form method="POST">
                <div id="new-user-required">
                <div class="form-group">
                    <label>Full Name</label>
                    <input type="text" name="full-name" value="%s" class="form-control" placeholder="Full Name">
                    <span id="name-help" class="help-block"></span>
                </div>
                <!-- <div class="form-group">
                    <label>Profile Picture</label>
                    <input type="file">
                    <p class="help-block">Profile picture.</p>
                </div> -->
                <div class="form-group">
                    <label>Email address</label>
                    <input type="email" name="email" value="%s" class="form-control" placeholder="Email">
                    <span id="email-help" class="help-block"></span>
                </div>
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="new-username" value="%s" class="form-control" placeholder="Username">
                    <span id="username-help" class="help-block"></span>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="new-password" value="%s" class="form-control" placeholder="Password">
                </div>
                <div class="form-group">
                    <label>Confirm Password</label>
                    <input type="password" name="new-password-confirm" value="%s" class="form-control" placeholder="Confirm Password">
                    <span id="password-help" class="help-block"></span>
                </div>
                </div><!-- Compulsory -->
                <!-- <div class="collapse" id="new-user-optional">
                <h2>Home Details <small>(Optional)</small></h2>
                <div class="form-group">
                    <label>Suburb</label>
                    <input type="text" name="suburb" class="form-control" placeholder="Suburb">
                </div>
                <div class="form-group">
                    <label>Latitude</label>
                    <input type="text" name="latitude" class="form-control" placeholder="Latitude">
                </div>
                <div class="form-group">
                    <label>Longitude</label>
                    <input type="text" name="longitude" class="form-control" placeholder="Longitude">
                </div>
                </div> -->
                <button id="new-user-submit" type="button" name="new-user" value="submit" class="btn btn-primary">Submit</button>
            </form>
        </div>
        <div class="col-md-3">
        </div>
    </div>
</div>
""" % (parameters.getfirst('full-name',''),parameters.getfirst('email',''), parameters.getfirst('new-username',''),parameters.getfirst('new-password',''),parameters.getfirst('new-password-confirm',''))

def bleat_page(parameters):
    bleat_details = bleat_panel(parameters.getvalue('bleat'))
    print """<div class="container">
<div class="row">
    <div class="col-md-3">
    </div>
    <div class="col-md-6 col-sm-12">
    %s
    </div>
    <div class="col-md-3">
    </div>""" % bleat_details

def dashboard():
    curr_user = user(active_user)
    listens = curr_user.details['listens'].split()
    listens.append(active_user) # or manually listen to self?
    bleats = []
    for listen in listens:
        curr_user = user(listen)
        bleats += curr_user.bleats
    bleat_details = bleat_panels(sorted(bleats,reverse=True))
    page_details = paginator('',len(bleats) / 16 + (len(bleats) % 16 > 0))
    print """<div class="container">
<div class="row">
    <div class="col-md-3">
    </div>
    <div class="col-md-6 col-sm-12">
    %s
    %s
            <!-- <nav>
              <div class="text-center">
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
              </div>
              </nav> -->
    </div>
    <div class="col-md-3">
    </div>""" % (bleat_details,page_details)

def paginator(origin,pages): # TODO Need parameters so goes to same url
    if origin:
        origin += '&'
    page_details = """<nav>
    <div class="text-center">
    <ul class="pagination">"""
    if page <= 11:
        start = 1
        end = pages+1
    else:
        start = page - 5
        if pages < page + 5:
            end = pages + 1
        else:
            end = page + 6
    for i in range(start,page):
        page_details += '<li><a href="?%spage=%s">%s</a></li>\n' % (origin,i,i)
    page_details += '<li class="active"><a href="?%spage=%s">%s</a></li>\n' % (origin,page,page)
    for i in range(page+1,end):
        page_details += '<li><a href="?%spage=%s">%s</a></li>\n' % (origin,i,i)
    page_details += """</ul>
    </div>
    </nav>
    """
    return page_details

def landing_page():
    print """<div class="jumbotron">
    <div class="container">
<div class="row">
    <div class="col-md-12">
    <!-- <div class="jumbotron"> -->
    <h1>Welcome to Bitter</h1>
    <p>The latest and greatest thing since sliced bread!</p>
    <p><a class="btn btn-primary btn-lg" href="" role="button">Join Now</a></p>
    </div>
    </div>
    </div>
    </div>
    <div class="container">
<div class="row">
    <div class="col-md-6 col-sm-6">
    <h2>Featured</h2>
    </div>
    <div class="col-md-6 col-sm-6">
    <h2>Most Recent</h2>
    </div>
    </div>
    </div>
    """


def authenticate(parameters):
    # validate; if username and pass do not match the records, divert to incorrect pass screen
    username = parameters.getvalue('username')
    password = parameters.getvalue('password')
    # with open(os.path.join(users_dir,username,'details.txt') as f:
    if username not in os.listdir(users_dir):
        return False
    curr_user = user(username)
    if password == curr_user.details['password']:   
        return True
    else:
        return False
        cookie = Cookie.SimpleCookie()
        # session_id = random.getrandbits(128)
        session_id = uuid.uuid4()
        session = username + " " + str(session_id)
        cookie['session'] = session
        if parameters.getvalue('remember-me'): # for 30 days
            # expiration = datetime.datetime.now() + datetime.timedelta(days=30)
            # cookie['session']['expires'] = expiration.bleh  # Sun, 15 Jul 2012 00:00:01 GMT
            cookie['session']['max-age'] = 60 * 60 * 24 * 30
        with open('sessions.txt','a') as f:
            f.write(session+"\n")
        print cookie.output()

def issue_token(parameters):
    cookie = Cookie.SimpleCookie()
    username = parameters.getvalue('username')
    # session_id = random.getrandbits(128)
    session_id = uuid.uuid4()
    session = username + " " + str(session_id)
    cookie['session'] = session
    if parameters.getvalue('remember-me'): # for 30 days
        # expiration = datetime.datetime.now() + datetime.timedelta(days=30)
        # cookie['session']['expires'] = expiration.bleh  # Sun, 15 Jul 2012 00:00:01 GMT
        cookie['session']['max-age'] = 60 * 60 * 24 * 30
    with open('sessions.txt','a') as f:
        f.write(session+"\n")
    print cookie.output()

def new_bleat(parameters):
    text = cgi.escape(parameters.getvalue('new-bleat'))
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

def delete_bleat(bleat_id):
    bleat = {}
    lines = []
    with open(os.path.join(bleats_dir,bleat_id)) as f:
        lines = f.readlines()
        for line in lines:
            field, _, value = line.rstrip().partition(": ")
            bleat[field] = value
    lines = ['deleted\n'] + lines
    with open(os.path.join(bleats_dir,bleat_id),'w') as f:
        f.writelines(lines)
    username = bleat['username']
    bleats = []
    with open(os.path.join(users_dir,username,'bleats.txt')) as f:
        bleats = f.readlines()
    if (bleat_id+"\n") in bleats:
        bleats.remove(bleat_id+"\n")
    with open(os.path.join(users_dir,username,'bleats.txt'),'w') as f:
        f.writelines(bleats)
    # os.remove(os.path.join(bleats_dir,bleat_id)) # maybe just keep "deleted" bleats
    print """<div class="alert alert-info alert-dismissible toast fade in" id="bleat-alert" role="alert">
<button type="button" class="close" data-dismiss="alert"><span>&times;</span></button>
Bleat deleted.
</div>
    """

def main_form():
    return """<form method="POST" action="" id="main">
</form>"""

def add_listen(parameters):
    user = parameters.getvalue('listen')
    lines = []
    field = ""
    message = ""
    with open(os.path.join(users_dir,active_user,'details.txt')) as f:
        lines = f.readlines()
    for index, line in enumerate(lines):
        field, _, value = line.rstrip().partition(": ")
        if field == "listens":
            listens = value.split()
            if user not in listens: # listen
                lines[index] = field + ": " + value.rstrip() + " " + user + "\n"
                message = "You are now listening to"
            else: # unlisten
                listens.remove(user)
                if listens: # if there are still listens
                    lines[index] = field + ": " + ' '.join(listens) + "\n"
                else:
                    del lines[index]
                message = "You have stopped listening to"
            break
    if field != "listens": # if no listens
        lines.append("listens: " + user + "\n")
        message = "You are now listening to"
    with open(os.path.join(users_dir,active_user,'details.txt'),'w') as f:
        f.writelines(lines)
    print """<div class="alert alert-info alert-dismissible toast fade in" id="bleat-alert" role="alert">
<button type="button" class="close" data-dismiss="alert"><span>&times;</span></button>
%s <strong>%s</strong>.
</div>
    """ % (message,user)
    return

def bleat_panels(bleats):
    bleat_details = ""
    for bleat_id in bleats[(16*(page-1)):(16*page)]:
            bleat_details += bleat_panel(bleat_id.rstrip())
    return bleat_details

def bleat_panel(bleat_id):
    curr_bleat = {}
    bleat_details = ""
    with open(os.path.join(bleats_dir,bleat_id)) as f:
        lines = f.readlines()
        if 'deleted\n' in lines:
            return '<h1 class="text-center">Bleat deleted</h1>'
        for line in lines:
            field, _, value = line.rstrip().partition(": ")
            curr_bleat[field] = value
    # bleat_details += '<li class="list-group-item">\n'
    # bleat_details += '<button class="panel panel-default" type="button" data-toggle="collapse" data-target="#%s" aria-expanded="false" aria-controls="%s">' % (bleat_id,bleat_id)
    bleat_details += '<div id="%s">' % bleat_id
    bleat_details += '<div class="panel panel-default">\n'
    bleat_details += '<div class="list-group">\n'
    bleat_details += '<div class="list-group-item">\n'
    # bleat_details += '<h4 class="list-group-item-heading">%s</h4>\n' % curr_bleat['username'] # user
    if active_user:
        if curr_bleat['username'] != active_user:
            if curr_bleat['username'] in user(active_user).details["listens"].split():
                listen_button = "heart"
            else:
                listen_button = "heart-empty"
            bleat_details += '<form method="POST"><button type="submit" name="listen" value="%s" style="margin-top: -4px;" href="#" class="btn-sm btn btn-link pull-right"><span class="glyphicon glyphicon-%s"></span></button></form>\n' % (curr_bleat['username'],listen_button)
        else:
            bleat_details += '<button type="button" data-bleat="%s" data-toggle="modal" data-target="#delete-bleat-dialog" style="margin-top: -4px;" class="btn-sm btn btn-link pull-right"><span class="glyphicon glyphicon-trash"></span></button>\n' % bleat_id
    bleat_details += '<a style="color: inherit;" class="list-group-item-heading" href="?user=%s"><h4 class="list-group-item-heading">%s</h4></a>\n' % (curr_bleat['username'],curr_bleat['username']) # user
    bleat_details += '<p class="lead">%s</p>\n' % curr_bleat['bleat'] # bleat
    bleat_details += '<ul class="list-inline">\n' # metadata
    bleat_details += datetime.datetime.fromtimestamp(int(curr_bleat['time'])).strftime('<li><small>%I:%M:%S %p</small></li>\n<li><small>%A, %d %B %Y</small></li>\n')
    if 'latitude' in curr_bleat and 'longitude' in curr_bleat:
        bleat_details += '<li><small>Location: %s, %s</small></li>\n' % (curr_bleat['latitude'],curr_bleat['longitude'])
    bleat_details += "</ul>\n"
    bleat_details += '<a href="?bleat=%s" class="btn-sm btn btn-link pull-right"><span class="glyphicon glyphicon-link"></span></a>\n' % bleat_id
    precursors = bleat_conversation(bleat_id)
    replies = bleat_replies(bleat_id)
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
    if active_user:
        bleat_details += """<li class="list-group-item">
    <form method="POST" bleat>
    <input type="hidden" name="new-bleat-user" value="%s">
    <input type="hidden" name="new-bleat-reply" value="%s">
    <div class="form-group">
    <textarea name="new-bleat" placeholder="Your reply" class="form-control" rows="3" maxlength="142"></textarea>
    <span id="helpBlock" class="help-block pull-right">0/142</span>
    </div>
    <button type="submit" class="btn btn-default" disabled="disabled">Submit</button>
</form>
</li>
</ul>
""" % (active_user,bleat_id)
    else:
        bleat_details += """<li class="list-group-item">
        <p class="list-group-item-text"><a href="" data-toggle="modal" data-target="#log-in">Login</a> to reply to this bleat</p>
</li>
</ul>
"""
    bleat_details += "</ul>\n</div>\n"
    # previous bleats in conversation:
    if precursors:
        bleat_details += """<div class="collapse panel-collapse" id="%s-conversations">
    <ul class="list-group">
""" % (bleat_id)
        for precursor in precursors:
            bleat_details += bleat_child(precursor)
        bleat_details += "    </ul>\n</div>\n"
    if replies:
        bleat_details += """<div class="collapse panel-collapse" id="%s-replies">
    <ul class="list-group">
""" % (bleat_id)
        for reply in replies:
            bleat_details += bleat_child(reply)
        bleat_details += "    </ul>\n</div>\n"
    bleat_details += "</div>\n" # panel
    bleat_details += "</div>\n"
    return bleat_details

# take a bleat and return a list of its replies
def bleat_replies(bleat_id):
    replies = []
    for curr_bleat in os.listdir(bleats_dir): # sort by time first?
        with open(os.path.join(bleats_dir,curr_bleat)) as f:
            lines = f.readlines()
            if 'deleted\n' in lines:
                continue
            for line in lines:
                field, _, value = line.rstrip().partition(": ")
                if field == "in_reply_to":
                    if value == bleat_id:
                        replies.append(curr_bleat)
                    else:
                        break
    return replies
    replies_details = ""
    for curr_bleat in replies:
         replies_details += bleat_child(curr_bleat)
    return replies_details

# take a bleat and return a list of its precursors
def bleat_conversation(bleat_id): # pass a dict/object instead of the id?
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
            lines = f.readlines()
            if 'deleted\n' in lines:
                precursors.pop() # remove the deleted bleat
                precursors.append('deleted')
            precursor = None
            for line in lines:
                field, _, value = line.rstrip().partition(": ")
                if field == "in_reply_to":
                    precursors.append(value)
                    precursor = value
                    break
    return precursors
    pre_details = ""
    for curr_bleat in precursors:
        pre_details += bleat_child(curr_bleat)
    return pre_details

def bleat_child(bleat_id):
    if bleat_id == 'deleted':
        return '''<li class="list-group-item">
<p class="lead">Deleted Bleat</p>
</li>'''
    curr_bleat = {}
    with open(os.path.join(bleats_dir,bleat_id)) as f:
        for line in f:
            field, _, value = line.rstrip().partition(": ")
            curr_bleat[field] = value
    if "in_reply_to" not in curr_bleat:
        curr_bleat["in_reply_to"] = "N/A"
    bleat_details = ''
    bleat_details += '<li class="list-group-item">\n'
    if active_user:
        if curr_bleat['username'] != active_user:
            if curr_bleat['username'] in user(active_user).details["listens"].split():
                listen_button = "heart"
            else:
                listen_button = "heart-empty"
            bleat_details += '<form method="POST"><button type="submit" name="listen" value="%s" style="margin-top: -4px;" href="#" class="btn-sm btn btn-link pull-right"><span class="glyphicon glyphicon-%s"></span></button></form>\n' % (curr_bleat['username'],listen_button)
        else:
            bleat_details += '<button type="button" data-bleat="%s" data-toggle="modal" data-target="#delete-bleat-dialog" style="margin-top: -4px;" class="btn-sm btn btn-link pull-right"><span class="glyphicon glyphicon-trash"></span></button>\n' % bleat_id
    bleat_details += '<a style="color: inherit;" class="list-group-item-heading" href="?user=%s"><h4 class="list-group-item-heading">%s</h4></a>\n' % (curr_bleat['username'],curr_bleat['username']) # user
    bleat_details += '<p class="lead">%s</p><!--this:%s in-reply-to:%s-->\n' % (curr_bleat['bleat'],bleat_id,curr_bleat['in_reply_to'])  # bleat
    bleat_details += '<a href="?bleat=%s" style="margin-top: -4px;" class="btn-sm btn btn-link pull-right"><span class="glyphicon glyphicon-link"></span></a>\n' % bleat_id
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

def bleat_missing():
    print '<h1 class="text-center">Bleat not found</h1>'

def user_missing(username):
    print '<h1 class="text-center">User not found<br><small>No user named "%s"</h1>' % username

def user_page(parameters):
    # n = int(parameters.getvalue('n', 0))
    username = parameters.getvalue('user')
    # if user_to_show != '':
    #     user_to_show = os.path.join(users_dir,user_to_show)
    # else:
    #    users = sorted(glob.glob(os.path.join(users_dir, "*")))
    #    user_to_show  = users[n % len(users)]
    curr_user = user(username)
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
    for listen in listens.split():
        curr_listen = user(listen)
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
    if active_user:
        if curr_user.details['username'] in user(active_user).details["listens"].split():
            listen_button = '<span class="glyphicon glyphicon-heart"></span>  Stop Listening'
        else:
            listen_button = '<span class="glyphicon glyphicon-heart-empty"></span>  Listen'
    print """
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
            """ % (curr_user.pic, details, listen_details,home_details) 
    if active_user and active_user != curr_user.details['username']:
        print """<form method="POST"><!-- id="main"> -->
                <button type="submit" name="listen" value="%s" class="btn btn-default toaster">%s</button>
            </form>""" % (curr_user.details['username'],listen_button)
    print "</div>"
    page_details = paginator('user='+curr_user.details['username'],len(curr_user.bleats) / 16 + (len(curr_user.bleats) % 16 > 0))
    print  """ <div class="col-md-6 col-sm-7">
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
            <!-- <nav>
              <div class="text-center">
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
              </div>
            </nav> -->
            %s
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
""" % (bleat_panels(curr_user.bleats),page_details)

def user_search(parameters):
    search_term = parameters.getfirst('search')
    matches = []
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
    user_panels = ""
    for match in matches[(16*(page-1)):(16*page)]:
        curr_user = user(match)
        user_panels += """<a href="?user=%s" class="list-group-item">
<div class="media">
    <div class="media-left">
        <img class="media-object" src="%s" height="100" width="100">
    </div>
    <div class="media-body">
        <h3 class="media-heading">%s<br><small>%s</small></h3>
    </div>
</div>
</a>
""" % (match,curr_user.pic,curr_user.details["full_name"],match)
    # bleat_panels(matches)
    # page_details = paginator('',len(bleats) / 16 + (len(bleats) % 16 > 0))
    print """
<div class="container">
    <div class="row">
        <div class="col-md-12 col-sm-12">
            <h2> Search Results: <small>%s</small></h2>
            <ul class="nav nav-pills">
                <li role="presentation" class="active"><a href="#">Users</a></li>
                <li role="presentation"><a href="?search=%s&type=bleat">Bleats</a></li>
            </ul>
            <br>
            <div class="panel panel-default">
            %s
            </div>
            %s
        </div>
    </div>
</div>
""" % (search_term,search_term,user_panels,paginator('search='+search_term,len(matches) / 16 + (len(matches) % 16 > 0)))

def bleat_search(parameters):
    search_term = parameters.getfirst('search')
    matches = []
    for curr_bleat in os.listdir(bleats_dir):
        with open(os.path.join(bleats_dir,curr_bleat)) as f:
            lines = f.readlines()
            if 'deleted\n' in lines:
                continue
            for line in lines:
                field, _, value = line.rstrip().partition(": ")
                if field == "bleat":
                    if search_term.lower() in value.lower():
                        matches.append(curr_bleat)
                    else:
                        break
    # bleat_panels(matches)
    # page_details = paginator('',len(bleats) / 16 + (len(bleats) % 16 > 0))
    print """
<div class="container">
    <div class="row">
        <div class="col-md-12 col-sm-12">
            <h2> Search Results: <small>%s</small></h2>
            <ul class="nav nav-pills">
                <li role="presentation"><a href="?search=%s">Users</a></li>
                <li role="presentation" class="active"><a href="#">Bleats</a></li>
            </ul>
            <br>
            %s
            %s
        </div>
    </div>
</div>
""" % (search_term,search_term,bleat_panels(matches),paginator('search='+search_term+'&type=bleat',len(matches) / 16 + (len(matches) % 16 > 0)))

def search_page(parameters):
    search_term = parameters.getfirst('search')
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
        curr_user = user(match)
        user_results += """<a href="?user=%s" class="list-group-item">
<div class="media">
    <div class="media-left">
        <img class="media-object" src="%s" height="100" width="100">
    </div>
    <div class="media-body">
        <h3 class="media-heading">%s<br><small>%s</small></h3>
    </div>
</div>
</a>
""" % (match,curr_user.pic,curr_user.details["username"],match)
    matches = []
    for curr_bleat in os.listdir(bleats_dir):
        with open(os.path.join(bleats_dir,curr_bleat)) as f:
            lines = f.readlines()
            if 'deleted\n' in lines:
                continue
            for line in lines:
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
            <!-- div class="panel panel-primary">
                <div class="panel-body">
                    <h2 class="list-group-item-heading">Search Results: <small></small></h2>
                </div>
            </div> -->
            <h2> Search Results: <small>%s</small></h2>
            <ul class="nav nav-pills">
                <li role="presentation" class="active"><a href="#users" data-toggle="pill">Users</a></li>
                <li role="presentation"><a href="#bleats" data-toggle="pill">Bleats</a></li>
                <!-- <li role="presentation"><a href="#">All</a></li> -->
            </ul>
            <br>
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
""" % (search_term,user_results,bleat_panels(matches))

#
# HTML placed at the top of every page
#
def page_header():
    print """<!DOCTYPE html>
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
"""

def navbar():
    print """<!-- active_user: %s -->
    <nav class="navbar navbar-default navbar-fixed-top">
            <div class="container">
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                        <span class="sr-only">Toggle nagivation</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>  
                        <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" href="?">Bitter</a>
                    <!-- <input type="reset" class="navbar-brand" value="Bitter"> -->
                </div>

                <div id="navbar" class="collapse navbar-collapse">
                    <!-- <ul class="nav navbar-nav">
                        <li class="active"><input type="reset" value="Home" class="btn btn-link navbar-btn"><span class="sr-only">(current)</span></a></li>
                        <li><a href="#">New Bleat</a></li>
                        <li class="active"><input type="submit" value="New Bleat" class="btn btn-link navbar-btn"><span class="sr-only">(current)</span></a></li>
                    </ul> -->
                    <form class="navbar-form navbar-left" id="search" role="search">
                    <!-- <input type="submit" value="Home" class="btn btn-link" name=".defaults">
                    <input type="submit" value="Bleats" class="btn btn-link"> -->
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
                        <input type="text" name="search" class="form-control" placeholder="Search">
                        <span class="input-group-btn">
                            <button type="submit" class="btn btn-link">
                                <span class="glyphicon glyphicon-search" aria-hidden="true"></span>
                            </button>
                        </span>
                    </div>
                    </form>
                    """ % active_user
    if active_user:
        curr_user = user(active_user)
        if "full_name" in curr_user.details:
            name = curr_user.details['full_name']
        else:
            name = active_user
        print """<ul class="nav navbar-nav navbar-right">
    <li><p class="navbar-text">Signed in as <a href="?user=%s" class="navbar-link">%s</a></p></li>
    <li><form method="POST"><button class="btn btn-link navbar-btn" type="submit" name="logout" value="True">Log Out</button></form></li>
</ul>
</div>
</div>
</nav>""" % (active_user,name)
        print """<button class="fab-fixed mdl-button mdl-js-button mdl-button--fab mdl-js-ripple-effect mdl-button--colored" data-toggle="modal" data-target="#new-bleat-dialog">
                <i class="material-icons">create</i>
        </button>"""
        print """<div class="modal fade" id="new-bleat-dialog" tabindex="-1" role="dialog">
<div class="modal-dialog">
    <div class="modal-content">
        <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal"><span>&times;</span></button>
            <h4 class="modal-title">New Bleat</h4>
        </div>
        <div class="modal-body">
            <form method="POST" bleat>
            <input type="hidden" name="new-bleat-user" value="%s">
            <div class="form-group">
                <textarea name="new-bleat" placeholder="Your bleat" class="form-control" rows="3" maxlength="142"></textarea>
                <span id="helpBlock" class="help-block pull-right">0/142</span>
            </div>
            <button type="submit" class="btn btn-default" disabled="disabled">Submit</button>
            </form>
        </div>
    </div>
</div>
</div><!-- New Bleat Modal -->
""" % active_user
        print """<div class="modal fade" id="delete-bleat-dialog" tabindex="-1" role="dialog">
<div class="modal-dialog">
    <div class="modal-content">
        <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal"><span>&times;</span></button>
            <h4 class="modal-title">Delete Bleat</h4>
        </div>
        <div class="modal-body">
            <p>Are you sure you want to delete this bleat?</p>
        </div>
            <!-- <form method="POST" bleat>
            <input type="hidden" name="new-bleat-user" value="%s">
            <div class="form-group">
                <textarea name="new-bleat" placeholder="Your bleat" class="form-control" rows="3" maxlength="142"></textarea>
                <span id="helpBlock" class="help-block pull-right">0/142</span>
            </div>
            <button type="submit" class="btn btn-default" disabled="disabled">Submit</button>
            </form>
        </div> -->
        <div class="modal-footer">
            <form method="POST">
            <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
            <button type="submit" name="delete-bleat" class="btn btn-danger">Delete Bleat</button>
            </form>
        </div>
    </div>
</div>
</div><!-- New Bleat Modal -->
""" % active_user
    else: # just print disabled button
        print """<!-- <ul class="nav navbar-nav navbar-right">
    <li><button class="btn btn-link navbar-btn" data-toggle="modal" data-target="">Log In</button></li>
</ul> -->
<button class="btn btn-link navbar-btn navbar-right" data-toggle="modal" data-target="#log-in">Log In</button>
</div>
            </div>
        </nav>
        <div class="modal fade" id="log-in" tabindex="-1" role="dialog">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal"><span>&times;</span></button>
                        <h4 class="modal-title">Log In</h4>
                    </div>
                    <div class="modal-body">
                        <form method="POST" login>
                        <div class="form-group">
                        <input type="text" class="form-control" name="username" placeholder="Username">
                        </div>
                        <div class="form-group">
                        <input type="password" class="form-control" name="password" placeholder="Password">
                        </div>
                        <div class="checkbox">
                            <label>
                                <input type="checkbox" name="remember-me"> Remember Me
                             </label>
                        </div>
                        <button type="submit" class="btn btn-default" disabled="disabled">Submit</button>
                        
                        </form>
                    </div>
                </div>
            </div>
        </div>
        <div class="fab-fixed" data-toggle="tooltip" data-placement="left" title="Login to bleat">
            <button disabled="disabled" class="mdl-button mdl-js-button mdl-button--fab mdl-js-ripple-effect mdl-button--colored">
                <i class="material-icons">create</i>
            </button>
        </div>
"""
    return

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

    $('[bleat]').on('input', function () {
        var area = $("textarea",this);
        $("textarea",this).val($("textarea",this).val().replace(/\\n/g,''));
        var count = $("textarea",this).val().length;
        if (count > 0) {
            $("button",this).attr("disabled",false);
        } else {
            $("button",this).attr("disabled","disabled");
        }
        $("span.help-block",this).text(count+'/142');
        // alert(">>"+count);
    })

    $('[bleat]').keypress(function(e) {
        if (e.which == 13) { // enter key
            this.submit()
        }
    })

    $('#new-user-submit').click(function() {
        $('div.form-group',$('#new-user-required')).each(function(i){
            if ($('input',this).val().length == 0){
                $(this).addClass('has-error');
            } else {
                $(this).removeClass('has-error');
            }
            if ($('input',this).attr("name") == 'email'){
                if (/^[^@\s]+@[\w\-]+(\.[\w\-]+)+$/.test($('input[name="email"]',this).val())){
                    $(this).removeClass('has-error');
                    $('#email-help').text('');
                } else {
                    $(this).addClass('has-error');
                    $('#email-help').text('Invalid email address.');
                }
            } else if ($('input',this).attr("name") == 'full-name'){
                if (/^[A-Za-z\-]+( [A-Za-z\-]+)*$/.test($('input[name="full-name"]',this).val())){
                    $(this).removeClass('has-error');
                    $('#name-help').text('');
                } else {
                    $(this).addClass('has-error');
                    $('#name-help').text('Full name required.');
                }
            } else if ($('input',this).attr("name") == 'new-username'){
                if (/^\w+$/.test($('input[name="new-username"]',this).val())){
                    $(this).removeClass('has-error');
                    $('#username-help').text('');
                } else {
                    $(this).addClass('has-error');
                    $('#username-help').text('Invalid username.');
                }
            }
        });
        if ($('input[name="new-password"]').val() != $('input[name="new-password-confirm"]').val()){
            $('input[name="new-password"]').parent().addClass('has-error');
            $('input[name="new-password-confirm"]').parent().addClass('has-error');
            $('#password-help').text('Passwords do not match.');
            // alert('moo');
            // $("span.help-block",this).text(count+'/142');
        } else if ($('input[name="new-password"]').val() == '' && $('input[name="new-password-confirm"]').val() == ''){
            $('input[name="new-password"]').parent().addClass('has-error');
            $('input[name="new-password-confirm"]').parent().addClass('has-error');
            $('#password-help').text('Password is required.');
            // alert('oom');
        } else {
            $('#password-help').text('');
            // alert('foo');
        }
        var all_valid = 1;
        $('div.form-group',$('#new-user-required')).each(function(i){
            if ($(this).hasClass("has-error")){
                all_valid = 0;
            }
        });
        if (all_valid){
            alert('submit');
        }
    });
    
    // remove error styling once edited
    $('div.form-group input').on('input', function () {
        // alert('af');
        $(this).parent().removeClass('has-error');
        if ($(this).attr('name') == 'new-password'){
            $('input[name="new-password-confirm"]').parent().removeClass('has-error');
        } else if ($(this).attr('name') == 'new-password-confirm'){
            $('input[name="new-password"]').parent().removeClass('has-error');
        }
    });

    /* // limit names to alphabet
    $('input[name="full-name"]').on('input', function () {
        var area = $("textarea",this);
        $(this).val($(this).val().replace(/[^A-Za-z ]/g,''));
    });
    
    // limit usernames to word chars
    $('input[name="new-username"]').on('input', function () {
        var area = $("textarea",this);
        $(this).val($(this).val().replace(/\W/g,''));
    }); */

    $('[login]').on('input', function () {
        var username = $("input[type=text]",this).val().length;
        var password = $("input[type=password]",this).val().length;
        // var count = username.val().length + password.val().length
        if ((username > 0) && (password > 0)) {
            $("button",this).attr("disabled",false);
        } else {
            $("button",this).attr("disabled","disabled");
        }
        // $("span.help-block",this).text(count+'/142');
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

    $('#delete-bleat-dialog').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget)
        var bleat = button.data('bleat')
        $('button.btn-danger',this).val(bleat)
    });

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
