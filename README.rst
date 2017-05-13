Pelican Podcast Feed
####################

This plugins adds a feed generator and feed writer for your podcast.

**Alert:** Still in early development stage.

Available Settings
==================

These are implemented as variables in the pelicanconf file.

::

  PODCAST_FEED_PATH = u''
  PODCAST_FEED_TITLE = u''
  PODCAST_FEED_EXPLICIT = u''
  PODCAST_FEED_LANGUAGE = u''
  PODCAST_FEED_COPYRIGHT = u''
  PODCAST_FEED_SUBTITLE = u''
  PODCAST_FEED_AUTHOR = u''
  PODCAST_FEED_SUMMARY = u''
  PODCAST_FEED_IMAGE = u''
  PODCAST_FEED_OWNER_NAME = u''
  PODCAST_FEED_OWNER_EMAIL = u''
  PODCAST_FEED_CATEGORY = ['iTunes Category','iTunes Subcategory']

Multiple Podcast Feeds
======================

You can optionally have a separate podcast feed for different content categories. To use this feature, you'll need to create a nested dictionary, called PODCASTS, with one sub dictionary for each category slug that you want to put into a separate podcast feed. (All of the episodes will continue to appear in the main feed as well, making it a master feed of all episodes.)

You can override specific configuration settings from the master feed. Everything that's not explicitly specified will be inherited from the master feed settings.

::

  PODCASTS = {
  	'category-slug-1': {
  		'PODCAST_FEED_PATH': u'',
  		'PODCAST_FEED_TITLE': u'',
  		'PODCAST_FEED_SUBTITLE': u'',
  		'PODCAST_FEED_SUMMARY': u'',
  		'PODCAST_FEED_IMAGE': u'',
  	},
  	'category-slug-2': {
  		'PODCAST_FEED_PATH': u'',
  		'PODCAST_FEED_TITLE': u'',
  		'PODCAST_FEED_SUBTITLE': u'',
  		'PODCAST_FEED_SUMMARY': u'',
  		'PODCAST_FEED_IMAGE': u'',
  	},
  }
