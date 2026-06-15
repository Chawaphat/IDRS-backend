

## Chapter Three | Testing

## 3.1) Unit Test Plan
## 3.1.1) Authentication Module

UTC-01 : Register with Email And Password
Unit Test ID : UTC-01
## Module : Authentication Service
Method Under Test : signUp()
Description : Verifies that a new user can successfully register using valid
information and that the system properly handles duplicate emails, invalid email
formats, and missing required fields.
## Prerequisite Data : None.
## Test Case
ID Description Prerequisites Input Expected Output
## UTC
## -01-
## TC-
## 01
## Success:
Register a
new user
with valid
information
## The
authenticatio
n system
does not
contain a
user with the
email
## "john_doe@
gmail.com".
## {
## “first_name” :
“John” ,
## “last_name” :
“Doe” ,
## “email” :
## “john_doe@gmai
l.com” ,
## “password” :
## “john234”,
## “confirm_passw
ord” :
## “john234”
## }
- Returns a successful
registration response.
- A new user account
is created.
- The response return
user email
## "john_doe@gmail.co
m" and user_id
- Access token and
refresh token are
generated.
- No exception is
raised.


## UTC
## -01-
## TC-
## 02
## Failure:
Attempt to
register
using an
email that
already
exists.
A user
account with
the email
## "john_doe@
gmail.com"
already
exists.
## {
## “first_name” :
“John” ,
## “last_name” :
“Doe” ,
## “email” :
## “john_doe@gmai
l.com” ,
## “password” :
## “john234”,
## “confirm_passw
ord” :
## “john234”
## }
- Registration is
rejected.
- Returns an error
response.
- The response status
code is 409
(Conflict).
- The response
message is "Email
already exists".
- No new user account
is created.
## UTC
## -01-
## TC-
## 03
## Failure:
Attempt to
register
using an
invalid email
format.
## None.
## {
## “email” :
## “john.com”
## }
- Registration is
rejected.
- Returns a validation
error response.
- The response status
code is 400 (Bad
## Request).
- The response
message is "Invalid
email format".
- No user account is
created.
## UTC
## -01-
## TC-
## 04
## Failure:
Attempt to
register with
missing
required
fields.
## None.
## {
## “first_name” :
## “”,
## “last_name” :
## “” ,
## “email” : “” ,
## “password” :
## “john234”
## “confirm_passw
ord” :
## “john234”
## }
- Registration is
rejected.
- Returns a validation
error response.
- The response status
code is 400 (Bad
## Request).
- The response
message is "Missing
required fields".
- No user account is
created.

UTC-02 : Register With Google

Unit Test ID : UTC-02
## Module: Authentication Service
Method Under Test : signUpWithGoogle()
Description : Verifies that a user can successfully authenticate using a valid
Google account.
Prerequisite Data : Valid Google account.
## Test Case
## No. Description Prerequisites Input Expected Output
## UTC-
## 02-
## TC-
## 01
## Success:
Sign in
using a valid
## Google
account.
## The Google
account
exists and is
successfully
authenticated
by Google
OAuth.
## Google Account

- Returns a successful
authentication
response.
- Access token and
refresh token are
generated.
- Returns a valid user
object.
- The user's email
matches the
authenticated Google
account.
- No exception is
raised.

## UTC-
## 02-
## TC-
## 02
## Failure:
User cancels
## Google
authentic
cation
Google sign-
in page is
displayed.
User clicks
"Cancel" during
## Google
authentication.
- Authentication is
cancelled.
- No user session is
created.
- No access token is
generated.
- An authentication
error response is
returned.
UTC-03 : Login With Email And Password
Unit Test ID : UTC-03

## Module : Authentication Service
Method Under Test : signInWithPassword()
Description : Verifies that a registered user can successfully log in using a valid
email address and password and that invalid credentials are properly handled.
Prerequisite Data : Registered user account.
## Test Case
## No. Description Prerequisites Input Expected Output
## UTC-
## 03-
## TC-
## 01
## Success:
Login with a
valid email
and
password.
A user
account
exists with
the email
## "john_doe@
gmail.com"
and
password
## "john1234".
## {
## "email":
## "john_doe@gmai
l.com",
## "password":
## "john1234"
## }
- Returns a successful
authentication
response.
- Access token and
refresh token are
generated.
- Returns a valid user
object.
- The returned user's
email is
## "john_doe@gmail.co
m".
- No exception is
raised.

## UTC-
## 03-
## TC-
## 02
## Failure:
Attempt to
log in with a
non-existent
email
address.
No user
account
exists with
the email
## "john@gmai
l.com".
## {
## “email” :
## “john@gmail.co
m” ,
## “password” :
## “john1234”
## }
- Login is rejected.
- Returns an
authentication error
response.
- The response status
code is 401
(Unauthorized).
- The response
message is "Invalid
email or password".
- No access token is
generated.


## UTC-
## 03-
## TC-
## 03
## Failure:
Attempt to
log in with
an incorrect
password.
A user
account
exists with
the email
## "john_doe@
gmail.com".
## {
## “email” :
## “john_doe@gmai
l.com”,
## “password” :
## “wrongpassword
## ”
## }
- Login is rejected.
- Returns an
authentication error
response.
- The response status
code is 401
(Unauthorized).
- The response
message is "Invalid
email or password".
- No access token is
generated.
## UTC-
## 03-
## TC-
## 04
## Failure:
Attempt to
log in with
empty email
and
password
fields.
## None.
## {
## “email” : “”
## “password” :
## “”
## }
- Login is rejected.
- Returns a validation
error response.
- The response status
code is 400 (Bad
## Request).
- The response
message is "Missing
email or password".
- No authentication
attempt is
performed.





UTC-04 : Login With Google
Unit Test ID : UTC-04
## Moduel : Authentication Service
Method Under Test : signInWithGoogle()

Description : Verifies that the system properly handles Google login
authentication.
Prerequisite Data: Google OAuth service is available.
## Test Case
## No. Description Prerequisite Input Expected Output
## UTC-
## 04-
## TC-
## 01
## Success:
Login using a
valid Google
account.
## The Google
account
exists and
has
previously
authorized
the
application.
## Google Account

- Returns a successful
authentication
response.
- Access token and
refresh token are
generated.
- Returns a valid user
object.
- The user's email
matches the
authenticated
Google account.
- No exception is
raised.
## UTC-
## 04-
## TC-
## 02
## Failure:
## Google
authentication
is cancelled
by the user.
Google sign-
in page is
displayed.
User cancels the
Google sign-in
process.
- Authentication is
cancelled.
- No user session is
created.
- No access token is
generated.
- An authentication
error message is
returned.

## 3.1.2) Patient Module

UTC-05 : Create New Dental Chart
Unit Test ID : UTC-05
## Module : Patient Service

Method Under Test : create_patient(session, payload,dentist_id)
Description : Verifies that a dentist can successfully create a new patient record
and that invalid patient information is properly rejected.
Prerequisite Data: Valid authentication token.
## Test Case
## No. Description Prerequisite Input Expected Output
## UTC-
## 05-
## TC-
## 01
## Success:
Create a
patient with
valid
information.
The HN
number
## "HN001"
does not
already exist
in the
database.
## {
## “hn_number”:
## "HN001",
## “name”:
"john doe",
## “sex”:
## "male",
## “age”: 32,
## “phone” :
## “09032332”
## }

- Returns a Patient
object schema.
## {
## "id": "53a84328-
## 8ff5-4eb1-b716-
## 2afa7211bd6e",
## "hn_number":
## "HN001",
"name": "John Doe",
## "sex": "male",
## "age": 32,
## "phone": "09032332"
## }
- A new patient record
is created in the
database.
- The patient is
associated with the
authenticated dentist.
- No exception is
raised.
## UTC-
## 05-
## TC-
## 02
## Failure:
Create a
patient with
missing
required
fields.
## None.
## {
## “hn_number”:
## "HN001",
## “name”: “”,
## “sex”: “”,
## “age”: 32,
## “phone” : “”
## }
## Authorization:
## Bearer
- Patient creation is
rejected.
- Returns a validation
error response.
- The response status
code is 422
(Unprocessable
## Entity).
- Required field
validation fails.

- No patient record is
created in the
database.















UTC-06 : View Patient List
Unit Test ID: UTC-06
## Module: Patient Service
Method Under Test: get_all_patients(session, dentist_id)

Description: Verifies that a dentist can view all patients assigned to their account
and handles cases where no patient records exist.
Prerequisite Data:Valid authentication token.
## Test Cases
## No. Description Prerequisite Input Expected Output
## UTC-
## 06-
## TC-
## 01
## Success:
View patient
list
successfully.
## The
authenticated
dentist has
patient
records
assigned to
their account.
dentist_id =
## "036f8d6a-
## 483d-4c03-
## 9438-
a501ec78291a
## "
- Returns a list of
patient records.
- Each patient record
contains patient
information.
- Only patients
belonging to the
authenticated
dentist are returned.
- No exception is
raised.
## [
## {
## "patient_id":
## "3fb0f7b1-da69-
## 4793-a7c7-
a6f441dd2f23",
## "hn_number":
## "HN001",
"name": "John Doe",
"status": "Active"
## },
## {
## "patient_id":
## "53a84328-8ff5-
## 4eb1-b716-
## 2afa7211bd6e",
## "hn_number":
## "HN002",
"name": "Kitty",
"status": "Active"
## }
## ]

## UTC-
## 06-
## TC-
## 02
## Failure:
Attempt to
view patient
list without
authentication.
## No
authentication
token is
provided.
## No Bearer
## Token
- Access is denied.
- Returns an
authentication error
response.
- The response status
code is 401
(Unauthorized).
- No patient data is
returned.
## UTC-
## 06-
## TC-
## 03
## Success:
View patient
list when no
patient records
exist.
## The
authenticated
dentist has no
patient
records
assigned.
dentist_id =
## "036f8d6a-
## 483d-4c03-
## 9438-
a501ec78291a
## "
- Returns an empty
list [].
- No exception is
raised.








UTC-07 : View Patient Details
Unit Test ID: UTC-07
## Module: Patient Service
Method Under Test: get_patient_by_id(session, patient_id, dentist_id)
Description: Verifies that a dentist can view patient details and that appropriate
errors are returned when the patient does not exist or authentication is missing.
Prerequisite Data: Valid authentication token .
## Test Cases

## No. Description Prerequisite Input Expected Output
## UTC-
## 07-
## TC-
## 01
## Success:
View existing
patient details.
The specified
patient record
exists and
belongs to the
authenticated
dentist.
patient_id =
## "3fb0f7b1-
da69-4793-
a7c7-
a6f441dd2f23"
## ,
dentist_id =
## "036f8d6a-
## 483d-4c03-
## 9438-
a501ec78291a
## "
- Returns the
patient's details.
- The returned
patient ID matches
the requested
patient ID.
- The returned
patient belongs to
the authenticated
dentist.
- No exception is
raised.
## {
## "patient_id":
## "3fb0f7b1-da69-
## 4793-a7c7-
a6f441dd2f23",
"name": "John Doe",
"sex": "Male",
## "age": 32,
## "phone": "09032332"
## }

## UTC-
## 07-
## TC-
## 02
## Failure:
Attempt to
view patient
details without
authentication.
## No
authentication
token is
provided.
## No Bearer
## Token
- Access is denied.
- Returns an
authentication error
response.
- The response status
code is 401
(Unauthorized).
- No patient record is
returned.
## UTC-
## 07-
## TC-
## 03
## Failure:
Attempt to
view a non-
existent
patient.
No patient
record exists
with the
specified
patient ID.
patient_id =
## "99999999-
## 9999-9999-
## 9999-
## 999999999999"
- Returns an error
response.
- The response status
code is 404 (Not
## Found).
- The response
message is "Patient
not found".

- No patient record is
returned.












UTC-08 : Update Patient Information
Unit Test ID: UTC-08
## Module: Patient Service
Method Under Test: update_patient(session, patient_id, payload, dentist_id)
Description: Verifies that a dentist can successfully update patient information and
that invalid or unauthorized update attempts are properly rejected.
Prerequisite Data: Valid authentication token.
## Test Case

## No. Description Prerequisite Input Expected Output
## UTC-
## 08-
## TC-
## 01
## Success:
Update patient
information
successfully.
## - Valid
authentication
token is
provided.
- Patient with
ID "3fb0f7b1-
da69-4793-
a7c7-
a6f441dd2f23"
exists in the
database.
patient_id =
## "3fb0f7b1-
da69-4793-
a7c7-
a6f441dd2f23"
## {   "name":
## "george
russell" }
- Returns the
updated Patient
object: {
## "patient_id":
## "3fb0f7b1-...",
"name": "George
## Russell”,  "sex":
## "male",   "age":
## 32,   "phone":
## "09032332",
## "dentist_id":
## "036f8d6a-..." }
- Patient record is
updated in the
database.
- No exception is
raised.
## UTC-
## 08-
## TC-
## 02
## Failure:
Attempt to
update patient
without
authentication.
## No
authentication
token is
provided.
## No Bearer
## Token
- Access is denied.
- Returns an
authentication
error response.
- The response
status code is
401(Unauthorized.
## { "message":
"Unauthorized" }
## UTC-
## 08-
## TC-
## 03
## Failure:
Attempt to
update a non-
existent
patient.
No patient
with the given
ID exists in
the database.
patient_id =
## "99999999-
## 9999-9999-
## 9999-
## 999999999999"
- Update is rejected.
- The response
status code is
404(Not found).
## { "message":
"Patient not
found" }

## UTC-
## 08-
## TC-
## 04
## Failure:
Update patient
with invalid
data type.
Patient with
ID "3fb0f7b1-
da69-4793-
a7c7-
a6f441dd2f23"
exists in the
database.
patient_id =
## "3fb0f7b1-
da69-4793-
a7c7-
a6f441dd2f23"
## {   "age":
"george russell"
## }
- Patient update is
rejected.
- Returns a
validation error
response.
- The response
status code is 422
(Unprocessable
## Entity). {
## "message":
"Invalid input
data" }
- No patient record
is modified in the
database.














UTC-09 : Delete Patient
Unit Test ID: UTC-09

## Module: Patient Service
Method Under Test: delete_patient(session, patient_id, dentist_id)
Description: Verifies that a dentist can successfully delete a patient record and that
unauthorized or invalid delete attempts are properly rejected.
Prerequisite Data: Valid authentication token .
## Test Case
## No. Description Prerequisite Input Expected Output
## UTC-
## 09-
## TC-
## 01
## Success:
Delete an
existing
patient record.
## - Valid
authentication
token is
provided.
- Patient with
ID "3fb0f7b1-
da69-4793-
a7c7-
a6f441dd2f23"
exists in the
database.
patient_id =
## "3fb0f7b1-
da69-4793-
a7c7-
a6f441dd2f23"
- Patient record is
deleted from the
database. {
## "message":
"Patient deleted
successfully" }
- No exception is
raised.

## UTC-
## 09-
## TC-
## 02
## Failure:
Attempt to
delete patient
without
authentication.
## No
authentication
token is
provided.
## No Bearer
## Token
- Access is denied.
- Returns an
authentication
error response.
- The response
status code is
401(Unauthorized
## { "message":
"Unauthorized" }
## UTC-
## 09-
## TC-
## 03
## Failure:
Attempt to
delete a non-
existent
patient.
No patient
with the given
ID exists in
the database.
patient_id =
## "99999999-
## 9999-9999-
## 9999-
## 999999999999"
- Delete is rejected.
- The response
status code is
404(Not found).
## { "message":
"Patient not
found" }







UTC-10 : Search Patient
Unit Test ID: UTC-10
## Module: Patient Service
Method Under Test: search_patients(session, query, dentist_id)
Description: Verifies that a dentist can search for patients by name or HN number
and that searches with no matching results return an empty list.
Prerequisite Data: Valid authentication token.
## Test Case
## No. Description Prerequisite Input Expected Output
## UTC-
## 10-
## TC-
## 01
## Success:
## Search
patient by
first name.
## - Valid
authentication
token is
provided.
-Patient
named john
doe" exists in
the database.
keyword =
## "john"
- 1. Returns a list with
matching patient record(s):
## 2. [
## 3. {"patient_id":
## "3fb0f7b1-...",
"hn_number": "HN001",
- "name": "John Doe",
## "sex": "male",
## "age": 32,
## 5. "phone":"09032332",
## "dentist_id": "036f8d6a-
## ..."   } ]
- 2. No exception is raised.


## UTC-
## 10-
## TC-
## 02
## Success:
## Search
patient by
HN number.
## - Valid
authentication
token is
provided.
- Patient with
HN number
## “ HN001"
exists in the
database.
keyword =
## "HN001"
- 1. Returns a list with
matching patient record(s):
## 8. [
## 9. {"patient_id":
## "3fb0f7b1-...",
"hn_number": "HN001",
- "name": "John Doe",
## "sex": "male",
## "age": 32,
## 11. "phone":"09032332",
## "dentist_id": "036f8d6a-
## ..."   } ]
- No exception is raised.
## UTC-
## 10-
## TC-
## 03
## Success:
## Search
patient with
no matching
result.
No patient
matching
keyword
“XYZ” exists
in the
database.
keyword =
## "XYZ"
- Returns an empty list: []
- No exception is raised.




UTC-11 : View Patient Dental Charts
Unit Test ID: UTC-11
## Module: Patient Service
Method Under Test: get_patient_dental_charts(session, patient_id)
Description: Verifies that a dentist can view all dental charts belonging to a
selected patient and that invalid or unauthorized access attempts are properly
rejected.
Prerequisite Data: Valid authentication token .
## Test Case

## No. Description Prerequisite Input Expected Output
## UTC-
## 11-
## TC-
## 01
## Success:
View all
dental charts
belonging to a
patient.
## - Valid
authentication
token is
provided.
- Patient with
ID "3fb0f7b1-
da69-4793-
a7c7-
a6f441dd2f23"
exists and has
dental chart
records.
patient_id =
## "3fb0f7b1-
da69-4793-
a7c7-
a6f441dd2f23"
- 1. Returns a list of
dental chart records:
## 2. [{
## 3. "chart_id":
## "cee82218-7eb5-
## 43be-b947-
## 7144bbfb47d7",
## "record_date":
## "2026-06-09",
## "dentist_id":
## "036f8d6a-..."
## },   {
## "chart_id":
## "62326311-bac9-
## 48b5-958d-
## 0ee0831d7a50",
## "record_date":
## "2026-06-10" } ]
- 2. Only charts
belonging to the
specified patient are
returned.
- 3. No exception is
raised.
## UTC-
## 11-
## TC-
## 02
## Success:
View dental
charts when
no charts exist
for the patient.
Patient with
ID "3fb0f7b1-
da69-4793-
a7c7-
a6f441dd2f23"
exists but has
no dental chart
records.
patient_id =
## "3fb0f7b1-
da69-4793-
a7c7-
a6f441dd2f23"
- Returns an empty
list: []
- No exception is
raised.
## UTC-
## 11-
## TC-
## 03
## Failure:
Attempt to
view dental
charts for a
non-existent
patient.
No patient
with the given
ID exists in
the database.
patient_id =
## "999"
- Request is rejected.
- The response status
code is 404 (Not
## Found). {
## "message":
"Patient not
found" }

## UTC-
## 11-
## TC-
## 04
## Failure:
Attempt to
view dental
charts without
authentication.
## No
authentication
token is
provided.
## No Bearer
## Token
- Access is denied.
- Returns an
authentication error
response.
- The response status
code is 401
(Unauthorized). {
## "message":
"Unauthorized" }







## 3.1.3) Dental Chart Module

UTC-12 : Create New Dental Chart
Unit Test ID: UTC-12
## Module: Dental Chart Service
Method Under Test: create_dental_chart(session, payload)
Description: Verifies that a dentist can successfully create a new dental chart for
an existing patient and that invalid or unauthorized creation attempts are properly
rejected.
Prerequisite Data: Valid authentication token. Existing patient record and dentist
account.
## Test Case
## No.  Description Prerequisite Input Expected Output

## UTC-
## 12-
## TC-
## 01
## Success:
Create a
dental chart
with valid
information.
## - Valid
authentication
token is
provided.
## - Patient
## "53a84328-
## 8ff5-4eb1-
b716-
## 2afa7211bd6e"
and dentist
## "ff6ecd52-
d252-4da0-
aa21-
## 339c008178c7"
exist in the
database.
## {

## "patient_id":
## "53a84328-
## 8ff5-4eb1-
b716-
## 2afa7211bd6e",

## "dentist_id":
## "ff6ecd52-
d252-4da0-
aa21-
## 339c008178c7"
## }
- Returns a Dental
Chart object:
## {
## "chart_id":
## "d8454cab-1a71-
## 46e8-8ac1-
## 69ebae557d5a",
## "patient_id":
## "53a84328-8ff5-
## 4eb1-b716-
## 2afa7211bd6e",
## "dentist_id":
## "036f8d6a-483d-
## 4c03-9438-
a501ec78291a",
## "record_date":
## "2026-04-25"
## }
- A new dental
chart record is
created in the
database.
- No exception is
raised.
## UTC-
## 12-
## TC-
## 02
## Failure:
Create a
dental chart
with a non-
existent
patient ID.
No patient with
the given
patient_id
exists in the
database.
## {
## "patient_id":
## "999999",

## "dentist_id":
## "ff6ecd52-
d252-4da0-
aa21-
## 339c008178c7"
## }
- Chart creation is
rejected.
- The response
status code is 404
(Not Found).
## { "message":
"Patient not
found" }
## UTC-
## 12-
## TC-
## 03
## Failure:
Create a
dental chart
with a non-
existent
dentist ID.
No dentist with
the given
dentist_id
exists in the
database.
## {
## "patient_id":
## "53a84328-
## 8ff5-4eb1-
b716-
## 2afa7211bd6e",

## "dentist_id":
## "999999"
## }
- Chart creation is
rejected.
- The response
status code is 404
(Not Found).
## { "message":
"Dentist not
found" }
## UTC-
## 12-
## TC-
## 04
## Failure:
Create a
dental chart
with missing
## None.
## {
## "patient_id":
## "",
## "dentist_id":
- Chart creation is
rejected.
- Returns a
validation error

required
fields.
## ""
## }
response.
- The response
status code is 422
(Unprocessable
## Entity).
## { "message":
"Missing required
fields" }
- No dental chart
record is created in
the database.
## UTC-
## 12-
## TC-
## 05
## Failure:
Create a
dental chart
without
authentication.
## No
authentication
token is
provided.
## No Bearer
## Token
- Access is denied.
- Returns an
authentication error
response.
- The response
status code is 401
(Unauthorized).
## { "message":
"Unauthorized" }
UTC-13 : Delete Dental Chart
Unit Test ID: UTC-13
## Module: Dental Chart Service
Method Under Test: delete_dental_chart(session, chart_id)
Description: Verifies that a dentist can successfully delete an existing dental chart
and that invalid deletion attempts are properly rejected.
Prerequisite Data: Valid authentication token and existing dental chart record.
## Test Case
## No. Description Prerequisite Input Expected Output
## UTC-
## 13-
## TC-
## 01
## Success:
Delete an
existing
dental chart.
## - Valid
authentication
token is
provided.
- Dental chart
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## { "chart_id":
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d5a"
## }
- Dental chart record
is deleted from the
database.
## { "message":
"Dental chart
deleted
successfully" }
- No exception is
raised.

## 69ebae557d5a"
exists in the
database.
## UTC-
## 13-
## TC-
## 02
## Failure:
Delete a
non-existent
dental chart.
No dental chart
with the given
chart_id exists
in the database.
## { "chart_id":
## "9999" }
- Delete is rejected.
- The response status
code is 404 (Not
## Found).
## { "message":
"Dental chart not
found" }
## UTC-
## 13-
## TC-
## 03
## Failure:
Delete a
dental chart
with an
invalid chart
ID format.
## Valid
authentication
token is
provided.
## { "chart_id":
## "" }
- Delete is rejected.
- Returns a
validation error
response.
- The response status
code is 422
(Unprocessable
## Entity).
## { "message":
"Invalid chart ID"
## }

## 3.1.4) Medical History Module

UTC-14: Create Medical History
Unit Test ID: UTC-14
## Module: Medical History Service
Method Under Test: create_medical_history(session, chart_id, payload)
Description: Verifies that a dentist can successfully create a new medical history
record for an existing dental chart and that invalid or unauthorized creation
attempts are properly rejected.
Prerequisite Data: Valid authentication token, existing chart ID and medical
history information.
## Test Case

## No. Description Prerequisite Input Expected
## Output
## UTC
## -14-
## TC-
## 01
## Success:
## Create
medical
history with
valid
information.
## - Valid
authenticatio
n token is
provided.
## - Dental
chart
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d5
a" exists in
the database.
## {
## "chart_id": "d8454cab-
## 1a71-46e8-8ac1-
## 69ebae557d5a",
## "chief_complaint":
"Tooth pain on upper
right molar",
## "present_illness":
"Pain started 3 days
ago, worse when
chewing",
"medical_history": "No
significant medical
history",

## "regular_doctor_visits":
true,
## "current_medication":
## "paracetamol",
## "allergy_status":
## "no",
## "allergy_detail":
null,
## "dental_history":
"Previous filling on
tooth 18",
## "patient_expectation":
## ["chewing", "esthetic"],
## "patient_expectation_oth
er": null,

## "patient_self_evaluation
": "Pain level 7/10",

## "patient_expected_outcom
e": "Relief from pain
and normal chewing
function"
## }
- Returns a
## Medical
## History
object:
## {
## "history_id"
## : "2f6e8f12-
f746-4d07-
## 8a2b-
## 225746f67167
## ",
## "chart_id":
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d5a
## "
## }
- A new
medical
history record
is created in
the database.
## 3. No
exception is
raised.
## UTC
## -14-
## TC-
## 02
## Failure:
## Create
medical
history with
a non-
existent
chart ID.
No dental
chart with
the given
chart_id
exists in the
database.
## {
## "chart_id": "9999",
## "chief_complaint":
"Tooth pain on upper
right molar",
## "present_illness":
"Pain started 3 days
ago, worse when
chewing",
"medical_history": "No
## 1. Medical
history
creation is
rejected.
## 2. The
response
status code is

significant medical
history",

## "regular_doctor_visits":
true,
## "current_medication":
## "paracetamol",
## "allergy_status":
## "no",
## "allergy_detail":
null,
## "dental_history":
"Previous filling on
tooth 18",
## "patient_expectation":
## ["chewing", "esthetic"],

## "patient_expectation_oth
er": null,

## "patient_self_evaluation
": "Pain level 7/10",

## "patient_expected_outcom
e": "Relief from pain
and normal chewing
function"
## }
404 (Not
## Found).
## { "message":
"Chart not
found" }
## UTC
## -14-
## TC-
## 03
## Failure:
## Create
medical
history with
missing
required
fields.
## Valid
authenticatio
n token is
provided.
Dental chart
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d5
a" exists in
the database.
## {
## "chart_id": "d8454cab-
## 1a71-46e8-8ac1-
## 69ebae557d5a",
## "chief_complaint": "",
## "present_illness": "",
## "medical_history": "",

## "regular_doctor_visits":
true,
## "current_medication":
## "",
## "allergy_status":
## "no",
## "allergy_detail":
null,
## "dental_history":
"Previous filling on
tooth 18",
## "patient_expectation":
## ["chewing", "esthetic"],

## "patient_expectation_oth
## 1. Medical
history
creation is
rejected.
- Returns a
validation
error
response.
## 3. The
response
status code is
## 422
(Unprocessab
le Entity).
## { "message":
"Missing
required
fields" }
- No medical

er": null,

## "patient_self_evaluation
": "Pain level 7/10",

## "patient_expected_outcom
e": "Relief from pain
and normal chewing
function"
## }
history record
is created in
the database.
## UTC
## -14-
## TC-
## 04
## Failure:
## Create
medical
history
without
authenticati
on.
## No
authenticatio
n token is
provided.
No Bearer Token 1. Access is
denied.
- Returns an
authentication
error
response.
## 3. The
response
status code is
## 401
(Unauthorize
d).
## { "message":
"Unauthorize
d" }



















UTC-15: View Medical History
Unit Test ID: UTC-15
## Module: Medical History Service
Method Under Test: get_medical_history_by_chart_id(session, chart_id)
Description: Verifies that a dentist can view the medical history belonging to a
selected chart and that invalid access attempts are properly rejected.
Prerequisite Data: Valid authentication token and existing chart ID.
## Test Case
## No. Description Prerequisite Input Expected Output
## UTC
## -15-
## TC-
## 01
## Success:
## View
medical
history for
an existing
chart.
-Valid
authenticati
on token is
provided.
-Dental
chart
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d
5a" exists
with a
medical
history
record.
## {
## "chart_id":
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d5
a" }
- Returns the Medical
History object:
## {
## "history_id":
## "2f6e8f12-f746-4d07-8a2b-
## 225746f67167",
## "chart_id": "d8454cab-
## 1a71-46e8-8ac1-
## 69ebae557d5a",
## "chief_complaint":
"Tooth pain on upper
right molar",
## "present_illness":
"Pain started 3 days ago,
worse when chewing",
"medical_history": "No
significant medical
history",

## "regular_doctor_visits":

true,
## "current_medication":
## "paracetamol",
## "allergy_status": "no",
"allergy_detail": null,
## "dental_history":
"Previous filling on
tooth 16",
## "patient_expectation":
## ["chewing", "esthetic"],

## "patient_expectation_othe
r": null,

## "patient_self_evaluation"
: "Pain level 7/10",

## "patient_expected_outcome
": "Relief from pain and
normal chewing function",
## "created_at": "2026-04-
## 24T21:18:25.485257"
## }
- No exception is raised.
## UTC
## -15-
## TC-
## 02
## Failure:
## View
medical
history for a
non-
existent
chart ID.
No dental
chart with
the given
chart_id
exists in the
database.
## {
## "chart_id":
## "9999" }
- Request is rejected.
- The response status code is
404 (Not Found).
{ "message": "Chart not
found" }
## UTC
## -15-
## TC-
## 03
## Failure:
## View
medical
history with
no chart ID
provided.
## None.
## {
## "chart_id":
## "" }
- Request is rejected.
- Returns a validation error
response.
- The response status code is
422 (Unprocessable Entity).
{ "message": "Missing
chart ID" }










UTC-16: Update Medical History
Unit Test ID: UTC-16
## Module: Medical History Service
Method Under Test: update_medical_history(session, chart_id, payload)
Description: Verifies that a dentist can successfully update an existing medical
history record and that invalid update attempts are properly rejected.
Prerequisite Data: Valid authentication token, existing chart ID and medical
history information.
## Test Case
## No. Descripti
on
## Prerequisite Input Expected Output
## UT
## C-
## 16-
## TC-
## 01
## Success:
## Update
medical
history
with valid
informati
on.
## Valid
authenticati
on token is
provided.
Dental chart
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d
5a" exists
with a
medical
history
record.
## {
## "chart_id":
## "d8454cab-1a71-
## 46e8-8ac1-
## 69ebae557d5a",

## "chief_complaint":
"Tooth pain on
upper right molar",

## "present_illness":
"Pain started 3000
days ago, worse
when chewing",

## "medical_history":
"No significant
medical history",

## "regular_doctor_vis
its": true
## }
- Returns the updated
## Medical History
object:
## {
## "chart_id":
## "d8454cab-1a71-
## 46e8-8ac1-
## 69ebae557d5a",
## "history_id":
## "2f6e8f12-f746-
## 4d07-8a2b-
## 225746f67167",

## "chief_complaint":
"Tooth pain on
upper right molar",

## "present_illness":
"Pain started 3000
days ago, worse
when chewing",

## "medical_history":
"No significant

medical history",

## "regular_doctor_vis
its": true,
## "updated_at":
## "2026-04-
## 24T21:18:25.485257"
## }
- Medical history
record is updated in
the database.
- No exception is
raised.
## UT
## C-
## 16-
## TC-
## 02
## Failure:
## Update
medical
history
for a non-
existent
chart ID.
No dental
chart with
the given
chart_id
exists in the
database.
## {
## "chart_id":
## "999999",

## "chief_complaint":
"Tooth pain on
upper right molar",

## "regular_doctor_vis
its": true
## }
- Update is rejected.
- The response status
code is 404 (Not
## Found).
{ "message": "Chart
not found" }















## 3.1.5) Extraoral Exam Module

UTC-17: Create Extraoral Exam
Unit Test ID: UTC-17
## Module: Extraoral Exam Service
Method Under Test: create_extraoral_exam(session, chart_id, payload)
Description: Verifies that a dentist can successfully create an extraoral exam
record for an existing dental chart and that invalid or unauthorized creation
attempts are properly rejected.
Prerequisite Data: Valid authentication token, existing chart ID and extraoral
exam information.
## Test Case
## No. Description Prerequisite Input Expected
## Output
## UT
## C-
## 17-
## TC-
## 01
## Success:
Create an
extraoral
exam with
valid
information
## .
## Valid
authenticati
on token is
provided.
Dental chart
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d
5a" exists in
the
database.
## {
## "chart_id": "d8454cab-
## 1a71-46e8-8ac1-
## 69ebae557d5a",
## "facial_symmetry":
## "symmetry",
## "facial_profile":
## "straight",
## "muscle_pain": {
## "temporalis": "mild",
## "masseter": "none"
## },
## "joint_pain":
## ["function"],
## "joint_sound":
## "clicking",
## "jaw_deviation":
## "to_left",
## "has_limited_opening":
false,
## "mouth_opening_mm": 42,
## "has_limited_movement":
false,

- Returns an
## Extraoral
Exam object:
## {

## "exam_id":
## "740f02d0-
## 2667-46aa-
b3e7-
## 8488d05e501
## 5",

## "chart_id":
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d5
a"
## }
- A new
extraoral
exam record

## "specify_movement_detail"
: null,
## "parafunctional_habit":
## ["bruxism", "clenching"],

## "parafunctional_habit_oth
er": null,

## "factors_affecting_tooth_
wear": {
"acidic_diet": true,
"dry_mouth": false
## }
## }
is created in
the database.
## 3. No
exception is
raised.
## UT
## C-
## 17-
## TC-
## 02
## Failure:
Create an
extraoral
exam with a
non-
existent
chart ID.
No dental
chart with
the given
chart_id
exists in the
database.
## {
## "chart_id": "999999",
## "facial_symmetry":
## "symmetry",
## "facial_profile":
## "straight",
## "muscle_pain": {
## "temporalis": "mild",
## "masseter": "none" },
## "joint_pain":
## ["function"],
## "joint_sound":
## "clicking",
## "jaw_deviation":
## "to_left",
## "has_limited_opening":
false,
## "mouth_opening_mm": 42,
## "has_limited_movement":
false,

## "specify_movement_detail"
: null,
## "parafunctional_habit":
## ["bruxism", "clenching"],

## "parafunctional_habit_oth
er": null,

## "factors_affecting_tooth_
wear": {
"acidic_diet": true,
"dry_mouth": false
## }
## }

## 1. Exam
creation is
rejected.
## 2. The
response
status code is
404 (Not
## Found).
## {
## "message":
"Chart not
found" }

## UT
## C-
## 17-
## TC-
## 03
## Failure:
Create an
extraoral
exam with
missing
required
fields.
## Valid
authenticati
on token is
provided.
Dental chart
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d
5a" exists in
the
database.
## {
## "chart_id": "d8454cab-
## 1a71-46e8-8ac1-
## 69ebae557d5a",
## "facial_symmetry": "",
## "facial_profile": "",
## "muscle_pain": {
## "temporalis": "",
## "masseter": "" },
## "joint_pain":
## ["function"],
## "joint_sound": "",
## "jaw_deviation":
## "to_left",
## "has_limited_opening":
false,
## "mouth_opening_mm": 42,
## "has_limited_movement":
false,

## "specify_movement_detail"
: null,
## "parafunctional_habit":
## ["bruxism", "clenching"],

## "parafunctional_habit_oth
er": null,

## "factors_affecting_tooth_
wear": {
"acidic_diet": true,
"dry_mouth": false
## }
## }
## 1. Exam
creation is
rejected.
- Returns a
validation
error
response.
## 3. The
response
status code is
## 422
(Unprocessa
ble Entity).
## {
## "message":
"Missing
required
fields" }
## 4. No
extraoral
exam record
is created in
the database.
## UT
## C-
## 17-
## TC-
## 04
## Failure:
Create an
extraoral
exam
without
authenticati
on.
## No
authenticati
on token is
provided.
No Bearer Token 1. Access is
denied.
- Returns an
authenticatio
n error
response.
## 3. The
response
status code is
## 401
(Unauthorize
d).
## {
## "message":

"Unauthoriz
ed" }


UTC-18: View Extraoral Exam
Unit Test ID: UTC-18
## Module: Extraoral Exam Service
Method Under Test: get_extraoral_exam_by_chart_id(session, chart_id)
Description: Verifies that a dentist can view the extraoral exam record belonging
to a selected chart and that invalid access attempts are properly rejected.
Prerequisite Data: Valid authentication token and existing chart ID.
## Test Case
## No. Descripti
on
## Prerequisite Input Expected Output
## UTC
## -18-
## TC-
## 01
## Success:
View an
extraoral
exam for
an
existing
chart.
## Valid
authenticatio
n token is
provided.
Dental chart
## "6ae0746a-
## 511e-4a5d-
## 88c9-
## 975234efc03
a" exists
with an
extraoral
exam record.
## {
## "chart_id":
## "6ae0746a-
## 511e-4a5d-
## 88c9-
## 975234efc03
a" }
- Returns the Extraoral Exam
object:
## {
## "exam_id": "f7e355d5-
## 875d-4e22-a843-
## 6e244f731afb",
## "chart_id": "6ae0746a-
## 511e-4a5d-88c9-
## 975234efc03a",
## "facial_symmetry":
## "symmetry",
## "facial_profile":
## "straight",
## "muscle_pain": {
## "masseter": "none",
## "temporalis": "mild" },
## "joint_pain":
## ["function"],
## "joint_sound":
## "clicking",
## "jaw_deviation":
## "to_left",
## "has_limited_opening":
false,
## "mouth_opening_mm": 42,
## "has_limited_movement":
false,


## "specify_movement_detail":
null,
## "parafunctional_habit":
## ["bruxism", "clenching"],

## "parafunctional_habit_other
": null,

## "factors_affecting_tooth_we
ar": {
"dry_mouth": false,
"acidic_diet": true
## },
"note": null
## }
- No exception is raised.
## UTC
## -18-
## TC-
## 02
## Failure:
View an
extraoral
exam for
a non-
existent
chart ID.
No dental
chart with
the given
chart_id
exists in the
database.
## {
## "chart_id":
## "99999" }
- Request is rejected.
- The response status code is
404 (Not Found).
{ "message": "Chart not
found" }
## UTC
## -18-
## TC-
## 03
## Failure:
View an
extraoral
exam
with no
chart ID
provided.
## Valid
authenticatio
n token is
provided.
## {
## "chart_id":
## "" }
- Request is rejected.
- Returns a validation error
response.
- The response status code is
422 (Unprocessable Entity).
{ "message": "Missing chart
## ID" }





UTC-19: Update Extraoral Exam
Unit Test ID: UTC-19
## Module: Extraoral Exam Service
Method Under Test: update_extraoral_exam(session, chart_id, payload)

Description: Verifies that a dentist can successfully update an existing extraoral
exam record and that invalid update attempts are properly rejected.
Prerequisite Data: Valid authentication token, existing chart ID and extraoral
exam information.
## Test Case :
## No. Description Prerequisite Input Expected Output
## UTC
## -19-
## TC-
## 01
## Success:
Update an
extraoral
exam with
valid
information
## .
## Valid
authentication
token is
provided.
Dental chart
## "6ae0746a-
## 511e-4a5d-
## 88c9-
## 975234efc03a
" exists with
an extraoral
exam record.
## {
## "chart_id":
## "6ae0746a-511e-
## 4a5d-88c9-
## 975234efc03a",

## "joint_sound":
## "popping",

## "jaw_deviation"
## : "to_right"
## }
- Returns the
updated Extraoral
Exam object:
## {
## "chart_id":
## "6ae0746a-511e-
## 4a5d-88c9-
## 975234efc03a",
## "exam_id":
## "f7e355d5-875d-
## 4e22-a843-
## 6e244f731afb",
## "joint_sound":
## "popping",
## "jaw_deviation":
## "to_right",
## "updated_at":
## "2026-04-
## 24T21:18:25.485257
## "
## }
- Extraoral exam
record is updated in
the database.
- No exception is
raised.
## UTC
## -19-
## TC-
## 02
## Failure:
Update an
extraoral
exam for a
non-
existent
chart ID.
No dental
chart with the
given chart_id
exists in the
database.
## {
## "chart_id":
## "99999",

## "joint_sound":
## "popping",

## "jaw_deviation"
## : "to_right"
## }
- Update is rejected.
- The response status
code is 404 (Not
## Found).
## { "message":
"Chart not found"
## }





















## 3.1.6) Esthetic Evaluation Module

UTC-20: Create Esthetic Evaluation
Unit Test ID: UTC-20
## Module: Esthetic Evaluation Service
Method Under Test: create_esthetic_evaluation(session, chart_id, payload)

Description: Verifies that a dentist can successfully create an esthetic evaluation
record for an existing dental chart and that invalid or unauthorized creation
attempts are properly rejected.
Prerequisite Data: Valid authentication token, existing chart ID and esthetic
evaluation information.
## Test Case:
## No. Description Prerequisite Input Expected
## Output
## UTC
## -20-
## TC-
## 01
## Success:
Create an
esthetic
evaluation
with valid
information.
## Valid
authenticatio
n token is
provided.
Dental chart
## "6ae0746a-
## 511e-4a5d-
## 88c9-
## 975234efc03
a" exists in
the database.
## {
## "chart_id":
## "6ae0746a-511e-4a5d-
## 88c9-975234efc03a",
## "occlusal_plane":
## "parallel",

## "midline_discrepancy"
## : "symmetric",
## "lip_thickness":
## "average",
## "lip_length":
## "average",

## "upper_tooth_exposure
## ": 2.5,

## "lower_tooth_exposure
## ": 1.0,
## "midline_shift":
## 0.5,
## "nasolabial_angle":
## "normal",

## "dentofacial_analysis
## ": {
## "profile_note":
"balanced soft
tissue",
## "smile_line":
## "medium"
## },
"fv_sound": true,
## "closest_speaking":
## 1.8,
## "reference_teeth":
## [11, 21]
## }
- Returns an
## Esthetic
## Evaluation
object:
## {

## "esthetic_id"
## : "ac522cf4-
d2db-478a-
b377-
cbed160540de"
## ,
## "chart_id":
## "6ae0746a-
## 511e-4a5d-
## 88c9-
## 975234efc03a"
## }
- A new
esthetic
evaluation
record is
created in the
database.
## 3. No
exception is
raised.

## UTC
## -20-
## TC-
## 02
## Failure:
Create an
esthetic
evaluation
with a non-
existent chart
## ID.
No dental
chart with the
given
chart_id
exists in the
database.
## {
## "chart_id":
## "99999",
## "occlusal_plane":
## "parallel",

## "midline_discrepancy"
## : "symmetric",
## "lip_thickness":
## "average",
## "lip_length":
## "average",

## "upper_tooth_exposure
## ": 2.5,

## "lower_tooth_exposure
## ": 1.0,
## "midline_shift":
## 0.5,
## "nasolabial_angle":
## "normal",

## "dentofacial_analysis
## ": {
## "profile_note":
"balanced soft
tissue",
## "smile_line":
## "medium"
## },
"fv_sound": true,
## "closest_speaking":
## 1.8,
## "reference_teeth":
## [11, 21]
## }
## 1. Evaluation
creation is
rejected.
## 2. The
response status
code is 404
(Not Found).
## { "message":
"Chart not
found" }
## UTC
## -20-
## TC-
## 03
## Failure:
Create an
esthetic
evaluation
with missing
required
fields.
## Valid
authenticatio
n token is
provided.
Dental chart
## "6ae0746a-
## 511e-4a5d-
## 88c9-
## 975234efc03
a" exists in
the database.
## {
## "chart_id":
## "6ae0746a-511e-4a5d-
## 88c9-975234efc03a",
## "occlusal_plane":
## "",

## "midline_discrepancy"
## : "",
## "lip_thickness":
## "",
## "lip_length": "",

## "upper_tooth_exposure
## 1. Evaluation
creation is
rejected.
- Returns a
validation
error response.
## 3. The
response status
code is 422
(Unprocessabl
e Entity).

## ": 2.5,

## "lower_tooth_exposure
## ": 1.0,
## "midline_shift":
## 0.5,
## "nasolabial_angle":
## "",

## "dentofacial_analysis
## ": {
## "profile_note":
"balanced soft
tissue",
## "smile_line":
## "medium"
## },
"fv_sound": true,
## "closest_speaking":
## 1.8,
## "reference_teeth":
## [11, 21]
## }
## { "message":
"Missing
required
fields" }
- No esthetic
evaluation
record is
created in the
database.
## UTC
## -20-
## TC-
## 04
## Failure:
Create an
esthetic
evaluation
without
authenticatio
n.
## No
authenticatio
n token is
provided.
No Bearer Token 1. Access is
denied.
- Returns an
authentication
error response.
## 3. The
response status
code is 401
(Unauthorized)
## .
## { "message":
"Unauthorized
## " }





















UTC-21: View Esthetic Evaluation
Unit Test ID: UTC-21
## Module: Esthetic Evaluation Service
Method Under Test: get_esthetic_evaluation_by_chart_id(session, chart_id)
Description: Verifies that a dentist can view the esthetic evaluation record
belonging to a selected chart and that invalid access attempts are properly rejected.
Prerequisite Data: Valid authentication token and existing chart ID.
## Test Case:
## No. Descriptio
n
## Prerequisite Input Expected Output
## UTC
## -21-
## TC-
## 01
## Success:
View an
esthetic
evaluation
## Valid
authentication
token is
provided.
## {
## "chart_id":
## "6ae0746a-
## 511e-4a5d-
## 88c9-
- Returns the Esthetic
Evaluation object:
## {
## "esthetic_id":
## "ac522cf4-d2db-478a-

for an
existing
chart.
Dental chart
## "6ae0746a-
## 511e-4a5d-
## 88c9-
## 975234efc03a
" exists with
an esthetic
evaluation
record.
## 975234efc03a
## " }
b377-cbed160540de",
## "chart_id":
## "6ae0746a-511e-4a5d-
## 88c9-975234efc03a",
## "occlusal_plane":
## "parallel",

## "midline_discrepancy":
## "symmetric",
## "lip_thickness":
## "average",
## "lip_length":
## "average",

## "upper_tooth_exposure"
## : 2.5,

## "lower_tooth_exposure"
## : 1.0,
## "midline_shift":
## 0.5,
## "nasolabial_angle":
## "normal",

## "dentofacial_analysis"
## : {
## "smile_line":
## "medium",
## "profile_note":
"balanced soft tissue"
## },
"fv_sound": true,
## "closest_speaking":
## 1.8,
## "reference_teeth":
## [11, 21],
"note": null
## }
- No exception is raised.
## UTC
## -21-
## TC-
## 02
## Failure:
View an
esthetic
evaluation
for a non-
existent
chart ID.
No dental
chart with the
given chart_id
exists in the
database.
## {
## "chart_id":
## "99999" }
- Request is rejected.
- The response status
code is 404 (Not Found).
{ "message": "Chart
not found" }
## UTC
## -21-
## Failure:
View an
## Valid
authentication
## {
## "chart_id":
## "" }
- Request is rejected.
- Returns a validation

## TC-
## 03
esthetic
evaluation
with no
chart ID
provided.
token is
provided.
error response.
- The response status
code is 422
(Unprocessable Entity).
{ "message": "Missing
chart ID" }









UTC-22: Update Esthetic Evaluation
Unit Test ID: UTC-22
## Module: Esthetic Evaluation Service
Method Under Test: update_esthetic_evaluation(session, chart_id, payload)
Description: Verifies that a dentist can successfully update an existing esthetic
evaluation record and that invalid update attempts are properly rejected.
Prerequisite Data: Valid authentication token, existing chart ID and esthetic
evaluation information.
## Test Case:
## No. Descriptio
n
## Prerequisite Input Expected Output
## UTC
## -22-
## TC-
## 01
## Success:
Update an
esthetic
evaluation
with valid
## Valid
authenticatio
n token is
provided.
Dental chart
## {
## "chart_id":
## "6ae0746a-511e-
## 4a5d-88c9-
## 975234efc03a",

## "midline_discrepanc
- Returns the
updated Esthetic
Evaluation object:
## {
## "chart_id":
## "6ae0746a-511e-

informatio
n.
## "6ae0746a-
## 511e-4a5d-
## 88c9-
## 975234efc03
a" exists
with an
esthetic
evaluation
record.
y": "right_shift",
## "midline_shift":
## 1.2,
## "fv_sound":
false,

## "closest_speaking":
## 2.1,

## "reference_teeth":
## [12, 22]
## }
## 4a5d-88c9-
## 975234efc03a",
## "esthetic_id":
## "ac522cf4-d2db-
## 478a-b377-
cbed160540de",

## "midline_discrepanc
y": "right_shift",
## "midline_shift":
## 1.2,
## "fv_sound":
false,

## "closest_speaking":
## 2.1,

## "reference_teeth":
## [12, 22],
## "updated_at":
## "2026-04-
## 24T21:18:25.485257"
## }
- Esthetic evaluation
record is updated in
the database.
- No exception is
raised.
## UTC
## -22-
## TC-
## 02
## Failure:
Update an
esthetic
evaluation
for a non-
existent
chart ID.
No dental
chart with
the given
chart_id
exists in the
database.
## {
## "chart_id":
## "99999",

## "midline_discrepanc
y": "right_shift",
## "midline_shift":
## 1.2,
## "fv_sound":
false,

## "closest_speaking":
## 2.1,

## "reference_teeth":
## [12, 22]
## }
- Update is rejected.
- The response status
code is 404 (Not
## Found).
{ "message": "Chart
not found" }














3.1.7) VDO Evaluations Module
UTC-23 : Create VDO Evaluation
Unit Test ID: UTC-23
Module: VDO Evaluation Service
Method Under Test: create_vdo_evaluation(session, chart_id, payload)
Description: Verifies that a dentist can successfully create a VDO (Vertical
Dimension of Occlusion) evaluation record for an existing dental chart and that
invalid or unauthorized creation attempts are properly rejected.
Prerequisite Data: Valid authentication token and existing chart ID.
## Test Case:
## No. Description Prerequisite Input Expected
## Output
## UTC
## -23-
## TC-
## 01
## Success:
Create a
## VDO
evaluation
## Valid
authentication
token is
provided.
Dental chart
## {
## "chart_id":
## "6ae0746a-511e-4a5d-
## 88c9-975234efc03a",

## "facial_soft_tissue"
## :
- Returns a
## VDO
## Evaluation
object:
## {
## "vdo_id":

with valid
information.
## "6ae0746a-
## 511e-4a5d-
## 88c9-
## 975234efc03a
" exists in the
database.
## ["nasolabial_fold",
## "thin_lips"],

## "closest_speaking":
## 2.0,
## "free_way_space":
## 3.0,
## "bite_type":
## "normal_bite",
## "reference_teeth":
## [11, 21, 31, 41]
## }
## "2d2ddb74-
## 4d56-4fb0-
a6b8-
## 024eaf20fa7d"
## ,
## "chart_id":
## "6ae0746a-
## 511e-4a5d-
## 88c9-
## 975234efc03a"
## }
- A new VDO
evaluation
record is
created in the
database.
## 3. No
exception is
raised.
## UTC
## -23-
## TC-
## 02
## Failure:
Create a
## VDO
evaluation
with a non-
existent chart
## ID.
No dental
chart with the
given chart_id
exists in the
database.
## {
## "chart_id":
## "999999",

## "facial_soft_tissue"
## :
## ["nasolabial_fold"],

## "closest_speaking":
## 2.0,
## "free_way_space":
## 3.0,
## "bite_type":
## "normal_bite",
## "reference_teeth":
## [11, 21]
## }
- Creation is
rejected.
- The response
status code is
404 (Not
## Found).
## { "message":
"Chart not
found" }
## UTC
## -23-
## TC-
## 03
## Failure:
Create a
## VDO
evaluation
with missing
required
fields.
## Valid
authentication
token is
provided.
Dental chart
## "6ae0746a-
## 511e-4a5d-
## 88c9-
## 975234efc03a
## {
## "chart_id":
## "6ae0746a-511e-4a5d-
## 88c9-975234efc03a",

## "facial_soft_tissue"
## : [],

## "closest_speaking":
null,
## "free_way_space":
null,
## "bite_type": "",
- Creation is
rejected.
- Returns a
validation error
response.
- The response
status code is
## 422
(Unprocessable
## Entity).

" exists in the
database.
## "reference_teeth":
## []
## }
## { "message":
"Missing
required
fields" }
- No record is
created in the
database.
## UTC
## -23-
## TC-
## 04
## Failure:
Create a
## VDO
evaluation
without
authentication
## .
## No
authentication
token is
provided.
No Bearer Token 1. Access is
denied.
- Returns an
authentication
error response.
- The response
status code is
## 401
(Unauthorized)
## .
## { "message":
"Unauthorized
## " }






















UTC-24 : View VDO Evaluation
Unit Test ID: UTC-24
Module: VDO Evaluation Service
Method Under Test: get_vdo_evaluation_by_chart_id(session, chart_id)
Description: Verifies that a dentist can view the VDO evaluation record belonging
to a selected chart and that invalid access attempts are properly rejected.
Prerequisite Data: Valid authentication token and existing chart ID.
## Test Case:
## No. Description Prerequisite Input Expected Output
## UTC
## -24-
## TC-
## 01
## Success:
View a VDO
evaluation for
an existing
chart.
## Valid
authentication
token is
provided.
Dental chart
## "6ae0746a-
## 511e-4a5d-
## 88c9-
## 975234efc03a
" exists with a
## VDO
evaluation
record.
## {
## "chart_id":
## "6ae0746a-
## 511e-4a5d-
## 88c9-
## 975234efc03a
## " }
- Returns the VDO
Evaluation object:
## {
## "vdo_id":
## "2d2ddb74-4d56-4fb0-
a6b8-024eaf20fa7d",
## "chart_id":
## "6ae0746a-511e-4a5d-
## 88c9-975234efc03a",

## "facial_soft_tissue"
## :
## ["nasolabial_fold",
## "thin_lips"],

## "closest_speaking":
## 2.0,
## "free_way_space":

## 3.0,
## "bite_type":
## "normal_bite",
## "reference_teeth":
## [11, 21, 31, 41]
## }
- No exception is
raised.
## UTC
## -24-
## TC-
## 02
## Failure:
View a VDO
evaluation for
a non-existent
chart ID.
No dental
chart with the
given chart_id
exists in the
database.
## {
## "chart_id":
## "999999" }
- Request is rejected.
- The response status
code is 404 (Not
## Found).
{ "message": "Chart
not found" }
## UTC
## -24-
## TC-
## 03
## Failure:
View a VDO
evaluation
with no chart
ID provided.
## Valid
authentication
token is
provided.
## {
## "chart_id":
## "" }
- Request is rejected.
- The response status
code is 422
(Unprocessable Entity).
## { "message":
"Missing chart ID" }
## UTC
## -24-
## TC-
## 04
## Failure:
View a VDO
evaluation
without
authentication
## .
## No
authentication
token is
provided.
## No Bearer
## Token
- Access is denied.
- The response status
code is 401
(Unauthorized).
## { "message":
"Unauthorized" }

















UTC-25 : Update VDO Evaluation
Unit Test ID: UTC-25
Module: VDO Evaluation Service
Method Under Test: update_vdo_evaluation(session, chart_id, payload)
Description: Verifies that a dentist can successfully update an existing VDO
evaluation record and that invalid update attempts are properly rejected.
Prerequisite Data: Valid authentication token, existing chart ID and VDO
evaluation information.
## Test Case:
## No. Description Prerequisite Input Expected Output
## UT
## C-
## 25-
## TC-
## 01
## Success:
Update a
## VDO
evaluation
with valid
information
## .
## Valid
authenticati
on token is
provided.
## Dental
chart
## "6ae0746a-
## 511e-4a5d-
## 88c9-
## 975234efc0
3a" exists
with a
## VDO
evaluation
record.
## {
## "chart_id":
## "6ae0746a-511e-
## 4a5d-88c9-
## 975234efc03a",

## "facial_soft_tissue
## ":
## ["drooping_commissu
re"],
## "free_way_space":
## 2.5,
## "bite_type":
## "deep_bite",

## "reference_teeth":
## [13, 23]
## }
- Returns the updated
VDO Evaluation
object:
## {
## "vdo_id":
## "2d2ddb74-4d56-
## 4fb0-a6b8-
## 024eaf20fa7d",
## "chart_id":
## "6ae0746a-511e-
## 4a5d-88c9-
## 975234efc03a",

## "facial_soft_tissue
## ":
## ["drooping_commissu
re"],
## "free_way_space":
## 2.5,
## "bite_type":

## "deep_bite",

## "reference_teeth":
## [13, 23],
## "updated_at":
## "2026-04-
## 25T10:00:00.000000"
## }
- VDO evaluation
record is updated in
the database.
- No exception is
raised.
## UT
## C-
## 25-
## TC-
## 02
## Failure:
Update a
## VDO
evaluation
for a non-
existent
chart ID.
No dental
chart with
the given
chart_id
exists in the
database.
## {
## "chart_id":
## "999999",
## "free_way_space":
## 2.5,
## "bite_type":
## "deep_bite"
## }
- Update is rejected.
- The response status
code is 404 (Not
## Found).
{ "message": "Chart
not found" }
## UT
## C-
## 25-
## TC-
## 03
## Failure:
Update a
## VDO
evaluation
without
authenticati
on.
## No
authenticati
on token is
provided.
No Bearer Token 1. Access is denied.
- The response status
code is 401
(Unauthorized).
## { "message":
"Unauthorized" }














## 3.1.8) Dental Status Module
UTC-26 : Update/Replace Dental Status
Unit Test ID: UTC-26
## Module: Dental Status Service
Method Under Test: create_or_replace_dental_status_endpoint(chart_id, payload,
session)
Description: Verifies that a dentist can successfully save or replace the dental
status (tooth chart) for an existing chart. If a dental status record already exists it is
fully replaced; otherwise a new record is created.
Prerequisite Data: Valid authentication token and existing chart ID.
## Test Case:
## No. Description Prerequisite Input Expected Output
## UT
## C-
## 26-
## TC-
## 01
## Success:
## Save/replac
e dental
status with
valid tooth
information.
## Valid
authenticatio
n token is
provided.
Dental chart
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d
5a" exists in
the database.
Any existing
dental status
record is
replaced.
chart_id =
## "d8454cab-1a71-
## 46e8-8ac1-
## 69ebae557d5a"
## {
## "teeth": [
## {

## "tooth_number":
## 16, "tooth_type":
## "permanent",
## "caries":
[{"surface": "O",
## "depth":
## "dentine"}],
## "fillings":
## [{"surfaces":
## ["M","O"],
## "material":
## "composite"}],
## "vitality":
## {"root_canal_treat
- Dental status is
saved/replaced in
the database.
- Returns the
updated dental status
object:
## {
## "status_id":
## "2ab9b18e-c03e-
## 40c6-afa4-
## 0a4f8f568b23",
## "chart_id":
## "d8454cab-1a71-
## 46e8-8ac1-
## 69ebae557d5a",
## "created_at":
## "2026-05-
## 03T13:44:31.33817
## 6",
## "teeth": [

ed": "completed",
## "ept_result":
## "positive"},

## "restorations":
## {"restoration_type
## ": "crown",
## "material":
## "zirconia"}
## },
## {

## "tooth_number":
## 11, "tooth_type":
## "primary",
## "fillings":
## [{"surfaces":
## ["M","O"],
## "material":
## "composite"}],

## "periodontal":
## {"mobility_grade":
## "M1",
## "recession_mm":
## 0.2},
## "vitality":
## {"root_canal_treat
ed": "completed",
## "ept_result":
## "positive"},

## "restorations":
## {"restoration_type
## ": "crown",
## "material":
## "zirconia"}
## },
## {

## "tooth_number":
## 46, "tooth_type":
## "edentulous",

## "edentulous":
## {"edentulous_type"
## : "missing"}
## },
## {

## "tooth_number":
## {
## "tooth_id":
## "cc22f486-d338-
## 43f0-800d-
f12a51554be3",

## "tooth_number":
## 16, "tooth_type":
## "permanent",
## "caries":
## [{"caries_id":
## "de947216-...",
"surface": "O",
## "depth":
## "dentine"}],
## "fillings":
## [{"filling_id":
## "267f7ee7-...",
## "surfaces":
## ["M","O"],
## "material":
## "composite"}],
## "vitality":
## {"vitality_id":
## "389e1614-...",
## "ept_result":
## "positive",
## "root_canal_treat
ed":
## "completed"},

## "restorations":
## {"restoration_id"
## : "19282cec-...",
## "restoration_type
## ": "crown",
## "material":
## "zirconia"}
## },
## {
## "tooth_id":
## "ce16880a-478d-
## 4e2b-a274-
## 6eb442c75565",

## "tooth_number":
## 11, "tooth_type":
## "primary",
## "fillings":
## [{"filling_id":
## "372e58ba-...",

## 13, "tooth_type":
## "implant",
## "implant": {

## "component_type":
## "crown",

## "retention_type":
## "screw_retained",

## "material":
## "zirconia"
## }
## }
## ]
## }
## "surfaces":
## ["M","O"],
## "material":
## "composite"}],

## "periodontal":
## {"periodontal_id"
## : "a2f6b9f4-...",
## "mobility_grade":
## "M1",
## "recession_mm":
## 0.2},
## "vitality":
## {"vitality_id":
## "a5176a0e-...",
## "ept_result":
## "positive",
## "root_canal_treat
ed":
## "completed"},

## "restorations":
## {"restoration_id"
## : "b4894efc-...",
## "restoration_type
## ": "crown",
## "material":
## "zirconia"}
## },
## {
## "tooth_id":
## "ce2f77b5-776e-
## 4d61-afa3-
## 705b5e59816b",

## "tooth_number":
## 46, "tooth_type":
## "edentulous",

## "edentulous":
## {"edentulous_id":
## "7f53ef15-...",
## "edentulous_type"
## : "missing"}
## },
## {
## "tooth_id":
## "3bea3479-e20d-
## 4dcc-877d-
## 44ceeb6ae64d",


## "tooth_number":
## 13, "tooth_type":
## "implant",
## "implant":
## {"implant_id":
## "81f8fc6b-...",
## "component_type":
## "crown",

## "retention_type":
## "screw_retained",
## "material":
## "zirconia"}
## }
## ]
## }
- No exception is
raised.
## UT
## C-
## 26-
## TC-
## 02
## Failure:
Save dental
status with a
non-existent
chart ID.
No dental
chart with
the given
chart_id
exists in the
database.
chart_id =
## "999999"

## { "teeth": [ {
## "tooth_number":
## 11, "tooth_type":
## "permanent" } ] }
- Request is
rejected.
- The response
status code is 404
(Not Found).
## { "message":
"Chart not found"
## }
## UT
## C-
## 26-
## TC-
## 03
## Failure:
Save dental
status with
missing
required
fields.
## Valid
authenticatio
n token is
provided.
Dental chart
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d
5a" exists in
the database.
chart_id =
## "d8454cab-1a71-
## 46e8-8ac1-
## 69ebae557d5a"

## { "teeth": [ {
## "tooth_number":
## 16, "tooth_type":
## "" } ] }
- Request is
rejected.
- Returns a
validation error
response.
- The response
status code is 422
(Unprocessable
## Entity).
## { "message":
"Missing required
fields" }
- No dental status
record is modified in
the database.
## UT
## C-
## 26-
## Failure:
Save dental
status
without
## No
authenticatio
n token is
provided.
No Bearer Token 1. Access is denied.
- The response
status code is 401
(Unauthorized).

## TC-
## 04
authenticati
on.
## { "message":
"Unauthorized" }























UTC-27 : View Dental Status
Unit Test ID: UTC-27
## Module: Dental Status Service
Method Under Test: get_dental_status_endpoint(chart_id, session)
Description: Verifies that a dentist can view the complete dental status belonging
to a selected chart and that invalid access attempts are properly rejected.
Prerequisite Data: Valid authentication token and existing chart ID.
## Test Case:
## No. Description Prerequisite Input Expected Output
## UTC
## -27-
## TC-
## 01
## Success:
View dental
status for an
existing chart.
## Valid
authentication
token is
provided.
Dental chart
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d5a
" exists with a
dental status
record.
## {
## "chart_id":
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d5a
## " }
- Returns the Dental
Status object:
## {
## "status_id":
## "2ab9b18e-c03e-40c6-
afa4-0a4f8f568b23",
## "chart_id":
## "d8454cab-1a71-46e8-
## 8ac1-69ebae557d5a",
## "created_at":
## "2026-05-
## 03T13:44:31.338176",
## "teeth": [
## {
## "tooth_id":
## "cc22f486-d338-43f0-
## 800d-f12a51554be3",

## "tooth_number": 16,
## "tooth_type":
## "permanent",
## "caries":
## [{"caries_id":
## "de947216-...",
"surface": "O",
## "depth":
## "dentine"}],
## "fillings":
## [{"filling_id":
## "267f7ee7-...",
## "surfaces":
## ["M","O"],
## "material":
## "composite"}],
## "vitality":
## {"vitality_id":

## "389e1614-...",
## "ept_result":
## "positive",
## "root_canal_treated"
## : "completed"},

## "restorations":
## {"restoration_id":
## "19282cec-...",
## "restoration_type":
## "crown", "material":
## "zirconia"}
## },
## {
## "tooth_id":
## "ce16880a-478d-4e2b-
a274-6eb442c75565",

## "tooth_number": 11,
## "tooth_type":
## "primary",
## "fillings":
## [{"filling_id":
## "372e58ba-...",
## "surfaces":
## ["M","O"],
## "material":
## "composite"}],
## "periodontal":
## {"periodontal_id":
## "a2f6b9f4-...",
## "mobility_grade":
## "M1",
## "recession_mm":
## 0.2},
## "vitality":
## {"vitality_id":
## "a5176a0e-...",
## "ept_result":
## "positive",
## "root_canal_treated"
## : "completed"},

## "restorations":
## {"restoration_id":
## "b4894efc-...",
## "restoration_type":
## "crown", "material":
## "zirconia"}
## },
## {

## "tooth_id":
## "ce2f77b5-776e-4d61-
afa3-705b5e59816b",

## "tooth_number": 46,
## "tooth_type":
## "edentulous",
## "edentulous":
## {"edentulous_id":
## "7f53ef15-...",
## "edentulous_type":
## "missing"}
## },
## {
## "tooth_id":
## "3bea3479-e20d-4dcc-
## 877d-44ceeb6ae64d",

## "tooth_number": 13,
## "tooth_type":
## "implant",
## "implant":
## {"implant_id":
## "81f8fc6b-...",
## "component_type":
## "crown",

## "retention_type":
## "screw_retained",
## "material":
## "zirconia"}
## }
## ]
## }
- No exception is
raised.
## UTC
## -27-
## TC-
## 02
## Failure:
View dental
status for a
non-existent
chart ID.
No dental
chart with the
given chart_id
exists in the
database.
## {
## "chart_id":
## "999999" }
- Request is rejected.
- The response status
code is 404 (Not
## Found).
{ "message": "Chart
not found" }
## UTC
## -27-
## TC-
## 03
## Failure:
View dental
status with no
chart ID
provided.
## Valid
authentication
token is
provided.
## {
## "chart_id":
## "" }
- Request is rejected.
- The response status
code is 422
(Unprocessable Entity).
## { "message":
"Missing chart ID" }

## UTC
## -27-
## TC-
## 04
## Failure:
View dental
status without
authentication
## .
## No
authentication
token is
provided.
## No Bearer
## Token
- Access is denied.
- The response status
code is 401
(Unauthorized).
## { "message":
"Unauthorized" }
















## 3.1.9) Occlusal Analysis & Occlusal Contact Module
UTC-28 : Update/Replace Occlusal Analysis
Unit Test ID: UTC-28
## Module: Occlusal Analysis Service
Method Under Test: upsert_occlusal_analysis(session, chart_id, payload)

Description: Verifies that a dentist can successfully save or replace the occlusal
analysis record for an existing chart. If a record already exists it is fully replaced;
otherwise a new record is created.
Prerequisite Data: Valid authentication token and existing chart ID.
## Test Case:
## No. Description Prerequisite Input Expected Output
## UTC
## -28-
## TC-
## 01
## Success:
## Save/replac
e occlusal
analysis
with valid
information.
## Valid
authenticatio
n token is
provided.
Dental chart
## "cc3ec91f-
## 3412-409c-
## 9471-
## 8d5a017b5a
da" exists in
the database.
Any existing
occlusal
analysis
record is
replaced.
## {
## "chart_id":
## "cc3ec91f-3412-
## 409c-9471-
## 8d5a017b5ada",
## "right_molar":
## "class_iii",
## "left_molar":
## "class_ii",

## "overlap_horizonta
l": 25.3,

## "overlap_vertical"
## : 32.4,

## "anterior_slide":
## 32.5,
## "lateral_slide":
## 23.2
## }
- Occlusal analysis
is saved/replaced in
the database.
- Returns the saved
## Occlusal Analysis
object:
## {
## "occlusal_id":
## "19125d64-deb7-
## 4bb6-b0b2-
## 171bac42590f",
## "chart_id":
## "cc3ec91f-3412-
## 409c-9471-
## 8d5a017b5ada",
## "right_molar":
## "class_iii",
## "left_molar":
## "class_ii",

## "overlap_horizonta
l": 25.3,

## "overlap_vertical"
## : 32.4,

## "anterior_slide":
## 32.5,
## "lateral_slide":
## 23.2
## }
- No exception is
raised.
## UTC
## -28-
## TC-
## 02
## Failure:
## Save
occlusal
analysis
with a non-
No dental
chart with
the given
chart_id
## {
## "chart_id":
## "999999",
## "right_molar":
## "class_iii",
## "left_molar":
## "class_ii",
- Request is
rejected.
- The response
status code is 404
(Not Found).

existent
chart ID.
exists in the
database.

## "overlap_horizonta
l": 25.3,

## "overlap_vertical"
## : 32.4,

## "anterior_slide":
## 32.5,
## "lateral_slide":
## 23.2
## }
## { "message":
"Chart not found"
## }
## UTC
## -28-
## TC-
## 03
## Failure:
## Save
occlusal
analysis
with
missing
required
fields.
## Valid
authenticatio
n token is
provided.
Dental chart
## "cc3ec91f-
## 3412-409c-
## 9471-
## 8d5a017b5a
da" exists in
the database.
## {
## "chart_id":
## "cc3ec91f-3412-
## 409c-9471-
## 8d5a017b5ada",
## "right_molar":
## "",
## "left_molar": ""
## }
- Request is
rejected.
- Returns a
validation error
response.
- The response
status code is 422
(Unprocessable
## Entity).
## { "message":
"Missing required
fields" }
- No occlusal
analysis record is
modified in the
database.
## UTC
## -28-
## TC-
## 04
## Failure:
## Save
occlusal
analysis
without
authenticati
on.
## No
authenticatio
n token is
provided.
No Bearer Token 1. Access is denied.
- The response
status code is 401
(Unauthorized).
## { "message":
"Unauthorized" }






















UTC-29 : Update/Replace Occlusal Contact
Unit Test ID: UTC-29
## Module: Occlusal Analysis Service
Method Under Test: create_and_replace_occlusal_contacts_endpoint(chart_id,
payload, session)
Description: Verifies that a dentist can successfully save or replace the occlusal
contact records for an existing chart. All existing contact records are replaced with
the new set.
Prerequisite Data: Valid authentication token and existing chart ID.
## Test Case:

## No. Description Prerequisite Input Expected Output
## UTC-
## 29-
## TC-
## 01
## Success:
## Save/replace
occlusal
contacts with
valid
information.
## Valid
authentication
token is
provided.
Dental chart
## "cc3ec91f-
## 3412-409c-
## 9471-
## 8d5a017b5ada"
exists in the
database. Any
existing
occlusal
contact records
are replaced.
chart_id =
## "cc3ec91f-3412-
## 409c-9471-
## 8d5a017b5ada"

## {
## "contacts": [

## {"contact_type":
## "premature",
## "upper_tooth":
## 15,
## "lower_tooth":
## 45},

## {"contact_type":
## "protrusive",
## "upper_tooth":
## 13,
## "lower_tooth":
## 43},

## {"contact_type":
## "mip",
## "upper_tooth":
## 33,
## "lower_tooth":
## 22},

## {"contact_type":
## "working",
## "upper_tooth":
## 42,
## "lower_tooth":
## 41},

## {"contact_type":
## "non_working",
## "upper_tooth":
## 11,
## "lower_tooth":
## 22}
## ]
## }
## 1. Occlusal
contacts are
saved/replaced in
the database.
- Returns the
saved contact list:
## [

## {"contact_id":
## "686a9f31-...",
## "contact_type":
## "premature",
## "upper_tooth":
## 15,
## "lower_tooth":
## 45},

## {"contact_id":
## "b94f1504-...",
## "contact_type":
## "protrusive",
## "upper_tooth":
## 13,
## "lower_tooth":
## 43},

## {"contact_id":
## "d32dcc7a-...",
## "contact_type":
## "mip",
## "upper_tooth":
## 33,
## "lower_tooth":
## 22},

## {"contact_id":
## "9d669cb4-...",
## "contact_type":
## "working",
## "upper_tooth":
## 42,
## "lower_tooth":
## 41},

## {"contact_id":
## "8c906d54-...",
## "contact_type":
## "non_working",

## "upper_tooth":
## 11,
## "lower_tooth":
## 22}
## ]
- No exception is
raised.
## UTC-
## 29-
## TC-
## 02
## Failure: Save
occlusal
contacts with
a non-existent
chart ID.
No dental chart
with the given
chart_id exists
in the database.
chart_id =
## "999999"

## { "contacts": [
## {
## "contact_type":
## "mip",
## "upper_tooth":
## 16,
## "lower_tooth":
## 46 } ] }
- Request is
rejected.
- The response
status code is 404
(Not Found).
## { "message":
"Chart not
found" }
## UTC-
## 29-
## TC-
## 03
## Failure: Save
occlusal
contacts with
missing
required
fields.
## Valid
authentication
token is
provided.
Dental chart
## "cc3ec91f-
## 3412-409c-
## 9471-
## 8d5a017b5ada"
exists in the
database.
chart_id =
## "cc3ec91f-3412-
## 409c-9471-
## 8d5a017b5ada"

## { "contacts": [
## {
## "contact_type":
## "",
## "upper_tooth":
null,
## "lower_tooth":
null } ] }
- Request is
rejected.
- Returns a
validation error
response.
- The response
status code is 422
(Unprocessable
## Entity).
## { "message":
"Missing
required
fields" }
- No occlusal
contact records
are modified in
the database.
## UTC-
## 29-
## TC-
## 04
## Failure: Save
occlusal
contacts
without
authentication.
## No
authentication
token is
provided.
No Bearer Token 1. Access is
denied.
- The response
status code is 401
(Unauthorized).
## { "message":
"Unauthorized"
## }











UTC-30 : View Occlusal Analysis & Contact
Unit Test ID: UTC-30
## Module: Occlusal Analysis Service
Method Under Test: get_occlusal_analysis_record(chart_id, session)
Description: Verifies that a dentist can view the occlusal analysis details and all
associated contact points belonging to a selected chart and that invalid access
attempts are properly rejected.
Prerequisite Data: Valid authentication token and existing chart ID.
## Test Case:
## No. Description Prerequisite Input Expected Output
## UTC
## -30-
## Success:
## View
occlusal
## Valid
authenticatio
n token is
## {
## "chart_id":
## "cc3ec91f-
## 3412-409c-
- Returns the Occlusal
Analysis object including all
contacts:

## TC-
## 01
analysis and
contact
records for
an existing
chart.
provided.
Dental chart
## "cc3ec91f-
## 3412-409c-
## 9471-
## 8d5a017b5a
da" exists
with occlusal
analysis and
contact
records.
## 9471-
## 8d5a017b5ad
a" }
## {
## "occlusal_id":
## "19125d64-deb7-4bb6-
b0b2-171bac42590f",
## "chart_id": "cc3ec91f-
## 3412-409c-9471-
## 8d5a017b5ada",
## "right_molar":
## "class_i",
## "left_molar":
## "class_ii",
## "overlap_horizontal":
## 2.5,
## "overlap_vertical":
## 3.0,
## "anterior_slide": 1.0,
## "lateral_slide": 0.5,
## "contacts": {
## "mip": [
## {"contact_id":
## "686a9f31-...",
## "upper_tooth": 16,
## "lower_tooth": 46},
## {"contact_id":
## "b94f1504-...",
## "upper_tooth": 26,
## "lower_tooth": 36}
## ],
## "premature":
## [{"contact_id":
## "ad0417e1-...",
## "upper_tooth": 25,
## "lower_tooth": 35}],
## "protrusive":
## [{"contact_id":
## "9d669cb4-...",
## "upper_tooth": 11,
## "lower_tooth": 41}],
## "working":
## [{"contact_id":
## "8c906d54-...",
## "upper_tooth": 23,
## "lower_tooth": 33}],

## "non_working":[{"contact
## _id": "b2bf116c-...",
## "upper_tooth": 26,
## "lower_tooth": 36}]
## }
## }
- No exception is raised.

## UTC
## -30-
## TC-
## 02
## Failure:
## View
occlusal
record for a
non-existent
chart ID.
No dental
chart with
the given
chart_id
exists in the
database.
## {
## "chart_id":
## "999999" }
- Request is rejected.
- The response status code
is 404 (Not Found).
{ "message": "Chart not
found" }
## UTC
## -30-
## TC-
## 03
## Failure:
## View
occlusal
record with
no chart ID
provided.
## Valid
authenticatio
n token is
provided.
## {
## "chart_id":
## "" }
- Request is rejected.
- The response status code
is 422 (Unprocessable
## Entity).
{ "message": "Missing
chart ID" }
## UTC
## -30-
## TC-
## 04
## Failure:
## View
occlusal
record
without
authenticati
on.
## No
authenticatio
n token is
provided.
## No Bearer
## Token
- Access is denied.
- The response status code
is 401 (Unauthorized).
## { "message":
"Unauthorized" }

## 3.1.10) Residual Ridge Assessment Module

UTC-30 : View Occlusal Analysis & Contact
Unit Test ID: UTC-30
## Module: Occlusal Analysis Service
Method Under Test: get_occlusal_analysis_record(chart_id, session)
Description: Verifies that a dentist can view the occlusal analysis details and all
associated contact points belonging to a selected chart and that invalid access
attempts are properly rejected.
Prerequisite Data: Valid authentication token and existing chart ID.
## Test Case:
## No. Description Prerequisite Input Expected Output
## UTC
## -30-
## Success:
## View
occlusal
## Valid
authenticatio
n token is
## {
## "chart_id":
## "cc3ec91f-
## 3412-409c-
- Returns the Occlusal
Analysis object including all
contacts:

## TC-
## 01
analysis and
contact
records for
an existing
chart.
provided.
Dental chart
## "cc3ec91f-
## 3412-409c-
## 9471-
## 8d5a017b5a
da" exists
with occlusal
analysis and
contact
records.
## 9471-
## 8d5a017b5ad
a" }
## {
## "occlusal_id":
## "19125d64-deb7-4bb6-
b0b2-171bac42590f",
## "chart_id": "cc3ec91f-
## 3412-409c-9471-
## 8d5a017b5ada",
## "right_molar":
## "class_i",
## "left_molar":
## "class_ii",
## "overlap_horizontal":
## 2.5,
## "overlap_vertical":
## 3.0,
## "anterior_slide": 1.0,
## "lateral_slide": 0.5,
## "contacts": {
## "mip": [
## {"contact_id":
## "686a9f31-...",
## "upper_tooth": 16,
## "lower_tooth": 46},
## {"contact_id":
## "b94f1504-...",
## "upper_tooth": 26,
## "lower_tooth": 36}
## ],
## "premature":
## [{"contact_id":
## "ad0417e1-...",
## "upper_tooth": 25,
## "lower_tooth": 35}],
## "protrusive":
## [{"contact_id":
## "9d669cb4-...",
## "upper_tooth": 11,
## "lower_tooth": 41}],
## "working":
## [{"contact_id":
## "8c906d54-...",
## "upper_tooth": 23,
## "lower_tooth": 33}],

## "non_working":[{"contact
## _id": "b2bf116c-...",
## "upper_tooth": 26,
## "lower_tooth": 36}]
## }
## }
- No exception is raised.

## UTC
## -30-
## TC-
## 02
## Failure:
## View
occlusal
record for a
non-existent
chart ID.
No dental
chart with
the given
chart_id
exists in the
database.
## {
## "chart_id":
## "999999" }
- Request is rejected.
- The response status code
is 404 (Not Found).
{ "message": "Chart not
found" }
## UTC
## -30-
## TC-
## 03
## Failure:
## View
occlusal
record with
no chart ID
provided.
## Valid
authenticatio
n token is
provided.
## {
## "chart_id":
## "" }
- Request is rejected.
- The response status code
is 422 (Unprocessable
## Entity).
{ "message": "Missing
chart ID" }
## UTC
## -30-
## TC-
## 04
## Failure:
## View
occlusal
record
without
authenticati
on.
## No
authenticatio
n token is
provided.
## No Bearer
## Token
- Access is denied.
- The response status code
is 401 (Unauthorized).
## { "message":
"Unauthorized" }
















UTC-31 : Create Residual Ridge Assessment
Unit Test ID: UTC-31
## Module: Residual Ridge Assessment Service
Method Under Test: create_residual_ridge_assessment(session, chart_id, payload)
Description: Verifies that a dentist can successfully create a residual ridge
assessment record for an existing dental chart and that invalid or unauthorized
creation attempts are properly rejected.
Prerequisite Data: Valid authentication token and existing chart ID.
## Test Case:
## No. Description Prerequisite Input Expected Output
## UTC
## -31-
## TC-
## 01
## Success:
Create a
residual
ridge
assessment
with valid
information.
## Valid
authenticatio
n token is
provided.
Dental chart
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d5
## {
## "chart_id":
## "d8454cab-1a71-46e8-
## 8ac1-69ebae557d5a",
## "ridge_height":
## "low_flat",
## "ridge_width":
## "narrow",
## "jaw_size":
## "medium",

## "ridge_shape_upper":
## "u_shape",
- Returns the
created Residual
## Ridge
## Assessment
object:
## {

## "assessment_id
## ": "87b67cca-
## 5a61-417b-
## 9c7b-
f3706852ad8d",

a" exists in
the database.

## "ridge_shape_lower":
## "v_shape",
## "ridge_relation":
## "class_i",

## "ridge_parallelism":
## "parallel",

## "interridge_space":
## "sufficient",
## "lower_arch_form":
## "ovoid",
## "palatal_vault":
## "average",

## "palatal_throat_form
## ": "class_ii",

## "freenum_attachment"
## : {
## "upper_labial":
## "normal",
## "lower_labial":
## "low",
## "buccal":
## "multiple"
## },
## "ridge_deformity":
## ["bone_spicule",
## "sharp_ridge"],
## "torus_palatinus":
{"presence": true,
## "size": "small"},
## "tongue_size":
## "medium",
## "tongue_position":
## "normal",
## "saliva_amount":
## "normal",

## "saliva_consistency"
## : "thin",
## "lip_mobility":
## "normal",

## "facial_muscle_tone"
## : "average",
## "mental_attitude":
## "philosophical",
"note": "Patient
## "chart_id":
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d5a"
## }
- A new
residual ridge
assessment
record is created
in the database.
- No exception
is raised.

has slightly shallow
lower ridge."
## }
## UTC
## -31-
## TC-
## 02
## Failure:
Create a
residual
ridge
assessment
with a non-
existent chart
## ID.
No dental
chart with the
given
chart_id
exists in the
database.
## {
## "chart_id":
## "999999",
## "ridge_height":
## "low_flat",
## "ridge_width":
## "narrow",
## "jaw_size":
## "medium",

## "ridge_shape_upper":
## "u_shape",

## "ridge_shape_lower":
## "v_shape",
## "ridge_relation":
## "class_i"
## }
- Creation is
rejected.
- The response
status code is
404 (Not
## Found).
## { "message":
"Chart not
found" }
## UTC
## -31-
## TC-
## 03
## Failure:
Create a
residual
ridge
assessment
with missing
required
fields.
## Valid
authenticatio
n token is
provided.
Dental chart
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d5
a" exists in
the database.
## {
## "chart_id":
## "d8454cab-1a71-46e8-
## 8ac1-69ebae557d5a",
## "ridge_height":
## "",
## "ridge_width": "",
## "jaw_size": "",

## "ridge_shape_upper":
## "",

## "ridge_shape_lower":
## "",
## "ridge_relation":
## ""
## }
- Creation is
rejected.
- Returns a
validation error
response.
- The response
status code is
## 422
(Unprocessable
## Entity).
## { "message":
"Missing
required
fields" }
- No record is
created in the
database.
## UTC
## -31-
## TC-
## 04
## Failure:
Create a
residual
ridge
assessment
without
## No
authenticatio
n token is
provided.
No Bearer Token 1. Access is
denied.
- The response
status code is
## 401
(Unauthorized).
## { "message":

authenticatio
n.
"Unauthorized"
## }




UTC-32 : View Residual Ridge Assessment
Unit Test ID: UTC-32
## Module: Residual Ridge Assessment Service
Method Under Test: get_residual_ridge_assessment(session, chart_id)
Description: Verifies that a dentist can view the residual ridge assessment
belonging to a selected chart and that invalid access attempts are properly rejected.
Prerequisite Data: Valid authentication token and existing chart ID.
## Test Case:
## No. Description Prerequisite Input Expected Output
## UTC
## -32-
## TC-
## 01
## Success:
View a
residual ridge
assessment
for an
existing
chart.
## Valid
authentication
token is
provided.
Dental chart
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d5a
" exists with a
residual ridge
assessment
record.
## {
## "chart_id":
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d5a
## " }
- Returns the Residual
## Ridge Assessment
object:
## {
## "assessment_id":
## "87b67cca-5a61-417b-
## 9c7b-f3706852ad8d",
## "chart_id":
## "d8454cab-1a71-46e8-
## 8ac1-69ebae557d5a",
## "ridge_height":
## "low_flat",
## "ridge_width":
## "narrow",
## "jaw_size":
## "medium",

## "ridge_shape_upper":
## "u_shape",


## "ridge_shape_lower":
## "v_shape",
## "ridge_relation":
## "class_i",

## "ridge_parallelism":
## "parallel",
## "interridge_space":
## "sufficient",
## "lower_arch_form":
## "ovoid",
## "palatal_vault":
## "average",

## "palatal_throat_form"
## : "class_ii",

## "freenum_attachment":
## {
## "upper_labial":
## "normal",
## "lower_labial":
## "low", "buccal":
## "multiple"
## },
## "ridge_deformity":
## ["bone_spicule",
## "sharp_ridge"],
## "torus_palatinus":
{"presence": true,
## "size": "small"},
## "tongue_size":
## "medium",
## "tongue_position":
## "normal",
## "saliva_amount":
## "normal",

## "saliva_consistency":
## "thin",
## "lip_mobility":
## "normal",

## "facial_muscle_tone":
## "average",
## "mental_attitude":
## "philosophical",
## "ridge_deformity":
## ["bone_spicule",
## "sharp_ridge"],

## "created_at":
## "2026-05-
## 23T19:10:54.073852Z",
## "updated_at":
## "2026-05-
## 23T19:10:54.073855Z"
## }
- No exception is
raised.
## UTC
## -32-
## TC-
## 02
## Failure:
View a
residual ridge
assessment
for a non-
existent chart
## ID.
No dental
chart with the
given chart_id
exists in the
database.
## {
## "chart_id":
## "999999" }
- Request is rejected.
- The response status
code is 404 (Not
## Found).
{ "message": "Chart
not found" }
## UTC
## -32-
## TC-
## 03
## Failure:
View a
residual ridge
assessment
with no chart
ID provided.
## Valid
authentication
token is
provided.
## {
## "chart_id":
## "" }
- Request is rejected.
- The response status
code is 422
(Unprocessable Entity).
{ "message": "Missing
chart ID" }
## UTC
## -32-
## TC-
## 04
## Failure:
View a
residual ridge
assessment
without
authenticatio
n.
## No
authentication
token is
provided.
## No Bearer
## Token
- Access is denied.
- The response status
code is 401
(Unauthorized).
## { "message":
"Unauthorized" }









UTC-33 : Update Residual Ridge Assessment
Unit Test ID: UTC-33
## Module: Residual Ridge Assessment Service
Method Under Test: update_residual_ridge_assessment(session, chart_id,
payload)
Description: Verifies that a dentist can successfully update an existing residual
ridge assessment record and that invalid update attempts are properly rejected.
Prerequisite Data: Valid authentication token, existing chart ID and residual ridge
assessment information.
## Test Case:
## No. Description Prerequisite Input Expected Output
## UTC
## -33-
## TC-
## 01
## Success:
Update a
residual
ridge
assessment
with valid
information.
## Valid
authenticatio
n token is
provided.
Dental chart
## "d8454cab-
## 1a71-46e8-
## 8ac1-
## 69ebae557d5
a" exists with
a residual
ridge
assessment
record.
## {
## "chart_id":
## "d8454cab-1a71-
## 46e8-8ac1-
## 69ebae557d5a",
## "ridge_height":
## "low_flat",
## "ridge_width":
## "narrow",
## "jaw_size":
## "medium",

## "ridge_shape_uppe
r": "u_shape",

## "ridge_shape_lowe
r": "v_shape",

## "ridge_relation":
## "class_i",

## "ridge_parallelis
m": "parallel",

- Returns the
updated Residual
## Ridge Assessment
object:
## {

## "assessment_id":
## "87b67cca-5a61-
## 417b-9c7b-
f3706852ad8d",
## "chart_id":
## "d8454cab-1a71-
## 46e8-8ac1-
## 69ebae557d5a",
## "ridge_height":
## "low_flat",
## "ridge_width":
## "narrow",
## "jaw_size":
## "medium",

## "ridge_shape_uppe
r": "u_shape",

## "interridge_space
## ": "sufficient",

## "lower_arch_form"
## : "ovoid",

## "palatal_vault":
## "average"
## }

## "ridge_shape_lowe
r": "v_shape",

## "ridge_relation":
## "class_i",

## "ridge_parallelis
m": "parallel",
## "updated_at":
## "2026-05-
## 24T10:00:00.00000
## 0Z"
## }
- Residual ridge
assessment record is
updated in the
database.
- No exception is
raised.
## UTC
## -33-
## TC-
## 02
## Failure:
Update a
residual
ridge
assessment
for a non-
existent
chart ID.
No dental
chart with
the given
chart_id
exists in the
database.
## {
## "chart_id":
## "999999",
## "ridge_height":
## "low_flat",
## "ridge_width":
## "narrow"
## }
- Update is
rejected.
- The response
status code is 404
(Not Found).
## { "message":
"Chart not found"
## }
## UTC
## -33-
## TC-
## 03
## Failure:
Update a
residual
ridge
assessment
without
authenticatio
n.
## No
authenticatio
n token is
provided.
No Bearer Token 1. Access is denied.
- The response
status code is 401
(Unauthorized).
## { "message":
"Unauthorized" }


