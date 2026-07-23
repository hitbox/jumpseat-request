# WORKFLOW

A flask web app to request a jump seat.

User must login or create an account, verifying their email address which is
used as their username. An authenticated user may submit a jumpseat request.
Requests are emailed to configured email addresses for a decision. The user
receieves an email confirmed their request was taken. Another email notifies
the requester of a decision. A request that is not decided after some
configured amount of time, is elevated and sent to more configured email
addresses.

# TODO

[ ] Scheduled Flights from LSY
[ ] Okta authentication.
[ ] Detect and alert user to enter their employee information.

# QUESTIONS
[?] How to verify employee info? Automatically after an approved request?
[?] Table listings filters.

[X] User created accounts.
[X] Approved/denied emails.
[X] Background service to query and escalate proposals. (tasks.py)
[X] Background service to send email verification codes. (tasks.py)
[X] Test query returns proposals that should be escalated.
[X] Test creating request proposal through flask view.
[X] Service task to send emails from database queue.
