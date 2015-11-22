UDACITY Project #4 - Scalable Applications

Conference Omnibud appliction / Google App Engine
--------------------------------------------------

### Technologies:
   Google App Engine
   Python 2.7
   Google Cloud Endpoints

## Preparation to register and run the application on Goolge App Engine
   1. A new Application has been registered via the Goolge App Engine called 'Conference Omnibud'.
      This unique App ID is included in `app.yaml`  and defines the context url.
   2. The Google App Client ID is also defined in `settings.py` to
      allow client browsers or front-end applications to access the conference-omnibud back-end api.
   3. The Google App CLIENT_ID in `static/js/app.js` is also defined.
   4. The app was developed and debugged through local instance at the local server's address (by default [localhost:8080])
   5. The Conference Omnibud application has been deployed to Google App Engine and is ready to use.

## Running the application
   1. Access https://conference-omnibud.appspot.com.
   2. Invoke back-end API at https://conference-omnibud.appspot.com/_ah/api/explorer.


### Functionality Design
    -- Functionality is added so that sessions can be defined for a conference.
       The Session database model is defined in the application, as well as the SessionForm presentation model.
       Session attributes Title, Location and Type are defined as String properties.
       When creating a session, the Type is checked to ensure it is a member of a strict SessionType enumeration [WORKSHOP, LECTURE ...].
       StartTime is defined as DateTime property - to capture the session date as well as start time.
       Duration is defined as an Integer property - to designate the duration of the session in minutes.
       1+ speakers can be defined for a Session using a simple ordered list of String properties via the "repeatable=True" NDB field type setting.
       Additionally, 1+ highlights (Strings) can be defined for a session.
       The parent conference unique key is stored as a String property. (See Discussion TASK 1 for design)
       In the SessionForm presentation model, attributes of the parent conference including Name, City and Dates are included.
       Defining these conference attributes allows for fuller information to be displayed for the session's host conference.

    -- A user can add sessions to a wishlist.
       The user's wishlist is implemented as a simple list in his/her profile containing Session keys.
      
    -- A featured speaker can be defined for a conference.
       An implementation to designate a Featured Speaker for a conference is in the application.
       At session definition, if the speaker for the added session is speaking at 1+ sessions in that conference, the speaker is designated
       as Featured. The speaker's name and list of sessions will be added to the applications memory cache.
       The featured speaker information can be retrieved from the memory cache via a backend end-point.
      

### EndPoints Developed
    Conferences ::
       -- List Conferences 
        http://localhost:9080/_ah/api/conference/v1/getConferencesCreated POST
        ** This is the means to find a conference's websafe key.

    Sessions ::
       -- Create Session 
           http://localhost:9080/_ah/api/conference/v1/session POST
           Required: Title, ConferenceKey
 
           Example payload:
           {
            "title": "Yoga in the AM",
            "conferenceKey": "ahZkZXZ-Y29uZmVyZW5jZS1vbW5pYnVkci4LEgdQcm9maWxlIhFsbGUuY3NjQGdtYWlsLmNvbQwLEgpDb25mZXJlbmNlGAEM",
            "highlights": [
             "Morning session"
            ],
            "location": "Town gym",
            "speakers": [
             "Sara",
             "Jerry"
            ],
            "type": "WORKSHOP",
            "duration": "30"
           }

       -- Get All Sessions
           http://localhost:9080/_ah/api/conference/v1/getSessions GET
        
       -- Get Conference Sessions
           http://localhost:9080/_ah/api/conference/v1/getConferenceSessions POST
           Required: ConferenceKey
        
           Example payload:
           {
            "conferenceKey": "ahZkZXZ-Y29uZmVyZW5jZS1vbW5pYnVkci4LEgdQcm9maWxlIhFsbGUuY3NjQGdtYWlsLmNvbQwLEgpDb25mZXJlbmNlGAEM"
           }
        
       -- Get Conference Sessions by Type
           http://localhost:9080/_ah/api/conference/v1/getConferenceSessionsByType POST  
           Required: ConferenceKey, session type (from enum WORKSHOP, LECTURE, FORUM, KEYNOTE)
           
           Example payload:
           {
            "conferenceKey": "ahZkZXZ-Y29uZmVyZW5jZS1vbW5pYnVkci4LEgdQcm9maWxlIhFsbGUuY3NjQGdtYWlsLmNvbQwLEgpDb25mZXJlbmNlGAMM",
            "type": "LECTURE"
           }
        
        
       -- Get Conference Sessions by Speaker
           http://localhost:9080/_ah/api/conference/v1/getConferenceSessionsBySpeaker POST  
           Required: ConferenceKey, Speaker name
        
           Example payload:
           {
            "conferenceKey": "ahZkZXZ-Y29uZmVyZW5jZS1vbW5pYnVkci4LEgdQcm9maWxlIhFsbGUuY3NjQGdtYWlsLmNvbQwLEgpDb25mZXJlbmNlGAEM",
            "speakers": [
             "Jerry"
            ]
           }
        
       -- Get Sessions (in all conferences) by Location
           http://localhost:9080/_ah/api/conference/v1/getSessionsByLocation POST  
           Required: Location
        
           Example payload:
           {
            "location": "Marriott Rm 6"
           }
        
       -- Get Sessions (in all conferences) by Highlights
           http://localhost:9080/_ah/api/conference/v1/getSessionsByHighlights POST  
           Required: Highlights
        
           Example payload:
           {
            "highlights": [
             "Fram",
             "Drinks"
            ]
           }
        
       -- Add Session to Wish List
           http://localhost:9080/_ah/api/conference/v1/session/{sessionKey} POST
           Required: sessionKey
        
           Example url:
           http://localhost:9080/_ah/api/conference/v1/session/ahZkZXZ-Y29uZmVyZW5jZS1vbW5pYnVkchQLEgdTZXNzaW9uGICAgICAgIAJDA
           
       -- Get Sessions Wish List
           http://localhost:9080/_ah/api/conference/v1/sessions/wishlist GET
        
       -- Get Featured Speaker
           http://localhost:9080/_ah/api/conference/v1/conference/featured/get GET
        

#### Discussion

  TASK 1
  ------
  The application design for the Session entity's relation to a parent Conference evolved.
     Originally, I chose to create Session object independent of a parent entity.
     I was considering the complexity of queries, decorators and Json marshalling.
     A Json list of conferences would be more lightwieght with children session objects not included.
     Query execution time would be shorter since children sessions wouldn't be returned.
     Logic and decorators remained simple without referencing 'lazy loading' or 'transient' keywords.
     The drawback of this choice is that the logic to query or manage children entities is additional and must be defined by the developer.
     In summary, using an ancestor Conference entity to group like sessions could create a performance hit.
     However, I implemented an ancestor Conference entity for child sessions so to leverage --strong consistency--.
     Strong consistency allowed for _cacheFeaturedSpeaker() to acquire the latest session that had beed committed by _createSessionObject().
     Originally, the qurey result for a common speaker did not include the most recently added Session.
     I choose the ancestor approach to avoud 'eventual consistency' that takes an undertermined number of seconds to complete.

     

  TASK 3
  ------
  To have a complete Conference Central online application, other functionality is necessary.
      1) New Session indexes were prepared when the application was deployed to Google App Engine.
         I relied on the auto-generated index config file that was created as I completed functionality on localhost.
            Indexes prepared:
                conferenceKey +  speakers + title
 
      2) For instance, each day's schedule for a conference should be rendered on the web site.
         To accomplish this, a query can be executed that returns all of the sessions scheduled per a particular day.
            """Return conference session daily schedule."""
            # create query for all sessions in a 24 hour period
            confDate = datetime.datetime.date.strptime(request.confDate, '%Y-%m-%dT%H:%M:%S %Z')  #send midnight (00:00Z) for request conference date
            sessions = Session.query()
            sessions = sessions.filter(Session.startTime >= confDate) 
            sessions = sessions.filter(Session.startTime <= confDate + timedelta(hours=24)) 
            # return set of SessionForm objects
            return SessionForms(
                sessions=[self._copySessionToForm(sess, 'Daily Schedule') for sess in sessions]
            )

      3) Additionally, the attendee might query sessions per highlights or specific location.
         This can be used by the attendee to target  her specific interests or when a session location has changed or moved within the conference.
            """Return sessions by highlight or location."""
            # create query for sessions
            sessions = Session.query()
            sessions = sessions.filter(Session.highlights.IN(request.highlights)) 
                       OR
            sessions = sessions.filter(Session.location ==  request.location) 
            # return set of SessionForm objects
            return SessionForms(
                sessions=[self._copySessionToForm(sess, 'Daily Schedule') for sess in sessions]
            )

       4) When building NDB filters with 1+ criteria, the developer will need to take precautions since NDB filter logic is restrictive.
          Google DataStore disallows:
            - combining too many filters
            - using inequalities for multiple properties
            - combining an inequality with a sort order on a different property
            - substring matches
            - case-insensitive matches
          So, a combined filter of ndb.AND(Session.type != 'WORKSHOP', Session.startTime < 19) breaks the restriction of 1+ inequalities for 
          multiple properties. For instance the following 2 implementation(s) returns a BadRequestError(Only one inequality filter per query 
          is supported. Encountered both type and startTime):
               q = Session.query()
               q = q.filter(Session.type != 'WORKSHOP') OR Session.query(ndb.query.AND(Session.type != 'WORKSHOP', Session.startTime < event_time))
               q = q.filter(Session.startTime < 19)
                     --- OR ---
               Session.query(ndb.query.AND(Session.type != 'WORKSHOP', Session.startTime < event_time))
          A workaround requires changing the inequality comparison of "type != 'WORKSHOP'" to an equailty comparision of "Session.type.IN()":
               q = Session.query()
               q = q.filter(Session.type.IN(['LECTURE', 'FORUM', 'KEYNOTE']))
               q = q.filter(Session.startTime < 19)
          Other technical considerations that need to be resolved in order to accomplish this query are:
            - Implement a computed property for filtering session type in case-insensitive. The logic implememted so far for Conference-Omnibud
              assumes that the session type can only be chosen from a UI drop-down with all enumeration values capitalized.
            - Also, how the session start time is stored needs to be fully fleshed out. Currently, the session start time is stored as a 
              full date - this taccomadate retieving a daily conference schedule.
              It would be effecient to store the sessionDate and sessionStartTime separately, the sessionDate as a DateTime property, and startTime 
              as a simple integer. The integer would represent military time in the range 0000-2400. (i.e. 1830 can indicate 6:30 pm)
              This implementation would accomodate queries for sessions based on start time regardless of conference day.


