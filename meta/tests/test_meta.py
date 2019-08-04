# -*- coding: utf-8 -*-


from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, TestCase, override_settings

from .. import settings as meta_settings
from ..views import Meta


class MetaObjectTestCase(TestCase):
    old = {}

    def setUp(self):
        super(MetaObjectTestCase, self).setUp()
        data = dict(
            SITE_TYPE=None,
            SITE_NAME=None,
            SITE_PROTOCOL=None,
            SITE_DOMAIN=None,
            INCLUDE_KEYWORDS=[],
            DEFAULT_KEYWORDS=[],
            USE_OG_PROPERTIES=False,
            IMAGE_URL='/static/',
            USE_TWITTER_PROPERTIES=False,
            USE_FACEBOOK_PROPERTIES=False,
            USE_GOOGLEPLUS_PROPERTIES=False,
            USE_TITLE_TAG=False,
            USE_SITES=False,
            DEFAULT_IMAGE=None,
        )
        self.old = {}
        for key, val in list(data.items()):
            self.old[key] = getattr(meta_settings, key)
            setattr(meta_settings, key, val)

    def tearDown(self):
        super(MetaObjectTestCase, self).tearDown()
        for key, val in list(self.old.items()):
            setattr(meta_settings, key, val)

    def test_defaults(self):
        m = Meta()
        self.assertEqual(m.title, None)
        self.assertEqual(m.og_title, None)
        self.assertEqual(m.gplus_title, None)
        self.assertEqual(m.twitter_title, None)
        self.assertEqual(m.description, None)
        self.assertEqual(m.extra_props, None)
        self.assertEqual(m.extra_custom_props, None)
        self.assertEqual(m.custom_namespace, None)
        self.assertEqual(m.keywords, [])
        self.assertEqual(m.url, None)
        self.assertEqual(m.image, None)
        self.assertEqual(m.object_type, None)
        self.assertEqual(m.site_name, None)
        self.assertEqual(m.twitter_site, None)
        self.assertEqual(m.twitter_creator, None)
        self.assertEqual(m.twitter_card, None)
        self.assertEqual(m.locale, None)
        self.assertEqual(m.facebook_app_id, None)
        self.assertEqual(m.use_og, False)
        self.assertEqual(m.use_sites, False)
        self.assertEqual(m.use_twitter, False)
        self.assertEqual(m.use_facebook, False)
        self.assertEqual(m.use_googleplus, False)
        self.assertEqual(m.fb_pages, '')
        self.assertEqual(m.og_app_id, '')
        self.assertEqual(m.use_title_tag, False)

    def test_set_keywords(self):
        m = Meta(keywords=['foo', 'bar'])
        self.assertEqual(m.keywords[0], 'foo')
        self.assertEqual(m.keywords[1], 'bar')

    def test_set_keywords_with_include(self):
        meta_settings.INCLUDE_KEYWORDS = ['baz']
        m = Meta(keywords=['foo', 'bar'])
        self.assertEqual(m.keywords[0], 'foo')
        self.assertEqual(m.keywords[1], 'bar')
        self.assertEqual(m.keywords[2], 'baz')

    def test_set_keywords_no_duplicate(self):
        m = Meta(keywords=['foo', 'foo', 'foo'])
        self.assertEqual(m.keywords[0], 'foo')
        self.assertEqual(len(m.keywords), 1)

    def test_pages_appid(self):
        meta_settings.FB_APPID = 'appid'
        m = Meta(fb_pages='fbpages')
        self.assertEqual(m.fb_pages, 'fbpages')
        self.assertEqual(m.og_app_id, 'appid')

        meta_settings.FB_PAGES = 'fbpages'
        m = Meta()
        self.assertEqual(m.fb_pages, 'fbpages')
        self.assertEqual(m.og_app_id, 'appid')

        meta_settings.FB_PAGES = ''
        meta_settings.FB_APPID = ''

    def test_set_keywords_with_defaults(self):
        meta_settings.DEFAULT_KEYWORDS = ['foo', 'bar']
        m = Meta()
        self.assertEqual(m.keywords[0], 'foo')
        self.assertEqual(m.keywords[1], 'bar')

    def test_set_namespaces(self):
        meta_settings.OG_NAMESPACES = ['foo', 'bar']
        m = Meta()
        self.assertEqual(m.custom_namespace[0], 'foo')
        self.assertEqual(m.custom_namespace[1], 'bar')
        meta_settings.OG_NAMESPACES = None

    def test_get_full_url_with_None(self):
        m = Meta()
        self.assertEqual(m.get_full_url(None), None)

    def test_get_full_url_with_full_url(self):
        m = Meta()
        self.assertEqual(
            m.get_full_url('http://example.com/foo'),
            'http://example.com/foo'
        )

    def test_get_full_url_without_protocol_will_raise(self):
        m = Meta()
        with self.assertRaises(ImproperlyConfigured):
            m.get_full_url('foo/bar')

    @override_settings(SITE_ID=None)
    def test_get_full_url_without_site_id_will_raise(self):
        meta_settings.USE_SITES = True
        meta_settings.SITE_PROTOCOL = 'http'
        m = Meta()
        with self.assertRaises(ImproperlyConfigured):
            m.get_full_url('foo/bar')

    @override_settings(SITE_ID=None)
    def test_get_full_url_without_site_id_with_request_will_not_raise(self):
        meta_settings.USE_SITES = True
        meta_settings.SITE_PROTOCOL = 'http'
        factory = RequestFactory()
        request = factory.get('/')
        Site.objects.create(domain=request.get_host())
        m = Meta(request=request)
        self.assertEqual(
            m.get_full_url('foo/bar'),
            'http://testserver/foo/bar'
        )

    def test_get_full_url_without_protocol_without_schema_will_raise(self):
        m = Meta()
        with self.assertRaises(ImproperlyConfigured):
            m.get_full_url('//foo.com/foo/bar')

    def test_get_full_url_without_domain_will_raise(self):
        meta_settings.SITE_PROTOCOL = 'http'
        m = Meta()
        with self.assertRaises(ImproperlyConfigured):
            m.get_full_url('foo/bar')

    def test_get_full_url_with_domain_and_protocol(self):
        meta_settings.SITE_PROTOCOL = 'https'
        meta_settings.SITE_DOMAIN = 'foo.com'
        m = Meta()
        self.assertEqual(
            m.get_full_url('foo/bar'),
            'https://foo.com/foo/bar'
        )

    def test_get_full_url_without_schema(self):
        meta_settings.SITE_PROTOCOL = 'https'
        m = Meta()
        self.assertEqual(
            m.get_full_url('//foo.com/foo/bar'),
            'https://foo.com/foo/bar'
        )

    def test_get_full_url_with_absolute_path(self):
        meta_settings.SITE_PROTOCOL = 'https'
        meta_settings.SITE_DOMAIN = 'foo.com'
        m = Meta()
        self.assertEqual(
            m.get_full_url('/foo/bar'),
            'https://foo.com/foo/bar'
        )

    def test_set_url(self):
        meta_settings.SITE_PROTOCOL = 'https'
        meta_settings.SITE_DOMAIN = 'foo.com'
        m = Meta(url='foo/bar')
        self.assertEqual(m.url, 'https://foo.com/foo/bar')

    def test_set_image_with_full_url(self):
        m = Meta(image='http://meta.example.com/image.gif')
        self.assertEqual(m.image, 'http://meta.example.com/image.gif')

    def test_set_image_with_absolute_path(self):
        meta_settings.SITE_PROTOCOL = 'https'
        meta_settings.SITE_DOMAIN = 'foo.com'
        m = Meta(image='/img/image.gif')
        self.assertEqual(m.image, 'https://foo.com/img/image.gif')

    def test_set_image_with_relative_path(self):
        meta_settings.SITE_PROTOCOL = 'https'
        meta_settings.SITE_DOMAIN = 'foo.com'
        m = Meta(image='img/image.gif')
        self.assertEqual(m.image, 'https://foo.com/static/img/image.gif')

    def test_set_image_with_image_url(self):
        meta_settings.SITE_PROTOCOL = 'https'
        meta_settings.SITE_DOMAIN = 'foo.com'
        meta_settings.IMAGE_URL = '/thumb/'
        m = Meta(image='img/image.gif')
        self.assertEqual(m.image, 'https://foo.com/thumb/img/image.gif')

    def test_set_image_with_default_image_url(self):
        meta_settings.SITE_PROTOCOL = 'https'
        meta_settings.SITE_DOMAIN = 'foo.com'
        meta_settings.IMAGE_URL = '/thumb/'
        meta_settings.DEFAULT_IMAGE = 'img/image.gif'
        m = Meta()
        self.assertEqual(m.image, 'https://foo.com/thumb/img/image.gif')

    def test_set_image_with_defaults(self):
        meta_settings.SITE_PROTOCOL = 'https'
        meta_settings.SITE_DOMAIN = 'foo.com'
        meta_settings.DEFAULT_IMAGE = 'img/image.gif'
        m = Meta()
        self.assertEqual(m.image, 'https://foo.com/static/img/image.gif')