import pandas as pd
import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Set

logger = logging.getLogger(__name__)

_POLITICAL_KEYWORDS = None


def load_political_keywords_from_xml(xml_path: str = None) -> Set[str]:
    """
    Load political keywords from XML file.
    """
    if xml_path is None:
        xml_path = Path(__file__).parent / 'politcal_keywords.xml'

    tree = ET.parse(xml_path)
    root = tree.getroot()

    keywords = set()

    for language in root.findall('Language'):
        for keyword_elem in language.findall('Keyword'):
            keyword = keyword_elem.text
            if keyword:
                keywords.add(keyword.lower().strip())

    logger.info(f"Loaded {len(keywords)} political keywords from {xml_path}")
    return keywords


def get_political_keywords() -> Set[str]:
    """Get political keywords, loading them if not already loaded."""
    global _POLITICAL_KEYWORDS
    if _POLITICAL_KEYWORDS is None:
        _POLITICAL_KEYWORDS = load_political_keywords_from_xml()
    return _POLITICAL_KEYWORDS


POLITICAL_TOPIC_URLS = {
    'https://en.wikipedia.org/wiki/Politics',
    'https://en.wikipedia.org/wiki/Political_science',
    'https://en.wikipedia.org/wiki/Government',
    'https://en.wikipedia.org/wiki/Election',
    'https://en.wikipedia.org/wiki/Politician'
}

POLITICAL_CATEGORY_IDS = {25}


def contains_political_keywords(text: str, keywords: Set[str]) -> bool:
    if pd.isna(text) or not text:
        return False

    text_lower = text.lower()

    words = set(re.findall(r'\b\w+\b', text_lower))

    for keyword in keywords:
        if ' ' in keyword:
            if keyword in text_lower:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    return True
        else:
            if keyword in words:
                return True

    return False


def has_political_topic(topic_categories) -> bool:
    if topic_categories is None:
        return False

    if isinstance(topic_categories, float):
        return False

    if isinstance(topic_categories, (list, tuple)):
        if len(topic_categories) == 0:
            return False
        return any(topic in POLITICAL_TOPIC_URLS for topic in topic_categories)

    if isinstance(topic_categories, str):
        if not topic_categories:
            return False
        return any(topic in topic_categories for topic in POLITICAL_TOPIC_URLS)

    return False


def label_political_content(df: pd.DataFrame, min_signals: int = 2) -> pd.DataFrame:
    df = df.copy()

    # Get keywords (lazy load)
    keywords = get_political_keywords()

    # Signal 1: Category ID (News & Politics)
    df['signal_category'] = df['category_id'].isin(POLITICAL_CATEGORY_IDS)

    # Signal 2: Topic categories from YouTube API
    df['signal_topic'] = df['topic_categories'].apply(has_political_topic)

    # Signal 3: Channel topic categories
    if 'topic_categories_channel' in df.columns:
        df['signal_channel_topic'] = df['topic_categories_channel'].apply(has_political_topic)
    else:
        df['signal_channel_topic'] = False

    # Signal 4: Keywords in title
    df['signal_title'] = df['title'].apply(
        lambda x: contains_political_keywords(x, keywords)
    )

    # Signal 5: Keywords in description
    df['signal_description'] = df['description'].apply(
        lambda x: contains_political_keywords(x, keywords)
    )

    # Signal 6: Keywords in tags
    def check_tags(tags):
        if tags is None:
            return False
        if isinstance(tags, float):
            return False
        if isinstance(tags, list):
            if len(tags) == 0:
                return False
            tags_text = ' '.join(tags)
        else:
            tags_text = str(tags)
            if not tags_text:
                return False
        return contains_political_keywords(tags_text, keywords)

    df['signal_tags'] = df['tags'].apply(check_tags)

    # Combine signals into a score (0-6)
    signal_cols = ['signal_category', 'signal_topic', 'signal_channel_topic',
                  'signal_title', 'signal_description', 'signal_tags']
    df['signal_count'] = df[signal_cols].sum(axis=1)

    # Apply threshold: political if signal_count >= min_signals
    df['is_political'] = df['signal_count'] >= min_signals

    # Print summary statistics
    logger.info(f"\nPolitical Content Labeling Results:")
    logger.info(f"Threshold: min_signals = {min_signals}")
    logger.info(f"Keywords loaded: {len(keywords)}")
    logger.info(f"Total recommendations: {len(df):,}")
    logger.info(f"Political recommendations: {df['is_political'].sum():,} ({df['is_political'].mean()*100:.1f}%)")
    logger.info(f"\nSignal breakdown:")
    logger.info(f"  - Category (News & Politics): {df['signal_category'].sum():,}")
    logger.info(f"  - Topic categories: {df['signal_topic'].sum():,}")
    logger.info(f"  - Channel topics: {df['signal_channel_topic'].sum():,}")
    logger.info(f"  - Title keywords: {df['signal_title'].sum():,}")
    logger.info(f"  - Description keywords: {df['signal_description'].sum():,}")
    logger.info(f"  - Tag keywords: {df['signal_tags'].sum():,}")
    logger.info(f"\nSignal count distribution:")
    logger.info(f"\n{df['signal_count'].value_counts().sort_index().to_string()}")

    return df


def add_custom_political_labels(df: pd.DataFrame,
                                channel_ids: List[str] = None,
                                video_ids: List[str] = None) -> pd.DataFrame:
    """
    Manually label specific channels or videos as political.

    Useful for known political channels that might not trigger automated detection.
    """
    df = df.copy()

    if channel_ids:
        df.loc[df['channel_id'].isin(channel_ids), 'is_political'] = True
        logger.info(f"Manually labeled {len(channel_ids)} channels as political")

    if video_ids:
        df.loc[df['video_id'].isin(video_ids), 'is_political'] = True
        logger.info(f"Manually labeled {len(video_ids)} videos as political")

    return df


def compare_thresholds(df: pd.DataFrame, max_threshold: int = 4) -> pd.DataFrame:
    """
    Compare political content detection across different threshold values.

    Useful for sensitivity analysis and choosing the optimal threshold.
    """
    results = []

    for threshold in range(1, max_threshold + 1):
        is_political = df['signal_count'] >= threshold

        results.append({
            'threshold': threshold,
            'political_count': is_political.sum(),
            'political_percentage': is_political.mean() * 100,
            'unique_videos': df[is_political]['video_id'].nunique(),
        })

    comparison_df = pd.DataFrame(results)

    logger.info("\nThreshold Comparison:")
    logger.info(f"\n{comparison_df.to_string(index=False)}")

    return comparison_df


if __name__ == "__main__":
    #Just for some quick testing
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    from load_data import load_full_dataset

    df = load_full_dataset()

    logger.info("\n" + "="*80)
    logger.info("Testing min_signals = 1 (Liberal)")
    logger.info("="*80)
    df1 = label_political_content(df, min_signals=1)

    logger.info("\n" + "="*80)
    logger.info("Testing min_signals = 2 (Balanced - Recommended)")
    logger.info("="*80)
    df2 = label_political_content(df, min_signals=2)

    logger.info("\n" + "="*80)
    logger.info("Testing min_signals = 3 (Conservative)")
    logger.info("="*80)
    df3 = label_political_content(df, min_signals=3)

    logger.info("\n\nSample of political videos (threshold=2):")
    political = df2[df2['is_political']].drop_duplicates('video_id').head(10)
    logger.info(f"\n{political[['video_id', 'title', 'signal_count', 'signal_category', 'signal_topic', 'signal_title']].to_string()}")
