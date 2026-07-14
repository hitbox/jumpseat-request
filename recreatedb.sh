#!/usr/bin/env bash

# strict mode
set -euo pipefail
IFS=$'\n\t'

# recreate database
dropdb jumpseat_request
createdb jumpseat_request
flask admin create-db
flask admin seed-db
flask user create --email "carl.harris@company.com" --password admin --is-admin --is-decider --is-verified
flask employee create --airline ABX --employee-number EECARL --name "CARL HARRIS" --user carl.harris@company.com --phone "111 111 1111"

# Emails from ticket for on-create and escalation:
# https://support.atsginc.com/incidents/182146626-jumpseat-app
flask user create --email "travel@abxair.com" --password 'tr@vel' --is-admin --is-decider --is-verified
flask user create --email "trackers@abxair.com" --password 'tr@ckers' --is-admin --is-decider --is-verified
flask user create --email "abxfc@abxair.com" --password '@bxfc' --is-admin --is-decider --is-verified

# notification rules

# Initial created request notifictions for requester and app admins.
flask notification create --name 'jumpseat-request-created-for-submitter' --blurb "Notify requester their request has been created." --signal-name 'jumpseat-request-created'
# force add email because format string will not exist in users table.
flask notification add-recipient 'jumpseat-request-created-for-submitter' --email-address '{submitter_email}' --force

flask notification create --name 'jumpseat-request-created' --blurb "Notify admins a jump seat request has been created." --signal-name 'jumpseat-request-created'
flask notification add-recipient 'jumpseat-request-created' --email-address 'travel@abxair.com'
flask notification add-recipient 'jumpseat-request-created' --email-address 'trackers@abxair.com'

# Notification for decision on request.
flask notification create --name 'jumpseat-request-decided-for-submitter' --blurb "Notify requester their request has been decided." --signal-name 'jumpseat-request-decided'
flask notification add-recipient 'jumpseat-request-decided-for-submitter' --email-address '{submitter_email}' --force

# Escalation: Notification for request timeout.
ESCALATE_AGE=5
flask notification create --name 'jumpseat-request-escalate' --blurb "Notify of request decision timeout." --signal-name 'jumpseat-request-escalate' --created-age "${ESCALATE_AGE}"
flask notification add-recipient 'jumpseat-request-escalate' --email-address  'abxfc@abxair.com' --force
