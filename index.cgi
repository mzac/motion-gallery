#!/usr/bin/perl -w

use DateTime;
use Date::Simple;
use DBI;
use Env;
use strict;

# Database settings
my $DB_DRIVER		= 'mysql';
my $DB_SERVER		= '127.0.0.1';
my $DB_PORT		= '3306';
my $DB_DATABASE		= 'motion';
my $DB_USER		= 'motion';
my $DB_PASSWORD		= 'motion';

# Web Server Settings
my $HTTP_SERVER		= 'http://192.168.0.4';

# Web Interface Settings
my $gallery_columns	= '3';
my $gallery_pixel	= '300';
my $gallery_cam1	= '/webcam/rcam1';
my $lastsnap		= '/webcam/rcam1/lastsnap.jpg';
my $live_url		= '/live';

# Set timezone - See http://search.cpan.org/dist/DateTime-TimeZone/ for a list
my $timezone		= 'America/Montreal';

# DON'T CHANGE ANYTHING BELOW THIS LINE
# -------------------------------------

# Database Connection
my $dsn			= "dbi:$DB_DRIVER:$DB_DATABASE";
my $dbh			= DBI->connect($dsn, $DB_USER, $DB_PASSWORD);

# Calculate today's date
my $dt 			= DateTime->now->set_time_zone( $timezone );
my $ymd         	= $dt->ymd;
my $today_date		= $dt->ymd;

&main_frame();

sub main_frame {

	my $camera;
	my $year;
	my $month;
	my $day;

	# Query Database
	my $search_a	= $dbh->prepare("
				SELECT * FROM (
					SELECT
						camera,
						filename,
						event_time_stamp
					FROM security
					WHERE file_type LIKE '1'
					ORDER BY event_time_stamp DESC LIMIT 8
				) SUB ORDER BY event_time_stamp ASC
			");		

	my $camera_number;
	my $camera_filename;
	my $camera_event_time_stamp;

	$search_a->execute() or die "Could not execute SQL query";
	$search_a->bind_columns(
                undef,
                \$camera_number,
                \$camera_filename,
                \$camera_event_time_stamp
	);

	&print_html_header();

        print "<BODY>\n";

        my $rows = $search_a->rows;
        if (!$rows) {
		print "<CENTER>\n";
		print "\t<H2>\n";
                print "\t\tNo captures found!\n";
		print "\t</H2>\n";
		print "</CENTER>\n";
        } else {

		my $column_number = 0;

		print "<TABLE>\n";

		while ($search_a->fetch()){

			my @camera_filename;
			my $jpeg_filename;

			@camera_filename = split('/', $camera_filename);
			$jpeg_filename = "$camera_filename[-1]";

		        # Query Database for Movie File
	        	my $search_b	= $dbh->prepare("
						SELECT
							filename
						FROM security
						WHERE (
							event_time_stamp LIKE '$camera_event_time_stamp'
							AND
							file_type LIKE '8'
						)
	                	        ");

			my @movie_filename;
			my $movie_filename;
			my $image_date;

			$search_b->execute() or die "Could not execute SQL query";
			@movie_filename = $search_b->fetchrow_array();

			@movie_filename = split('/', $movie_filename[0]);
			$movie_filename = "$movie_filename[-1]";
			$image_date = "$movie_filename[-2]";

			if ($column_number == 0) {
				print "\t<TR>\n";
			}

			print "\t\t<TD>\n";
			&html_popup($jpeg_filename,$image_date);
                        print "\t\t\t<IMG SRC=\"$HTTP_SERVER$gallery_cam1/$image_date/$jpeg_filename\" width=$gallery_pixel>\n";
			print "\t\t</A>\n";
			print "\t\t<BR>\n";
			&html_popup($movie_filename,$image_date);
			print "\t\t\t<CENTER>\n";
			print "\t\t\t\tMovie - $camera_event_time_stamp\n";
			print "\t\t\t</CENTER>\n";
			print "\t\t</A>\n";
			print "\t\t</TD>\n";

			$column_number = $column_number + 1;

			if ($column_number == $gallery_columns) {
				print "\t</TR>\n";
				$column_number = 0;
			}
		}
	print "<TD>\n";
	&html_popup_lastsnap($lastsnap);
	print "\t\t\t<IMG SRC=\"$HTTP_SERVER$lastsnap\" width=$gallery_pixel>\n";
	print "\t\t\t<CENTER>\n";
	print "\t\t\tLast Snap\n";
        print "\t\t</A>\n";
	print "</TABLE>\n";
	print "<CENTER>\n";
	print "Refreshing in <span id=\"countdown\">30</span> seconds - ";
	&html_popup_live($live_url);
	print "Live Stream\n";
	print "</A>\n";
	}
        print "</BODY>\n";
	&print_html_footer();
}

sub print_html_header{
        print "Content-type: text/html\n\n";
	print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Frameset//EN\" \"http://www.w3.org/TR/html4/frameset.dtd\">\n";
        print "<HTML>\n";
	print "<HEAD>\n";
        print "\t<META HTTP-EQUIV=\"Content-Type\" CONTENT=\"text/html;charset=utf-8\">\n";
        print "\t<TITLE>Motion Gallery</TITLE>\n";
        print "\t<META NAME=\"robots\" CONTENT=\"noindex, nofollow\">\n";
        print "\t<LINK REL=\"shortcut icon\" TYPE=\"image/x-icon\" HREF=\"images/favicon.ico\">\n";
	print "\t<META HTTP-EQUIV=\"refresh\" CONTENT=\"30\">\n";
	&java_timer;
        print "</HEAD>\n\n";
}

sub print_html_footer{
        print "</HTML>\n";
}

sub print_html_env{
	print "<BR>\n";
        foreach (sort keys %ENV) {
                print "<B>$_</B>: $ENV{$_}<BR>\n";
        }
}

sub html_popup{
	my $filename = $_[0];
	my $image_date = $_[1];
	print "\t\t<A HREF=\"$HTTP_SERVER$gallery_cam1/$image_date/$filename\" TARGET=\"_blank\" ONCLICK=\"window.open('$HTTP_SERVER$gallery_cam1/$image_date/$filename','$filename','resizable=1,width=640,height=480,top=120,left=120'); return false;\">\n";
}

sub html_popup_lastsnap{
	my $filename = $_[0];
	print "\t\t<A HREF=\"$HTTP_SERVER$lastsnap\" TARGET=\"_blank\" ONCLICK=\"window.open('$HTTP_SERVER$lastsnap','Last Snap','resizable=1,width=640,height=480,top=120,left=120'); return false;\">\n";
}

sub html_popup_live{
	my $live_url = $_[0];
	print "\t\t<A HREF=\"$HTTP_SERVER$lastsnap\" TARGET=\"_blank\" ONCLICK=\"window.open('$HTTP_SERVER$live_url','Last Snap','resizable=1,width=640,height=480,top=120,left=120'); return false;\">\n";
}

sub java_timer{
	print "\t<script language=\"javascript\">\n";
	print "\t\tvar max_time = 30;\n";
	print "\t\tvar cinterval;\n";
	print "\t\tfunction countdown_timer(){\n";
	print "\t\t\tmax_time--;\n";
	print "\t\t\tdocument.getElementById('countdown').innerHTML = max_time;\n";
	print "\t\t\tif(max_time == 0){\n";
	print "\t\t\t\tclearInterval(cinterval);\n";
	print "\t\t\t}\n";
	print "\t\t}\n";
	print "\t\tcinterval = setInterval('countdown_timer()', 1000);\n";
	print "\t</script>\n";
}

exit 0;
