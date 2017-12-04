The database is set up with a users table and a request table. When information
about users for emails is needed it can be retrieved by joining the requests and users
tables at userid.

When a user registers, application.py gets information from register.html and checks
that all of the data is there. For the phone number, it checks that it is a valid 10
digit phone number (handles dashes) and then formats the number with dashes before
it is entered into the data base. We did this formatting here just so the number would
look nicer in emails. The password is hashed and the username is made sure
to be not taken. If any of these conditions are not met, an error will occur. After all
the information is inserted into the data base under users, the userid is remembered.

Order is the most complex part of our project. First the order_D_or_A.html gets if the
type of trip (departure or arrival ). We used 0 to represent departure and 1 to represent
arrival since ints use less space than the strings. The type of trip matters since it
determines if we ask for eaarliest or latest time to be picked up and if location is needed.
Depending on the type of trip the user is redirected to another order page which gathers all
the neccessary data for a trip. It returns an error if any of the data is not there.
Then the ride data is inserted into the database under requests. Then a select command searches
for matches in the requests database. It ensures that the user is different, the non time ride
information is all the same and with an OR statement finds time ranges that overlap with the time
range of the user.
If one or more matches are found then an list of all their optimal times is created. Then using this
array another list of the differencce in time between the optimal time of each ride and the users ride is
found. This list and the original list of all the rideids of matches is zipped together so that the rideids
can be sorted by their time difference. This whole procedure allows for the email to be organized by the best match
to the worst match. Then the email is created by getting all the emails names and phones of the matchees to be
inserted into a string messgae. An email with this list is sent to the user. Also an email with the users information
is sent to all of the matchees.

Closest uses a similar method as Order in order to find the closest ride to the user when there are no matches. This
Was created so the user can see if they want to extend their wait time to match with this closest person. First the
user is prompted to select which of their rides they want to find the closest ride to. Then all the information from this
ride is retrieved and put into a search for any rides that match the ride information without specification to time. Then
these rides are ordered in the same way as in Order and the closest match is displayed to the user using a parsed string that
is edited for arrivals/departures. Each variable is called individually because they need to be casted as a dict in order to
get only the value of the object.

Settings simply is a way to change the user's password. The old password is checked for correctness and new password and
verification are checked to ensure that they are the same and then the password is hashed and the user is updated in the database.