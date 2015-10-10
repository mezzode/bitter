#!/usr/bin/python

# written by andrewt@cse.unsw.edu.au September 2015
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/bitter/

import cgi, cgitb, glob, os

def main():
    print page_header()
    cgitb.enable()
    dataset_size = "medium" 
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
    details_filename = os.path.join(user_to_show, "details.txt")
    with open(details_filename) as f:
        details = f.read()
    return """
<div class="bitter_user_details">
%s
</div>
<p>
<form method="POST" action="">
    <input type="hidden" name="n" value="%s">
    <input type="submit" value="Next user" class="bitter_button">
</form>
""" % (details, n + 1) 


#
# HTML placed at the top of every page
#
def page_header():
    return """Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
<title>Bitter</title>
<link href="bitter.css" rel="stylesheet">
</head>
<body>
<div class="bitter_heading">
Bitter
</div>
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
    html += "</body>\n</html>"
    return html

if __name__ == '__main__':
    debug = 1
    main()
