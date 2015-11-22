#!/usr/bin/env python

"""
conference.py -- Udacity conference server-side Python App Engine API;
    uses Google Cloud Endpoints
created by levans on 2015 oct 16
"""
__author__ = 'Lyn Evans'


from datetime import datetime
from google.appengine.api import memcache

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models import ConflictException
from models import Profile
from models import ProfileMiniForm
from models import ProfileForm
from models import BooleanMessage
from models import Conference
from models import ConferenceForm
from models import ConferenceForms
from models import ConferenceQueryForm
from models import ConferenceQueryForms
from models import Session
from models import SessionForm
from models import SessionForms
from models import SessionType
from models import TeeShirtSize
from models import StringMessage

from utils import getUserId

from settings import WEB_CLIENT_ID

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
MEMCACHE_ANNOUNCEMENTS_KEY = "RECENT_ANNOUNCEMENTS"
MEMCACHE_FEATURED_SPEAKER_KEY = "FEATURED_SPEAKER"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

DEFAULTS = {
    "city": "Default City",
    "maxAttendees": 0,
    "seatsAvailable": 0,
    "topics": ["Default", "Topic"],
}

OPERATORS = {
            'EQ':   '=',
            'GT':   '>',
            'GTEQ': '>=',
            'LT':   '<',
            'LTEQ': '<=',
            'NE':   '!='
            }

FIELDS = {
         'CITY': 'city',
         'TOPIC': 'topics',
         'MONTH': 'month',
         'MAX_ATTENDEES': 'maxAttendees',
         }

CONF_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1),
)

CONF_POST_REQUEST = endpoints.ResourceContainer(
    ConferenceForm,
    websafeConferenceKey=messages.StringField(1),
)

SESS_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    sessionKey=messages.StringField(1),
)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@endpoints.api(name='conference',
               version='v1',
               allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
               scopes=[EMAIL_SCOPE])
class ConferenceApi(remote.Service):
    """Conference API v0.1"""
# - - - Conference objects - - - - - - - - - - - - - - - - -

    def _copyConferenceToForm(self, conf, displayName):
        """Copy relevant fields from Conference to ConferenceForm."""
        cf = ConferenceForm()
        for field in cf.all_fields():
            if hasattr(conf, field.name):
                # convert Date to date string; just copy others
                if field.name.endswith('Date'):
                    setattr(cf, field.name, str(getattr(conf, field.name)))
                else:
                    setattr(cf, field.name, getattr(conf, field.name))
            elif field.name == "websafeKey":
                setattr(cf, field.name, conf.key.urlsafe())
        if displayName:
            setattr(cf, 'organizerDisplayName', displayName)
        cf.check_initialized()
        return cf

    def _createConferenceObject(self, request):
        """Create or update Conference object,
           returning ConferenceForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        if not request.name:
            err = "Conference 'name' field required"
            raise endpoints.BadRequestException(err)

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}
        del data['websafeKey']
        del data['organizerDisplayName']

        # add default values for those missing
        # (both data model & outbound Message)
        for df in DEFAULTS:
            if data[df] in (None, []):
                data[df] = DEFAULTS[df]
                setattr(request, df, DEFAULTS[df])

        # convert dates from strings to Date objects;
        # set month based on start_date
        if data['startDate']:
            data['startDate'] = \
                datetime.strptime(data['startDate'][:10], "%Y-%m-%d").date()
            data['month'] = data['startDate'].month
        else:
            data['month'] = 0
        if data['endDate']:
            data['endDate'] = \
                datetime.strptime(data['endDate'][:10], "%Y-%m-%d").date()

        # set seatsAvailable to be same as maxAttendees on creation
        if data["maxAttendees"] > 0:
            data["seatsAvailable"] = data["maxAttendees"]
        # generate Profile Key based on user ID and Conference
        # ID based on Profile key get Conference key from ID
        p_key = ndb.Key(Profile, user_id)
        c_id = Conference.allocate_ids(size=1, parent=p_key)[0]
        c_key = ndb.Key(Conference, c_id, parent=p_key)
        data['key'] = c_key
        data['organizerUserId'] = request.organizerUserId = user_id

        # create Conference, send email to organizer confirming
        # creation of Conference & return (modified) ConferenceForm
        Conference(**data).put()
        # TODO 2: add confirmation email sending task to queue
        taskqueue.add(params={'email': user.email(),
                              'conferenceInfo': repr(request)},
                      url='/tasks/send_confirmation_email')

        return request

    def _createSessionObject(self, request):
        """Create Session object, returning SessionForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        if not request.title:
            err = "Session 'title' field required"
            raise endpoints.BadRequestException(err)

        if not request.conferenceKey:
            err = "Session 'conferenceKey' field required"
            raise endpoints.BadRequestException(err)

        try:
            conf = ndb.Key(urlsafe=request.conferenceKey).get()
            if not conf:
                raise endpoints.BadRequestException("Conference key invalid.")
        except:
            raise endpoints.BadRequestException("Conference key invalid.")

        if request.type:
            if str(request.type).upper() not in SessionType.to_dict().keys():
                err = "Session type invalid. Valid types are: " \
                    + str(SessionType.to_dict().keys())
                raise endpoints.BadRequestException(err)

        # copy SessionForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}
        try:
            if data['startTime']:
                data['startTime'] = \
                    datetime.strptime(data['startTime'], "%Y-%m-%d %H:%M")
        except:
            err = "Format start time YYYY-mm-dd HH:MM (24-hr military time)."
            raise endpoints.BadRequestException(err)

        data['type'] = data['type'].upper()
        del data['conferenceName']
        del data['conferenceCity']
        del data['conferenceDates']
        del data['websafeKey']

        # create Session
        Session(parent=ndb.Key(urlsafe=request.conferenceKey), **data).put()

        # check for featured speaker
        if request.speakers:
            q = Session.query(ancestor=ndb.Key(urlsafe=conf.key.urlsafe()))
            sessions = q.filter(Session.speakers.IN(data['speakers'])).fetch()
            # push a task to the queue only when speaker appears 1+
            # sessions in conference
            if len(sessions) > 1:
                # create speakers csv list to embed in post body
                speaker_param = ""
                for speaker in data['speakers']:
                    speaker_param += speaker + ","
                speaker_param = speaker_param[:len(speaker_param)-1]
                taskqueue.add(params={'speakers': speaker_param,
                                      'conferenceKey': data['conferenceKey']},
                              url='/tasks/set_featured_speaker')

        return request

    @ndb.transactional()
    def _updateConferenceObject(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}

        # update existing conference
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
        # check that conference exists
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s'
                % request.websafeConferenceKey)

        # check that user is owner
        if user_id != conf.organizerUserId:
            raise endpoints.ForbiddenException(
                'Only the owner can update the conference.')

        # Not getting all the fields, so don't create a new object; just
        # copy relevant fields from ConferenceForm to Conference object
        for field in request.all_fields():
            data = getattr(request, field.name)
            # only copy fields where we get data
            if data not in (None, []):
                # special handling for dates (convert string to Date)
                if field.name in ('startDate', 'endDate'):
                    data = datetime.strptime(data, "%Y-%m-%d").date()
                    if field.name == 'startDate':
                        conf.month = data.month
                # write to Conference object
                setattr(conf, field.name, data)
        conf.put()
        prof = ndb.Key(Profile, user_id).get()
        return self._copyConferenceToForm(conf, getattr(prof, 'displayName'))

    @endpoints.method(ConferenceForm,
                      ConferenceForm,
                      path='conference',
                      http_method='POST',
                      name='createConference')
    def createConference(self, request):
        """Create new conference."""
        return self._createConferenceObject(request)

    @endpoints.method(CONF_POST_REQUEST,
                      ConferenceForm,
                      path='conference/{websafeConferenceKey}',
                      http_method='PUT',
                      name='updateConference')
    def updateConference(self, request):
        """Update conference w/provided fields & return w/updated info."""
        return self._updateConferenceObject(request)

    @endpoints.method(CONF_GET_REQUEST,
                      ConferenceForm,
                      path='conference/{websafeConferenceKey}',
                      http_method='GET',
                      name='getConference')
    def getConference(self, request):
        """Return requested conference (by websafeConferenceKey)."""
        # get Conference object from request; bail if not found
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
        if not conf:
            raise endpoints.NotFoundException(
                 'No conference found with key: %s'
                 % request.websafeConferenceKey)
        prof = conf.key.parent().get()
        # return ConferenceForm
        return self._copyConferenceToForm(conf, getattr(prof, 'displayName'))

    @endpoints.method(message_types.VoidMessage,
                      ConferenceForms,
                      path='getConferencesCreated',
                      http_method='POST',
                      name='getConferencesCreated')
    def getConferencesCreated(self, request):
        """Return conferences created by user."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        # create ancestor query for all key matches for this user
        confs = Conference.query(ancestor=ndb.Key(Profile, user_id))
        prof = ndb.Key(Profile, user_id).get()
        # return set of ConferenceForm objects per Conference
        return ConferenceForms(
            conferences=[self._copyConferenceToForm(conf,
                         getattr(prof, 'displayName')) for conf in confs]
        )

    def _getQuery(self, request):
        """Return formatted query from the submitted filters."""
        q = Conference.query()
        inequality_filter, filters = self._formatFilters(request.filters)

        # If exists, sort on inequality filter first
        if not inequality_filter:
            q = q.order(Conference.name)
        else:
            q = q.order(ndb.GenericProperty(inequality_filter))
            q = q.order(Conference.name)

        for filtr in filters:
            if filtr["field"] in ["month", "maxAttendees"]:
                filtr["value"] = int(filtr["value"])
            formatted_query = ndb.query.FilterNode(filtr["field"],
                                                   filtr["operator"],
                                                   filtr["value"])
            q = q.filter(formatted_query)
        return q

    def _formatFilters(self, filters):
        """Parse, check validity and format user supplied filters."""
        formatted_filters = []
        inequality_field = None

        for f in filters:
            filtr = {field.name: getattr(f, field.name)
                     for field in f.all_fields()}

            try:
                filtr["field"] = FIELDS[filtr["field"]]
                filtr["operator"] = OPERATORS[filtr["operator"]]
            except KeyError:
                err = "Filter contains invalid field or operator."
                raise endpoints.BadRequestException(err)

            # Every operation except "=" is an inequality
            if filtr["operator"] != "=":
                # check if inequality operation has been used
                # in previous filters
                # disallow the filter if inequality was performed
                # on a different field before
                # track the field on which the inequality operation
                # is performed
                if inequality_field and inequality_field != filtr["field"]:
                    err = "Inequality filter is allowed on only one field."
                    raise endpoints.BadRequestException(err)
                else:
                    inequality_field = filtr["field"]

            formatted_filters.append(filtr)
        return (inequality_field, formatted_filters)

    @endpoints.method(ConferenceQueryForms,
                      ConferenceForms,
                      path='queryConferences',
                      http_method='POST',
                      name='queryConferences')
    def queryConferences(self, request):
        """Query for conferences."""
        conferences = self._getQuery(request)

        # need to fetch organiser displayName from profiles
        # get all keys and use get_multi for speed
        organisers = [(ndb.Key(Profile,
                      conf.organizerUserId)) for conf in conferences]
        profiles = ndb.get_multi(organisers)

        # put display names in a dict for easier fetching
        names = {}
        for profile in profiles:
            names[profile.key.id()] = profile.displayName

        # return individual ConferenceForm object per Conference
        return ConferenceForms(
                conferences=[self._copyConferenceToForm(conf,
                             names[conf.organizerUserId]) for conf in
                             conferences]
        )

# - - - Profile objects - - - - - - - - - - - - - - - - - - -
    def _copyProfileToForm(self, prof):
        """Copy relevant fields from Profile to ProfileForm."""
        # copy relevant fields from Profile to ProfileForm
        pf = ProfileForm()
        for field in pf.all_fields():
            if hasattr(prof, field.name):
                # convert t-shirt string to Enum; just copy others
                if field.name == 'teeShirtSize':
                    setattr(pf,
                            field.name,
                            getattr(TeeShirtSize, getattr(prof, field.name)))
                else:
                    setattr(pf, field.name, getattr(prof, field.name))
        pf.check_initialized()
        return pf

    def _getProfileFromUser(self):
        """Return user Profile from datastore,
           creating new one if non-existent."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # get Profile from datastore
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)
        profile = p_key.get()
        # create new Profile if not there
        if not profile:
            profile = Profile(
                key=p_key,
                displayName=user.nickname(),
                mainEmail=user.email(),
                teeShirtSize=str(TeeShirtSize.NOT_SPECIFIED),
            )
            profile.put()

        return profile      # return Profile

    def _doProfile(self, save_request=None):
        """Get user Profile and return to user, possibly updating it first."""
        # get user Profile
        prof = self._getProfileFromUser()

        # if saveProfile(), process user-modifyable fields
        if save_request:
            for field in ('displayName', 'teeShirtSize'):
                if hasattr(save_request, field):
                    val = getattr(save_request, field)
                    if val:
                        setattr(prof, field, str(val))
            prof.put()

        # return ProfileForm
        return self._copyProfileToForm(prof)

    @endpoints.method(message_types.VoidMessage,
                      ProfileForm,
                      path='profile',
                      http_method='GET',
                      name='getProfile')
    def getProfile(self, request):
        """Return user profile."""
        return self._doProfile()

    @endpoints.method(ProfileMiniForm,
                      ProfileForm,
                      path='profile',
                      http_method='POST',
                      name='saveProfile')
    def saveProfile(self, request):
        """Update & return user profile."""
        return self._doProfile(request)

# - - - Registration - - - - - - - - - - - - - - - - - - - -
    @ndb.transactional(xg=True)
    def _conferenceRegistration(self, request, reg=True):
        """Register or unregister user for selected conference."""
        retval = None
        prof = self._getProfileFromUser()  # get user Profile

        # check if conf exists given websafeConfKey
        # get conference; check that it exists
        wsck = request.websafeConferenceKey
        conf = ndb.Key(urlsafe=wsck).get()
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % wsck)

        # register
        if reg:
            # check if user already registered otherwise add
            if wsck in prof.conferenceKeysToAttend:
                raise ConflictException(
                    "You have already registered for this conference")

            # check if seats avail
            if conf.seatsAvailable <= 0:
                raise ConflictException(
                    "There are no seats available.")

            # register user, take away one seat
            prof.conferenceKeysToAttend.append(wsck)
            conf.seatsAvailable -= 1
            retval = True

        # unregister
        else:
            # check if user already registered
            if wsck in prof.conferenceKeysToAttend:

                # unregister user, add back one seat
                prof.conferenceKeysToAttend.remove(wsck)
                conf.seatsAvailable += 1
                retval = True
            else:
                retval = False

        # write things back to the datastore & return
        prof.put()
        conf.put()
        return BooleanMessage(data=retval)

    @endpoints.method(message_types.VoidMessage,
                      ConferenceForms,
                      path='conferences/attending',
                      http_method='GET',
                      name='getConferencesToAttend')
    def getConferencesToAttend(self, request):
        """Get list of conferences that user has registered for."""
        prof = self._getProfileFromUser()  # get user Profile
        conf_keys = [ndb.Key(urlsafe=wsck)
                     for wsck in prof.conferenceKeysToAttend]
        conferences = ndb.get_multi(conf_keys)

        # get organizers
        organisers = [ndb.Key(Profile, conf.organizerUserId)
                      for conf in conferences]
        profiles = ndb.get_multi(organisers)

        # put display names in a dict for easier fetching
        names = {}
        for profile in profiles:
            names[profile.key.id()] = profile.displayName

        # return set of ConferenceForm objects per Conference
        return ConferenceForms(
                 conferences=[self._copyConferenceToForm(conf,
                              names[conf.organizerUserId])
                              for conf in conferences])

    @endpoints.method(CONF_GET_REQUEST,
                      BooleanMessage,
                      path='conference/{websafeConferenceKey}',
                      http_method='POST',
                      name='registerForConference')
    def registerForConference(self, request):
        """Register user for selected conference."""
        return self._conferenceRegistration(request)

    @endpoints.method(CONF_GET_REQUEST,
                      BooleanMessage,
                      path='conference/{websafeConferenceKey}',
                      http_method='DELETE',
                      name='unregisterFromConference')
    def unregisterFromConference(self, request):
        """Unregister user for selected conference."""
        return self._conferenceRegistration(request, reg=False)

# - - - Announcements - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    def _cacheAnnouncement():
        """Create Announcement & assign to memcache; used by
        memcache cron job & putAnnouncement().
        """
        confs = Conference.query(ndb.AND(
            Conference.seatsAvailable <= 5,
            Conference.seatsAvailable > 0)
        ).fetch(projection=[Conference.name])

        if confs:
            # If there are almost sold out conferences,
            # format announcement and set it in memcache
            announcement = '%s %s' % (
                'Last chance to attend! The following conferences '
                'are nearly sold out:',
                ', '.join(conf.name for conf in confs))
            memcache.set(MEMCACHE_ANNOUNCEMENTS_KEY, announcement)
        else:
            # If there are no sold out conferences,
            # delete the memcache announcements entry
            announcement = ""
            memcache.delete(MEMCACHE_ANNOUNCEMENTS_KEY)

        return announcement

    @endpoints.method(message_types.VoidMessage,
                      StringMessage,
                      path='conference/announcement/get',
                      http_method='GET',
                      name='getAnnouncement')
    def getAnnouncement(self, request):
        """Return Announcement from memcache."""
        # TODO 1
        # return an existing announcement from Memcache or an empty string.
        announcement = memcache.get(MEMCACHE_ANNOUNCEMENTS_KEY)
        if not announcement:
            announcement = ""
        return StringMessage(data=announcement)

# --------------------- Sessions ---------------------
    def _copySessionToForm(self, sess, confName):
        """Copy relevant fields from Session to SessionForm."""
        sf = SessionForm()
        conf = ndb.Key(urlsafe=sess.conferenceKey).get()
        for field in sf.all_fields():
            if hasattr(sess, field.name) and field.name != 'startTime':
                setattr(sf, field.name, getattr(sess, field.name))
            elif field.name == "startTime":
                setattr(sf, field.name, str(getattr(sess, field.name)))
            elif field.name == "conferenceName":
                setattr(sf, field.name, conf.name)
            elif field.name == "conferenceCity":
                setattr(sf, field.name, conf.city)
            elif field.name == "conferenceDates":
                dates = ''
                if conf.startDate:
                    dates = str(conf.startDate) + " to "
                if conf.endDate:
                    dates += str(conf.endDate)
                setattr(sf, field.name, dates)
            elif field.name == "websafeKey":
                setattr(sf, field.name, sess.key.urlsafe())
        sf.check_initialized()
        return sf

    @ndb.transactional(xg=True)
    def _addToWishList(self, request, add=True):
        """Add session key to user wish list."""
        retval = None
        prof = self._getProfileFromUser()  # get user Profile

        # check if sess exists given websafeKey
        wsck = request.sessionKey
        sess = ndb.Key(urlsafe=wsck).get()
        if not sess:
            raise endpoints.NotFoundException(
                'No session found with key: %s' % wsck)
        # add
        if add:
            # check if session already in list
            if wsck in prof.sessionKeysWishList:
                raise ConflictException(
                    "You have already added this session.")

            # add session
            prof.sessionKeysWishList.append(wsck)
            retval = True

        # remove (not implemented)
        else:
            # check if session already added
            if wsck in prof.sessionKeysWishList:

                # remove session
                prof.sessionKeysWishList.remove(wsck)
                retval = True
            else:
                retval = False

        # write user profile object back to the datastore & return
        prof.put()
        return BooleanMessage(data=retval)

    @staticmethod
    def _cacheFeaturedSpeaker(request):
        """Compare speaker of new session and,
           if featured, push sessions to memcache"""

        # TODO: This logic pushes a single featured speaker onto the cache
        #      For 1+ speakers, concatenate a unique iterator to a contstant
        #      string tag or prefix to build the key(s)

        # Check for valid conference key in request
        try:
            conf = ndb.Key(urlsafe=request.get('conferenceKey')).get()
            if not conf:
                raise endpoints.BadRequestException("Conference key invalid.")
        except:
            raise endpoints.BadRequestException("Conference key invalid.")

        # Check for speakers appearing 1+ sessions in a conference
        q = Session.query(ancestor=ndb.Key(urlsafe=conf.key.urlsafe()))
        if (request.get('speakers')):
            speaker_list = request.get('speakers').split(",")
            for speaker in speaker_list:
                sessions = q.filter(Session.speakers.IN([speaker])).fetch()

                if len(sessions) > 1:
                    featured = {}
                    featured[str(speaker)] = []
                    for s in sessions:
                        featured[speaker].append(s.title)
                    memcache.set(MEMCACHE_FEATURED_SPEAKER_KEY, featured)

    @endpoints.method(SessionForm,
                      SessionForm,
                      path='session',
                      http_method='POST',
                      name='createSession')
    def createSession(self, request):
        """Create new session in a conference."""
        return self._createSessionObject(request)

    @endpoints.method(SessionForm,
                      SessionForms,
                      path='getConferenceSessionsByType',
                      http_method='POST',
                      name='getConferenceSessionsByType')
    def getConferenceSessionsByType(self, request):
        """Return conference sessions by type."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        conf = ''
        try:
            conf = ndb.Key(urlsafe=request.conferenceKey).get()
            if not conf:
                raise endpoints.NotFoundException(
                    'No conference found with key: %s' % request.conferenceKey)
        except:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.conferenceKey)

        # create query for all key matches for sessions by conference by type
        sess = Session.query()
        sess = sess.filter(Session.conferenceKey == request.conferenceKey)
        sess = sess.filter(Session.type == request.type)
        # return set of SessionForm objects per Conference
        return SessionForms(
            sessions=[self._copySessionToForm(se, getattr(conf, 'name'))
                      for se in sess]
        )

    @endpoints.method(SessionForm,
                      SessionForms,
                      path='getConferenceSessionsBySpeaker',
                      http_method='POST',
                      name='getConferenceSessionsBySpeaker')
    def getConferenceSessionsBySpeaker(self, request):
        """Return conference sessions by speaker."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        # create query for all key matches for sessions by speaker
        sessions = Session.query()
        sessions = sessions.filter(Session.speakers.IN(request.speakers))
        # return set of SessionForm objects per Conference
        return SessionForms(
            sessions=[self._copySessionToForm(sess, 'All')
                      for sess in sessions]
        )

    @endpoints.method(SessionForm,
                      SessionForms,
                      path='getDaytimeNonWorkshops',
                      http_method='POST',
                      name='getDaytimeNonWorkshops')
    def getMySessions(self, request):
        """Return sessions by complex query. """
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        # create query for all key matches for sessions by location
        event_time = datetime.strptime("2016-01-19 19:00", "%Y-%m-%d %H:%M")
        sesstypes = ['LECTURE', 'FORUM', 'KEYNOTE']
        sessions = Session.query()
        sessions = sessions.filter(Session.type.IN(sesstypes))
        sessions = sessions.filter(Session.startTime < event_time)
        # return set of SessionForm objects per Conference
        return SessionForms(
            sessions=[self._copySessionToForm(sess, 'By Complex Query')
                      for sess in sessions]
        )

    @endpoints.method(SessionForm,
                      SessionForms,
                      path='getSessionsByLocation',
                      http_method='POST',
                      name='getSessionsByLocation')
    def getSessionsByLocation(self, request):
        """Return sessions by location."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        # create query for all key matches for sessions by location
        sessions = Session.query()
        sessions = sessions.filter(Session.location == request.location)
        # return set of SessionForm objects per Conference
        return SessionForms(
            sessions=[self._copySessionToForm(sess, 'By Location')
                      for sess in sessions]
        )

    @endpoints.method(SessionForm,
                      SessionForms,
                      path='getSessionsByHighlights',
                      http_method='POST',
                      name='getSessionsByHighlights')
    def getSessionsByHighlights(self, request):
        """Return sessions by highlights."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        # create query for all key matches for sessions by highlights
        sessions = Session.query()
        sessions = sessions.filter(Session.highlights.IN(request.highlights))
        # return set of SessionForm objects per Conference
        return SessionForms(
            sessions=[self._copySessionToForm(sess, 'By Highlights')
                      for sess in sessions]
        )

    @endpoints.method(SessionForm,
                      SessionForms,
                      path='getConferenceSessions',
                      http_method='POST',
                      name='getConferenceSessions')
    def getConferenceSessions(self, request):
        """Return conference sessions."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        try:
            conf = ndb.Key(urlsafe=request.conferenceKey).get()
            if not conf:
                raise endpoints.NotFoundException(
                    'No conference found with key: %s' % request.conferenceKey)
        except:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.conferenceKey)
        # create query for all sessions by conference
        sess = Session.query()
        sess = sess.filter(Session.conferenceKey == request.conferenceKey)
        # return set of SessionForm objects per Conference
        return SessionForms(
            sessions=[self._copySessionToForm(se,
                      getattr(conf, 'name')) for se in sess]
        )

    @endpoints.method(message_types.VoidMessage,
                      SessionForms,
                      path='getSessions',
                      http_method='GET',
                      name='getSessions')
    def getSessions(self, request):
        """Return conference sessions."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        sess = Session.query()
        # return set of SessionForm objects per Conference
        return SessionForms(
            sessions=[self._copySessionToForm(se, 'testname') for se in sess]
        )

    @endpoints.method(SESS_GET_REQUEST,
                      BooleanMessage,
                      path='session/{sessionKey}',
                      http_method='POST',
                      name='addToWishList')
    def addSessionToWishList(self, request):
        """Add session to user's wish list"""
        return self._addToWishList(request)

    @endpoints.method(message_types.VoidMessage,
                      SessionForms,
                      path='sessions/wishlist',
                      http_method='GET',
                      name='getSessionsInWishList')
    def getSessionsInWishList(self, request):
        """Get list of session that user has selected."""
        prof = self._getProfileFromUser()  # get user Profile
        skeys = [ndb.Key(urlsafe=wsck) for wsck in prof.sessionKeysWishList]
        sessions = ndb.get_multi(skeys)

        # get conferences
        conf_keys = [ndb.Key(urlsafe=sess.conferenceKey) for sess in sessions]
        conferences = ndb.get_multi(conf_keys)

        # put display names in a dict for easier fetching
        names = {}
        for conf in conferences:
            names[conf.key.urlsafe()] = conf.name

        # return set of SessionForm objects
        return SessionForms(sessions=[self._copySessionToForm(sess,
                            names[sess.conferenceKey])
                            for sess in sessions])

    @endpoints.method(message_types.VoidMessage,
                      BooleanMessage,
                      path='clearWishList',
                      http_method='POST',
                      name='clearWishList')
    def clearWishList(self, request):
        """Clear session to user's wish list"""
        prof = self._getProfileFromUser()  # get user Profile
        prof.sessionKeysWishList = []
        prof.put()
        retval = True
        return BooleanMessage(data=retval)

    @endpoints.method(message_types.VoidMessage,
                      BooleanMessage,
                      path='clearFeaturedSpeaker',
                      http_method='POST',
                      name='clearFeaturedSpeaker')
    def clearSpeaker(self, request):
        """Clear feature speaker in memcache"""
        memcache.delete(MEMCACHE_FEATURED_SPEAKER_KEY)
        retval = True
        return BooleanMessage(data=retval)

    @endpoints.method(message_types.VoidMessage,
                      StringMessage,
                      path='conference/featured/get',
                      http_method='GET',
                      name='getFeaturedSpeaker')
    def getFeatured(self, request):
        """Return speaker from memcache."""
        # return a speaker from Memcache or an empty string.
        featured = memcache.get(MEMCACHE_FEATURED_SPEAKER_KEY)
        if not featured:
            featured = "none today"
        return StringMessage(data=str(featured))

api = endpoints.api_server([ConferenceApi])  # register API

