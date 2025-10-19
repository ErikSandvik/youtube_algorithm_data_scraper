import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import gather_recommendations_insert_into_db, is_video_data_valid
from app.models.base import Base
from app.models.video import Video
from app.models.category import Category
from app.db import engine as app_engine

MOCK_VIDEO_URLS = ["https://www.youtube.com/watch?v=test_video_id"]
MOCK_API_RESPONSE = {
    'items': [{
        'id': 'test_video_id',
        'snippet': {
            'publishedAt': '2025-10-19T21:00:00Z',
            'channelId': 'test_channel_id',
            'title': 'Integration Test Video',
            'description': 'A video for testing.',
            'tags': ['testing', 'python'],
            'categoryId': '28',
            'channelTitle': 'Test Channel',
        },
        'contentDetails': {'duration': 'PT5M'},
        'statistics': {'viewCount': '1000', 'likeCount': '100', 'commentCount': '10'}
    }]
}

class TestMainIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.Session = sessionmaker(bind=app_engine)

    def setUp(self):
        self.session = self.Session()
        self.session.query(Video).filter(Video.video_id == 'test_video_id').delete()
        self.session.query(Category).filter(Category.id == 28).delete()
        self.session.commit()

        self.session.add(Category(id=28, name="Science & Technology"))
        self.session.commit()

    def tearDown(self):
        self.session.query(Video).filter(Video.video_id == 'test_video_id').delete()
        self.session.query(Category).filter(Category.id == 28).delete()
        self.session.commit()
        self.session.close()

    @patch('app.main.process_and_insert_video_from_json')
    @patch('app.main.fetch_video_data_from_urls')
    @patch('app.main.run_yt_agent')
    def test_gather_recommendations_successful_run(
        self, mock_run_yt_agent, mock_fetch_data, mock_process_insert
    ):
        mock_run_yt_agent.return_value = MOCK_VIDEO_URLS
        mock_fetch_data.return_value = MOCK_API_RESPONSE

        gather_recommendations_insert_into_db(self.session, videos_to_click=1)

        mock_run_yt_agent.assert_called_once_with(headless=False, iterations=1)
        mock_fetch_data.assert_called_once_with(MOCK_VIDEO_URLS)

        mock_process_insert.assert_called_once()
        call_args = mock_process_insert.call_args[0]
        self.assertEqual(call_args[1]['id'], 'test_video_id')

    def test_is_video_data_valid(self):
        self.assertTrue(is_video_data_valid(MOCK_API_RESPONSE['items'][0]))

        self.assertFalse(is_video_data_valid(None))
        self.assertFalse(is_video_data_valid({}))
        self.assertFalse(is_video_data_valid({'id': '123'}))
        self.assertFalse(is_video_data_valid({'id': '123', 'snippet': {}}))

if __name__ == '__main__':
    unittest.main()
