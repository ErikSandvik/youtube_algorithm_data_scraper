import sys
import logging
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from analysis.load_data import get_labeled_dataset
from analysis.political_labeling import add_custom_political_labels
from analysis.metrics import compute_exposure_summary
from analysis.visualizations import generate_all_visualizations

logger = logging.getLogger(__name__)


def run_analysis(
    output_dir: str = "analysis/outputs",
    custom_political_channels: list = None,
    custom_political_videos: list = None,
    min_signals: int = 2
):
    logger.info("=" * 80)
    logger.info("YOUTUBE RECOMMENDATION POLITICAL CONTENT ANALYSIS")
    logger.info("=" * 80)

    logger.info("\n[Step 1/5] Loading and labeling data...")
    df = get_labeled_dataset(min_signals=min_signals, max_age_hours=24)

    if custom_political_channels or custom_political_videos:
        logger.info("\n[Step 2/5] Adding custom political labels...")
        df = add_custom_political_labels(
            df,
            channel_ids=custom_political_channels,
            video_ids=custom_political_videos
        )
    else:
        logger.info("\n[Step 2/5] No custom labels to add (skipping)")

    logger.info("\n[Step 3/5] Computing exposure metrics...")
    summary = compute_exposure_summary(df)

    logger.info("\n[Step 4/5] Generating visualizations and tables...")
    generate_all_visualizations(summary, output_dir=output_dir)

    logger.info("\n[Step 5/5] Saving final outputs...")
    output_path = Path(output_dir)
    df.to_csv(output_path / 'labeled_dataset.csv', index=False)
    df.to_parquet(output_path / 'labeled_dataset.parquet', index=False)
    logger.info(f"Saved: labeled_dataset.csv and labeled_dataset.parquet")

    logger.info("\n" + "=" * 80)
    logger.info("ANALYSIS COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"\nAll outputs saved to: {output_path.absolute()}")
    logger.info("\nGenerated files:")
    logger.info("  - Figures: overall_exposure.png, exposure_by_iteration.png, etc.")
    logger.info("  - Tables: table_*.csv files ready for LaTeX/papers")
    logger.info("  - Data: labeled_dataset.csv and labeled_dataset.parquet")

    return df, summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')


    political_channels = [
        # 'UCxxxxxxxxxxxxxxxxxxxxx',  # Example
    ]


    df, summary = run_analysis(
        output_dir="analysis/outputs",
        min_signals=2,  # Adjust this based on your validation results
        custom_political_channels=political_channels if political_channels else None
    )

    # Optional: Additional custom analysis
    logger.info("\n" + "=" * 80)
    logger.info("ADDITIONAL INSIGHTS")
    logger.info("=" * 80)

    # Example: Check if there are trends over time
    if 'collected_at' in df.columns:
        logger.info("\nRecommendations over time:")
        df['date'] = pd.to_datetime(df['collected_at']).dt.date
        daily_stats = df.groupby('date')['is_political'].agg(['sum', 'count', 'mean'])
        logger.info(f"\n{daily_stats.tail(10)}")
