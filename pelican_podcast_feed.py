# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six
if not six.PY3:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse

from jinja2 import Markup
from pelican import signals
from pelican.writers import Writer
from pelican.generators import Generator
from pelican.utils import set_date_tzinfo
from feedgenerator import Rss201rev2Feed
from feedgenerator.django.utils.feedgenerator import rfc2822_date

ITEM_ELEMENTS = (
    'title',
    'itunes:author',
    'itunes:subtitle',
    'itunes:summary',
    'itunes:image',
    'enclosure',
    'guid',
    'pubDate',
    'itunes:duration',
    )

DEFAULT_ITEM_ELEMENTS = {}
for key in ITEM_ELEMENTS:
    DEFAULT_ITEM_ELEMENTS[key] = None


class PodcastFeed(Rss201rev2Feed):
    def __init__(self, *args, **kwargs):
        super(PodcastFeed, self).__init__(*args, **kwargs)

    def set_settings(self, settings):
        self.settings = settings

    def rss_attributes(self):
        attrs = super(PodcastFeed, self).root_attributes()
        attrs['xmlns:itunes'] = "http://www.itunes.com/dtds/podcast-1.0.dtd"
        attrs['version'] = '2.0'
        return attrs

    def add_root_elements(self, handler):
        super(PodcastFeed, self).add_root_elements(handler)
        if 'PODCAST_FEED_LANGUAGE' in self.settings:
            handler.addQuickElement(
                'language', self.settings['PODCAST_FEED_LANGUAGE']
                )

        if 'PODCAST_FEED_COPYRIGHT' in self.settings:
            handler.addQuickElement(
                'copyright', self.settings['PODCAST_FEED_COPYRIGHT']
                )

        if 'PODCAST_FEED_EXPLICIT' in self.settings:
            handler.addQuickElement(
                'itunes:explicit', self.settings['PODCAST_FEED_EXPLICIT']
                )

        if 'PODCAST_FEED_SUBTITLE' in self.settings:
            handler.addQuickElement(
                'itunes:subtitle', self.settings['PODCAST_FEED_SUBTITLE']
                )

        if 'PODCAST_FEED_AUTHOR' in self.settings:
            handler.addQuickElement(
                'itunes:author', self.settings['PODCAST_FEED_AUTHOR']
                )

        if 'PODCAST_FEED_SUMMARY' in self.settings:
            handler.addQuickElement(
                'itunes:summary', self.settings['PODCAST_FEED_SUMMARY']
                )

        if 'PODCAST_FEED_IMAGE' in self.settings:
            handler.addQuickElement(
                'itunes:image', attrs={
                    'href': self.settings['PODCAST_FEED_IMAGE']
                    }
                )

        if 'PODCAST_FEED_OWNER_NAME' in self.settings \
                and 'PODCAST_FEED_OWNER_EMAIL' in self.settings:
            handler.startElement('itunes:owner', {})
            handler.addQuickElement(
                'itunes:name', self.settings['PODCAST_FEED_OWNER_NAME']
                )
            handler.addQuickElement(
                'itunes:email', self.settings['PODCAST_FEED_OWNER_EMAIL']
                )
            handler.endElement('itunes:owner')

        if 'PODCAST_FEED_CATEGORY' in self.settings:
            categories = self.settings['PODCAST_FEED_CATEGORY']
            if type(categories) in (list, tuple):
                handler.startElement(
                    'itunes:category', attrs={'text': categories[0]}
                    )
                handler.addQuickElement(
                    'itunes:category', attrs={'text': categories[1]}
                    )
                handler.endElement('itunes:category')
            else:
                handler.addQuickElement(
                    'itunes:category', attrs={'text': categories}
                    )

    def add_item_elements(self, handler, item):
        for key in DEFAULT_ITEM_ELEMENTS:
            if item[key] is None:
                continue
            if type(item[key]) in (str, unicode):
                handler.addQuickElement(key, item[key])
            elif type(item[key]) is dict:
                handler.addQuickElement(key, attrs=item[key])
            else:
                print 'Ignoring', item[key]


class iTunesWriter(Writer):
    def __init__(self, *args, **kwargs):
        super(iTunesWriter, self).__init__(*args, **kwargs)

    def _create_new_feed(self, feed_type, context):
        self.context = context
        description = self.settings.get('PODCAST_FEED_SUMMARY', '')
        title = self.settings.get('PODCAST_FEED_TITLE', '') \
            or context['SITENAME']
        feed = PodcastFeed(
            title=title,
            link=(self.site_url + '/'),
            feed_url=None,
            description=description)
        feed.set_settings(self.settings)
        return feed

    def _add_item_to_the_feed(self, feed, item):
        items = DEFAULT_ITEM_ELEMENTS.copy()
        # Ex:
        #  http://example.com/episode-01
        items['link'] = '%s/%s' % (self.site_url, item.url)

        # Ex:
        #  <title>Episode Title</title>
        items['title'] = Markup(item.title).striptags()

        # Ex:
        #  <itunes:summary>In this episode... </itunes:summary>
        if hasattr(item, 'description'):
            items['itunes:summary'] = item.description
        else:
            items['itunes:summary'] = Markup(item.summary).striptags()
        items['description'] = items['itunes:summary']

        # Ex:
        #  <pubDate>Fri, 13 Jun 2014 04:59:00 -0300</pubDate>
        items['pubDate'] = rfc2822_date(
            set_date_tzinfo(
                item.modified if hasattr(item, 'modified') else item.date,
                self.settings.get('TIMEZONE', None))
            )

        # Ex:
        #  <itunes:author>John Doe</itunes:author>
        if hasattr(item, 'author'):
            items['itunes:author'] = item.author.name

        # Ex:
        #  <itunes:subtitle>My episode subtitle</itunes:subtitle>
        if hasattr(item, 'subtitle'):
            items['itunes:subtitle'] = Markup(item.subtitle).striptags()

        # Ex:
        #  <itunes:image href="http://example.com/Episodio1.jpg" />
        if hasattr(item, 'image'):
            items['itunes:image'] = {'href': self.site_url + item.image}

        # Ex:
        #  <enclosure url="http://example.com/episode.m4a"
        #   length="872731" type="audio/x-m4a" />
        if hasattr(item, 'podcast'):
            enclosure = {'url': item.podcast}
            if hasattr(item, 'length'):
                enclosure['length'] = item.length
            if hasattr(item, 'mimetype'):
                enclosure['type'] = item.mimetype
            else:
                enclosure['type'] = 'audio/mpeg'
            items['enclosure'] = enclosure

        # Ex:
        #  <itunes:duration>7:04</itunes:duration>
        if hasattr(item, 'duration'):
            items['itunes:duration'] = item.duration

        # Ex:
        #  <guid>http://example.com/aae20050615.m4a</guid>
        # Or:
        #  <guid>http://example.com/episode-01</guid>
        if hasattr(item, 'guid'):
            items['guid'] = item.guid
        else:
            items['guid'] = items['link']
        feed.add_item(**items)


class PodcastFeedGenerator(Generator):
    def __init__(self, *args, **kwargs):
        super(PodcastFeedGenerator, self).__init__(*args, **kwargs)
        self.episodes = []
        self.feed_path = self.settings.get('PODCAST_FEED_PATH', None)

    def generate_context(self):
        if self.feed_path:
            for article in self.context['articles']:
                if article.status.lower() == "published" \
                        and hasattr(article, 'podcast'):
                    self.episodes.append(article)

    def generate_output(self, writer):
        if self.feed_path:
            writer = iTunesWriter(self.output_path, self.settings)
            writer.write_feed(self.episodes, self.context, self.feed_path)


def get_generators(generators):
    return PodcastFeedGenerator


def register():
    signals.get_generators.connect(get_generators)
