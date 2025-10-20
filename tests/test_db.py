import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import get_session
from app.crud.video import get_video_by_id
from app.models.category import Category
from app.services.video_processing import process_and_insert_video_from_json
from sqlalchemy.orm import Session

API_RESPONSE = {
    'kind': 'youtube#videoListResponse',
    'etag': 'C70A969JmZxi4TOyVhgFGdo0Mfo',
    'items': [{
        'kind': 'youtube#video',
        'etag': 'IDwb3FDorpGTWkJXO0sX9-Fw8Gg',
        'id': 'lV_QcwbTlZU',
        'snippet': {
            'publishedAt': '2025-10-16T21:00:54Z',
            'channelId': 'UCnQC_G5Xsjhp9fEJKuIcrSw',
            'title': "They Weren't Supposed To See This",
            'description': 'Ben Shapiro breaks down Politico’s leaked “I Love Hitler” messages story...',
            'thumbnails': {},
            'channelTitle': 'Ben Shapiro',
            'tags': ['ben shapiro', 'daily wire', 'politics'],
            'categoryId': '25',
            'liveBroadcastContent': 'none',
            'defaultLanguage': 'en',
            'localized': {'title': "They Weren't Supposed To See This", 'description': '...'},
            'defaultAudioLanguage': 'en'
        },
        'contentDetails': {'duration': 'PT8M48S', 'dimension': '2d', 'definition': 'hd', 'caption': 'false', 'licensedContent': True, 'contentRating': {}, 'projection': 'rectangular'},
        'statistics': {'viewCount': '36369', 'likeCount': '1119', 'favoriteCount': '0', 'commentCount': '877'}
    }],
    'pageInfo': {'totalResults': 1, 'resultsPerPage': 1}
}


class TestDatabaseOperations(unittest.TestCase):
    session: Session
    video_item = API_RESPONSE['items'][0]
    video_id = video_item['id']

    @classmethod
    def setUpClass(cls):
        cls.session_context = get_session()
        cls.session = cls.session_context.__enter__()

        category_id = int(cls.video_item['snippet']['categoryId'])
        category_name = "News & Politics"

        test_category = cls.session.get(Category, category_id)
        if not test_category:
            cls.session.add(Category(id=category_id, name=category_name))
            cls.session.commit()

    @classmethod
    def tearDownClass(cls):
        cls.session_context.__exit__(None, None, None)

    def test_1_video_creation(self):
        process_and_insert_video_from_json(self.session, self.video_item)
        retrieved_video = get_video_by_id(self.session, self.video_id)

        self.assertIsNotNone(retrieved_video)
        self.assertEqual(retrieved_video.title, self.video_item['snippet']['title'])

    def test_2_video_update(self):
        update_item = self.video_item.copy()
        updated_title = "My Updated Test Video"
        update_item['snippet']['title'] = updated_title

        process_and_insert_video_from_json(self.session, update_item)
        updated_video = get_video_by_id(self.session, self.video_id)

        self.assertIsNotNone(updated_video)
        self.assertEqual(updated_video.title, updated_title)


if __name__ == "__main__":
    unittest.main()
