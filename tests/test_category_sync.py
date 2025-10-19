import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.base import Base
from app.models.category import Category
from app.models.video import Video
from app.services.category_sync import sync_categories_from_youtube
from app.db import get_session, DB_URL, engine as app_engine

MOCK_API_RESPONSE = {
    'items': [
        {'id': '1', 'snippet': {'title': 'Film & Animation'}},
        {'id': '2', 'snippet': {'title': 'Autos & Vehicles'}},
        {'id': '10', 'snippet': {'title': 'Music'}},
    ]
}

Base.metadata.bind = app_engine


class TestCategorySync(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.Session = sessionmaker(bind=app_engine)

    def setUp(self):
        self.session = self.Session()
        self.session.query(Video).delete()
        self.session.query(Category).delete()
        self.session.commit()

    def tearDown(self):
        self.session.close()

    @patch('app.services.category_sync.fetch_youtube_categories')
    def test_initial_sync_populates_db(self, mock_fetch_categories: MagicMock):
        mock_fetch_categories.return_value = MOCK_API_RESPONSE

        sync_categories_from_youtube(self.session)

        categories = self.session.query(Category).all()
        self.assertEqual(len(categories), 3)

        music_category = self.session.query(Category).filter_by(name="Music").one_or_none()
        self.assertIsNotNone(music_category)
        self.assertEqual(music_category.id, 10)

    @patch('app.services.category_sync.fetch_youtube_categories')
    def test_sync_is_idempotent(self, mock_fetch_categories: MagicMock):
        mock_fetch_categories.return_value = MOCK_API_RESPONSE

        sync_categories_from_youtube(self.session)
        count_after_first_run = self.session.query(Category).count()
        self.assertEqual(count_after_first_run, 3)

        sync_categories_from_youtube(self.session)

        count_after_second_run = self.session.query(Category).count()
        self.assertEqual(count_after_second_run, count_after_first_run)

if __name__ == '__main__':
    unittest.main()
