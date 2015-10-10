#!/usr/bin/python

# written by andrewt@cse.unsw.edu.au September 2015
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/bitter/

import cgi, cgitb, glob, os

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

    def details_full(self):
        details_formatted = ""
        # for field in vars(self):
        #     details += field + ": " + self.details[field]
        for field,_ in sorted(self.details.items()): # sorted
        # for field in self.details: # unsorted
            # details_formatted += field + ": " + self.details[field]
            details_formatted += "<p>%s: %s</p>\n" % (field,self.details[field])
        # return details # sorted(vars(self))
        return details_formatted


def main():
    print page_header()
    cgitb.enable()
    dataset_size = "small" 
    users_dir = "dataset-%s/users"% dataset_size
    parameters = cgi.FieldStorage()
    print user_page(parameters, users_dir)
    print page_trailer(parameters)


#
# Show unformatted details for user "n".
# Increment parameter n and store it as a hidden variable
#
def user_page(parameters, users_dir):
    n = int(parameters.getvalue('n', 0))
    users = sorted(glob.glob(os.path.join(users_dir, "*")))
    user_to_show  = users[n % len(users)]
    curr_user = user(user_to_show)
    details = curr_user.details_full()
    pic = curr_user.pic
    # details_filename = os.path.join(user_to_show, "details.txt")
    # with open(details_filename) as f:
    #     details = f.read()
    return """
<div class="container">
<div class="row">
<div class="col-sm-4 col-md-3">
<div class="panel panel-primary">
<div class="panel-body">
<img src="%s" class="img-responsive" alt="Profile Picture">
<p>
%s
</div>
</div>
<p>
<form method="POST" action="">
    <input type="hidden" name="n" value="%s">
    <input type="submit" value="Next user" class="btn btn-default">
</form>
</div>
<div class="col-md-6 col-sm-8">
<div class="panel panel-primary">
<div class="panel-body">
<p>Bleats</p>
</div>
</div>
</div>
<div class="col-md-3 col-sm-8">
<div class="panel panel-primary">
<div class="panel-body">
<p>Bleh</p>
</div>
</div>
</div>
</div>
</div>
""" % (pic, details, n + 1) 


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
						<span class="icon-bar></span>
						<span class="icon-bar></span>	
						<span class="icon-bar></span>
					</button>
					<a class="navbar-brand" href="#">Bitter</a>
				</div>

				<div id="navbar" class="collapse navbar-collapse">
					<ul class="nav navbar-nav">
						<li class="active"><a href="#">Home<span class="sr-only">(current)</span></a></li>
						<li><a href="#">New Bleat</a></li>
					</ul>
					<form class="navbar-form navbar-left" role="search">
						<div class="form-group">
							<input type="text" class="form-control" placeholder="Search">
						</div>
						<button type="submit" class="btn btn-default">
							<span class="glyphicon glyphicon-search" aria-hidden="true"</span>
						</button>
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
