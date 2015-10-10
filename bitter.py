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
    print user_page(parameters, users_dir, bleats_dir)
    print page_trailer(parameters)


#
# Show unformatted details for user "n".
# Increment parameter n and store it as a hidden variable
#
def user_page(parameters, users_dir, bleats_dir):
    n = int(parameters.getvalue('n', 0))
    users = sorted(glob.glob(os.path.join(users_dir, "*")))
    user_to_show  = users[n % len(users)]
    curr_user = user(user_to_show)
    if curr_user.details["full_name"] != None:
        details = "<h1>%s <small>%s</small></h1>\n" % (curr_user.details["full_name"],curr_user.details["username"])
        # details += '<h1><small>%s</small></h1>\n' % curr_user.details["username"]
    else:
        details = "<h1>%s</h1>\n" % curr_user.details["username"]
    details += curr_user.details_basic()
    bleat_details = ""
    curr_bleat = {}
    for bleat_id in curr_user.bleats:
        with open(os.path.join(bleats_dir,bleat_id.rstrip())) as f:
            for line in f:
                field, _, value = line.rstrip().partition(": ")
                curr_bleat[field] = value
        bleat_details += '<li class="list-group-item">'
        for field in sorted(curr_bleat): # sorted
            if field not in ["time"]:
                bleat_details += "<p>%s: %s</p>\n" % (field,curr_bleat[field])
            elif field == "time":
                # bleat_details += datetime.datetime.fromtimestamp(int(curr_bleat[field])).strftime('%I:%M:%S%p, %d %B %Y (%Z)') #'%Y-%m-%d %H:%M:%S')
                bleat_details += datetime.datetime.fromtimestamp(int(curr_bleat[field])).strftime('<p>%I:%M:%S%p (%Z)</p>\n<p>%A, %d %B %Y</p>\n')
        bleat_details += "</li>\n"
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
            </div>
            <p>
            <form method="POST" action="">
                <input type="hidden" name="n" value="%s">
                <input type="submit" value="Next user" class="btn btn-default">
            </form>
        </div>
        <div class="col-md-6 col-sm-7">
            <div class="panel panel-primary">
                <div class="panel-body">
                    <h1>Bleats</h1>
                </div>
                <ul class="list-group">
                    %s
                </ul>
            </div>
        </div>
        <div class="col-md-3 col-sm-7">
            <div class="panel panel-primary">
                <div class="panel-body">
                    <p>Bleh</p>
                </div>
            </div>
        </div>
    </div>
</div>
""" % (curr_user.pic, details, n + 1,bleat_details) 


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
		body { padding-top: 70px; }
		</style>
    </head>
    <body>
        <!-- <div class="bitter_heading">Bitter</div> -->
        <!-- <h1>Bitter</h1> -->
		<nav class="navbar navbar-default navbar-fixed-top">
			<div class="container">
				<div class="navbar-header">
					<button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
						<span class="sr-only">Toggle nagivation</span>
						<span class="icon-bar"></span>
						<span class="icon-bar"></span>	
						<span class="icon-bar"></span>
					</button>
					<a class="navbar-brand" href="#">Bitter</a>
				</div>

				<div id="navbar" class="collapse navbar-collapse">
					<ul class="nav navbar-nav">
						<li class="active"><a href="#">Home<span class="sr-only">(current)</span></a></li>
						<li><a href="#">New Bleat</a></li>
					</ul>
					<form class="navbar-form navbar-left" role="search">
					<div class="input-group">
						<input type="text" class="form-control" placeholder="Search">
						<span class="input-group-btn">
							<button type="submit" class="btn btn-default">
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
