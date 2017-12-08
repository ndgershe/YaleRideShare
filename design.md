The database is set up with a users table, a request table and a history table. When information
about users for emails is needed it can be retrieved by joining the requests and users
tables at userid. The history table and users table do have some shared information which is
redundant but we found this redundancy worth it as oppossed to having to join history and
requests every time the date, type, and airport were needed. Rides stay in history longer than
they stay in rides since they stay in history after they are completed/cancelled. The history
page has an option to clear history which just clears history but keeps rides in requests. This
is another reason why we allowed for some redundancy in the tables. If history had been cleared
requests wouldn't be able to access airport, date, and type.

When a user registers, application.py gets information from register.html and checks
that all of the data is there. For the phone number, it checks that it is a valid 10
digit phone number (handles dashes and spaces) and then formats the number before
it is entered into the data base. We did this formatting here just so the number would
look nicer in emails. This is all in the phonec function as it is also called later in
update2. The password is hashed and the username is made sureto be not taken. If any of
these conditions are not met, an error will occur. After all the information is inserted
into the data base under users, the userid is remembered.

Order is one of the most complex parts of our project. First the order_D_or_A.html gets if the
type of trip (departure or arrival ). We used 0 to represent departure and 1 to represent
arrival since ints use less space than the strings. The type of trip matters since it
determines if we ask for earliest or latest time to be picked up and the algorithm used for matching.
The user is redirected to another order page which gathers the rest of the
the neccessary data for a trip. It returns an error if any of the data is not there.
It checks to make sure that earliest time/ latest time are logical in the function timecheck.
This is a function because it is also called in update2.
Then the ride data is inserted into the database under requests and history. Then a match function is called which searches
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
is edited for arrivals/departures.

Settings shows all of the users current information and allows it to be changed.
change the user's password. The old password is checked for correctness and new password and
verification are checked to ensure that they are the same and then the password is hashed and the user is updated in the database.

For update request the user can pick a ride to update. They are shown all their current information and basically all the functionality
of order is used here. The user can change as little or as much of the request as they like and all the same checks and the searching
algorithm as order are done.

Complete has a link to the uber website so people can request a ride. Complete and cancel are similar in that the user selects a ride
and then the ride is deleted from requests (so it will no longer be available for matching) and its status is updated in history.

There is some java script functionality in that if a required box is left blank an error will pop up on screen.
The html was changed to add a background and change the colors to fit our theme. Font sizes were also done in html.

We decided to deploy our program on heroku so we had to use postgress data tables.