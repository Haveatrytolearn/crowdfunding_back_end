# Crowdfunding Back End
Maria Alistratova

## Planning:
### Concept/Name
The name of the project is **Generousource**

This project is a web platform that allows registered users to create fundraising initiatives for various causes and support other users’ initiatives through monetary donations. Donations can be made in any amount via bank transfer or PayPal.

### Intended Audience/User Stories
##### Intended Audience
The platform is intended for individuals who wish to raise funds for personal, social, or community causes, as well as for users who want to contribute financially to initiatives created by others.
The platform can be integrated into a company’s internal processes to allow employees to create fundraising initiatives for their needs.

- As a visitor, I want to browse existing fundraising initiatives so that I can decide whether I want to register on the platform and support a cause.
- As a visitor, I want to register on the website so that I can donate to existing initiatives or create my own fundraiser.
- As a user, I want to log in to the platform so that I can access features that require authentication.
- As a registered user, I want to create my own fundraising initiative so that I can raise funds for a cause I care about.
- As a registered user, I want to donate to other users’ initiatives so that I can support causes I believe in.
- As a registered user, I want to see whether I have already donated to an initiative so that I do not accidentally donate twice.
- As a registered user, I want to update my personal information in my profile so that my account details remain accurate.
- As a donor, I can edit a pledge, but the amount cannot be changed after donation.
- As a fundraiser creator, I want to view donations made to my initiative so that I can track its progress.
- As a fundraiser creator, I can edit a fundraiser, but the title and description cannot be changed after creation.
- As a fundraiser owner, I can delete a fundraiser, but all related data, including donors and their pledges, must be retained in the database.
- As an admin, I can view the list of deleted users and 
- fundraisers.
- As an admin or fundraiser owner, I can view the details of a deleted fundraiser along with its list of pledges.


### Front End Pages/Functionality
![Website pages 1-4: List of initiatives with search, log in page, Registration form, Homepage](crowdfunding/Project%20image/1%20to%204%20project%20image.jpg)
![Website pages 5-8: Read more option for initiatives, Fundraiser page, Payment page, New Fundraiser](crowdfunding/Project%20image/5%20to%208%20project%20image.jpg)
![Website pages 9-12: List of the pledges, My profile, Fundraiser, List of deleted fundraiser](crowdfunding/Project%20image/9%20to%2012%20project%20image.jpg)


### API Spec

| URL | HTTP Method | Purpose | Request Body | Success Response Code | Authentication/Authorisation |
| --- | ----------- | ------- | ------------ | --------------------- | ---------------------------- |
|/api-token-auth/|POST| Authenticate a user and get token| username, password |200 | Authentication |
| /fundraisers/ | GET | Retrieve a list of fundraisers | N/A | 200 | None |
| /fundraisers/ | POST | Create fundraiser | title, description,goal, image | 201 | Authentication/Authorisation |
| /fundraisers/<int:pk>/ | GET | Retrieve fundraiser details | N/A | 200 | Authentication/Authorisation |
| /fundraisers/<int:pk>/ | PUT | Update fundraiser details | Updated fundraiser fields | 200 | Authentication/Authorisation |
| /fundraisers/deleted/ | GET | Retrieve deleted fundraisers | N/A | 200 | Authentication/Authorisation |
| '/fundraisers/deleted/<int:pk>/' | GET | Retrieve a deleted fundraiser | N/A | 200 | Authentication/Authorisation |
| '/fundraisers/deleted/<int:pk>/' | DELETE | Delete a fundraiser | N/A | 200 | Authentication/Authorisation |
| /users/ | GET | Retrieve a list of users | N/A | 200 | Authentication/Authorisation |
| /users/ | POST | Create a user | username, password, email,first_name, last_name | 201 | Authentication/Authorisation |
| /users/<int:pk> | GET | Retrieve user details | N/A | 200 | Authentication/Authorisation|
| /users/<int:pk> | PUT | Update user details | Updated user fields | 200 | Authentication/Authorisation |
| /users/deleted/ | GET | Retrieve deleted users | N/A | 200 | Authentication/Authorisation |
| '/users/deleted/<int:pk>/'| GET | Retrieve a deleted user | N/A | 200 | Authentication/Authorisation |
| '/users/deleted/<int:pk>/'| DELETE | Delete a user | N/A | 200 | Authentication/Authorisation |
| /pledges/ | GET | Retrieve a list of pledges | N/A | 200 | Authentication |
| /pledges/ | POST | Create a new donation | amount, comment, anonymous, fundraiser | 201 | Authentication |
| /pledges/<int:pk> | PUT | Update some pledge details, except amount | Update relevant pledge fields | 200 | Authentication/Authorisation |

### DB Schema
![Database Schema](crowdfunding/Project%20image/DB%20Diagram.jpg)