#!/usr/bin/perl -w

# written by andrewt@cse.unsw.edu.au September 2015
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/bitter/

use CGI qw/:all/;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;

sub main() {
	# print start of HTML ASAP to assist debugging if there is an error in the script
	print page_header();
	
	# Now tell CGI::Carp to embed any warning in HTML
	warningsToBrowser(1);
	
	# define some global variables
	$debug = 1;
	$dataset_size = "medium"; 
	$users_dir = "dataset-$dataset_size/users";
	
	print user_page();
	print page_trailer();
}


#
# Show unformatted details for user "n".
# Increment parameter n and store it as a hidden variable
#
sub user_page {
    my $n = param('n') || 0;
    my @users = sort(glob("$users_dir/*"));
    my $user_to_show  = $users[$n % @users];
    my $details_filename = "$user_to_show/details.txt";
    open my $p, "$details_filename" or die "can not open $details_filename: $!";
    $details = join '', <$p>;
    close $p;
    param('n', $n + 1);
    return div({-class => "bitter_user_details"}, "\n$details\n"), "\n",
        '<p>'.
        start_form, "\n",
        hidden('n'), "\n",
        submit({-class => "bitter_button", -value => 'Next user'}), "\n",
        end_form, "\n";
}


#
# HTML placed at the top of every page
#
sub page_header {
    return header,
        start_html(-title => 'Bitter', -style => "bitter.css"),
        div({-class => "bitter_heading"}, "Bitter");
}


#
# HTML placed at the bottom of every page
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
    my $html = "";
    $html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
    $html .= end_html;
    return $html;
}

main();

