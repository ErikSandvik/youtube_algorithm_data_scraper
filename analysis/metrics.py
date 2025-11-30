import pandas as pd
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def compute_overall_exposure(df: pd.DataFrame) -> Dict[str, float]:
    total_recs = len(df)
    political_recs = df['is_political'].sum()

    political_df = df[df['is_political']]
    median_depth = political_df['iteration_rec'].median() if len(political_df) > 0 else 0
    mean_depth = political_df['iteration_rec'].mean() if len(political_df) > 0 else 0

    metrics = {
        'total_recommendations': total_recs,
        'political_recommendations': int(political_recs),
        'political_percentage': (political_recs / total_recs * 100) if total_recs > 0 else 0,
        'unique_videos': df['video_id'].nunique(),
        'unique_political_videos': df[df['is_political']]['video_id'].nunique(),
        'median_political_depth': median_depth,
        'mean_political_depth': mean_depth,
    }

    return metrics


def compute_exposure_by_iteration(df: pd.DataFrame) -> pd.DataFrame:
    iteration_stats = df.groupby('iteration_rec').agg({
        'is_political': ['sum', 'mean', 'count'],
        'video_id': 'nunique'
    }).reset_index()

    iteration_stats.columns = [
        'iteration',
        'political_count',
        'political_rate',
        'total_recommendations',
        'unique_videos'
    ]

    iteration_stats['political_percentage'] = iteration_stats['political_rate'] * 100

    return iteration_stats


def compute_exposure_by_position(df: pd.DataFrame, max_position: int = 20) -> pd.DataFrame:
    df_pos = df[df['position'].notna() & (df['position'] < max_position)].copy()

    position_stats = df_pos.groupby('position').agg({
        'is_political': ['sum', 'mean', 'count'],
        'video_id': 'nunique'
    }).reset_index()

    position_stats.columns = [
        'position',
        'political_count',
        'political_rate',
        'total_recommendations',
        'unique_videos'
    ]

    position_stats['political_percentage'] = position_stats['political_rate'] * 100

    return position_stats


def compute_exposure_by_run(df: pd.DataFrame) -> pd.DataFrame:
    run_stats = df.groupby('run_id').agg({
        'is_political': ['sum', 'mean', 'count'],
        'video_id': 'nunique',
        'iteration_rec': 'max'
    }).reset_index()

    run_stats.columns = [
        'run_id',
        'political_count',
        'political_rate',
        'total_recommendations',
        'unique_videos',
        'max_iteration'
    ]

    run_stats['political_percentage'] = run_stats['political_rate'] * 100

    return run_stats


def compute_top_political_videos(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    political_df = df[df['is_political']].copy()

    video_counts = political_df.groupby(['video_id', 'title', 'channel_title']).agg({
        'id': 'count',
        'iteration_rec': 'mean',
        'position': 'mean',
        'view_count': 'first',
        'category_name': 'first'
    }).reset_index()

    video_counts.columns = [
        'video_id', 'title', 'channel_title',
        'recommendation_count', 'avg_iteration', 'avg_position',
        'view_count', 'category'
    ]

    video_counts = video_counts.sort_values('recommendation_count', ascending=False).head(top_n)

    return video_counts


def compute_top_political_channels(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    political_df = df[df['is_political']].copy()

    channel_counts = political_df.groupby(['channel_id', 'channel_title']).agg({
        'video_id': 'nunique',
        'id': 'count',
        'iteration_rec': 'mean'
    }).reset_index()

    channel_counts.columns = [
        'channel_id', 'channel_title',
        'unique_videos', 'total_recommendations', 'avg_iteration'
    ]

    channel_counts = channel_counts.sort_values('total_recommendations', ascending=False).head(top_n)

    return channel_counts


def compute_exposure_summary(df: pd.DataFrame) -> Dict:
    logger.info("Computing exposure metrics...\n")

    summary = {
        'overall': compute_overall_exposure(df),
        'by_iteration': compute_exposure_by_iteration(df),
        'by_position': compute_exposure_by_position(df),
        'by_run': compute_exposure_by_run(df),
        'top_videos': compute_top_political_videos(df),
        'top_channels': compute_top_political_channels(df)
    }

    logger.info("=" * 60)
    logger.info("OVERALL EXPOSURE METRICS")
    logger.info("=" * 60)
    for key, value in summary['overall'].items():
        if isinstance(value, float):
            logger.info(f"{key}: {value:.2f}")
        else:
            logger.info(f"{key}: {value:,}")

    logger.info("\n" + "=" * 60)
    logger.info("EXPOSURE BY ITERATION")
    logger.info("=" * 60)
    logger.info(f"\n{summary['by_iteration'].to_string(index=False)}")

    logger.info("\n" + "=" * 60)
    logger.info("TOP 10 POLITICAL VIDEOS")
    logger.info("=" * 60)
    logger.info(f"\n{summary['top_videos'].head(10)[['title', 'recommendation_count', 'channel_title']].to_string(index=False)}")

    return summary
