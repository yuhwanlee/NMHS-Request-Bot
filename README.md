# NMHS Request Bot

This is a Discord bot written using discord.py, which is an API Wrapper for Discord.

Because of the transition to virtual learning, my school's National Math Honor Society (NMHS) decided to move our tutoring duties to Discord, which requires more organization which can be more easily and efficiently handled by a bot.

If a student needs tutoring, then they create a request, which members of the NMHS can accept. All members should be able to see any requests that need to be accepted by a tutor, any requests that have already been accepted by a tutor, and specific information about a specific request.

## New Requests
New requests can be added to the bot's storage by either submitting an entry into a Google Form, or manually inputting the data using the *!makerequest* command.
This is done by implementing a webhook in a Discord server, which Google Forms will send a message to every time a new form is submitted.

Once the Discord bot receives the message from Google Forms, it parses the message for the data regarding the new request, gives the request a unique ID, and stores the new data.

## Storage
The data that the bot uses (information about all of the current requests) is stored using Amazon S3. The "correct" copy of the data is stored in an S3 Bucket, and every time the bot needs to do an operation using the data, the bot downloads the files from Amazon S3 and uploads them to S3 after any changes are made.

Information about a specific request is stored in one of two files, one containing all of the "unaccepted" requests and one containing the "accepted" requests, the only difference being that the accepted requests file stores the user ID of the person who accepts the request.

## Commands
### !accept [request ID]
This command allows a user to accept a request that has not already been claimed by someone else.

### !info [request ID]
This command allows a user to get the information (name, grade, subject, time, etc.) about a specific request.

### !myrequests
This command allows a user to see all of the requests that they have accepted.

### !list
This command lists all of the requests that are currently in storage (both unaccepted and accepted requests).

### !makerequest
This command allows an admin user to manually create a request.

### !unaccept [request ID]
This command allows an admin user to unaccept a request that they may have accidentally accepted.

### !remove [request ID]
This command allows an admin user to completely remove a request from storage.
