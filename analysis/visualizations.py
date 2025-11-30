import pandas as pd
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


sns.set_style("whitegrid")
sns.set_palette("Set2")


def setup_output_dir(output_dir: str = "analysis/outputs") -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def plot_overall_exposure(metrics: Dict, output_dir: Path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    categories = ['Non-Political', 'Political']
    values = [
        metrics['total_recommendations'] - metrics['political_recommendations'],
        metrics['political_recommendations']
    ]
    colors = ['#3498db', '#e74c3c']

    ax1.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')

    for i, val in enumerate(values):
        pct = (val / metrics['total_recommendations']) * 100
        ax1.text(i, val,
                f'{val:,}\n({pct:.1f}%)',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax1.set_ylabel('Number of Recommendations', fontsize=12)
    ax1.set_title('Political vs Non-Political Content', fontsize=13, fontweight='bold')
    ax1.set_ylim(0, max(values) * 1.15)

    depth_labels = ['Median Depth', 'Mean Depth']
    depth_values = [
        metrics.get('median_political_depth', 0),
        metrics.get('mean_political_depth', 0)
    ]

    ax2.bar(depth_labels, depth_values, color='#e74c3c', alpha=0.7, edgecolor='black')

    for i, val in enumerate(depth_values):
        ax2.text(i, val,
                f'{val:.2f}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax2.set_ylabel('Iteration Depth', fontsize=12)
    ax2.set_title('Political Content Recommendation Depth', fontsize=13, fontweight='bold')
    ax2.set_ylim(0, max(depth_values) * 1.2 if max(depth_values) > 0 else 1)
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_dir / 'overall_exposure.png', dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: overall_exposure.png")


def plot_exposure_by_iteration(df_iteration: pd.DataFrame, output_dir: Path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(df_iteration['iteration'], df_iteration['political_percentage'],
             marker='o', linewidth=2, markersize=8, color='#e74c3c')
    ax1.fill_between(df_iteration['iteration'], 0, df_iteration['political_percentage'],
                      alpha=0.3, color='#e74c3c')
    ax1.set_xlabel('Iteration (Crawl Depth)', fontsize=12)
    ax1.set_ylabel('Political Content (%)', fontsize=12)
    ax1.set_title('Political Exposure by Iteration', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(df_iteration['iteration'])

    ax2.bar(df_iteration['iteration'], df_iteration['total_recommendations'],
            color='#3498db', alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Iteration (Crawl Depth)', fontsize=12)
    ax2.set_ylabel('Total Recommendations', fontsize=12)
    ax2.set_title('Recommendation Volume by Iteration', fontsize=13, fontweight='bold')
    ax2.set_xticks(df_iteration['iteration'])

    plt.tight_layout()
    plt.savefig(output_dir / 'exposure_by_iteration.png', dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: exposure_by_iteration.png")


def plot_exposure_by_position(df_position: pd.DataFrame, output_dir: Path):
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar(df_position['position'], df_position['political_percentage'],
            color='#e74c3c', alpha=0.7, edgecolor='black')

    mean_pct = df_position['political_percentage'].mean()
    ax.axhline(y=mean_pct, color='#2c3e50', linestyle='--', linewidth=2,
               label=f'Mean: {mean_pct:.1f}%')

    ax.set_xlabel('Recommendation Position (0 = top)', fontsize=12)
    ax.set_ylabel('Political Content (%)', fontsize=12)
    ax.set_title('Political Exposure by Recommendation Position', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_dir / 'exposure_by_position.png', dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: exposure_by_position.png")


def plot_top_videos(df_videos: pd.DataFrame, output_dir: Path, top_n: int = 15):
    fig, ax = plt.subplots(figsize=(12, 8))

    df_plot = df_videos.head(top_n).copy()

    df_plot['title_short'] = df_plot['title'].apply(
        lambda x: x[:60] + '...' if len(x) > 60 else x
    )

    ax.barh(range(len(df_plot)), df_plot['recommendation_count'],
            color='#e74c3c', alpha=0.7, edgecolor='black')

    ax.set_yticks(range(len(df_plot)))
    ax.set_yticklabels(df_plot['title_short'], fontsize=9)
    ax.set_xlabel('Number of Recommendations', fontsize=12)
    ax.set_title(f'Top {top_n} Most Recommended Political Videos', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig(output_dir / 'top_political_videos.png', dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: top_political_videos.png")


def plot_top_channels(df_channels: pd.DataFrame, output_dir: Path, top_n: int = 15):
    fig, ax = plt.subplots(figsize=(12, 8))

    df_plot = df_channels.head(top_n).copy()

    ax.barh(range(len(df_plot)), df_plot['total_recommendations'],
            color='#9b59b6', alpha=0.7, edgecolor='black')

    ax.set_yticks(range(len(df_plot)))
    ax.set_yticklabels(df_plot['channel_title'], fontsize=9)
    ax.set_xlabel('Total Political Recommendations', fontsize=12)
    ax.set_title(f'Top {top_n} Channels by Political Content', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig(output_dir / 'top_political_channels.png', dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: top_political_channels.png")


def plot_run_comparison(df_runs: pd.DataFrame, output_dir: Path):
    if len(df_runs) < 2:
        logger.info("Skipping run comparison (only 1 run found)")
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    x_pos = range(len(df_runs))
    ax.bar(x_pos, df_runs['political_percentage'],
           color='#e74c3c', alpha=0.7, edgecolor='black')

    ax.set_xlabel('Run ID', fontsize=12)
    ax.set_ylabel('Political Content (%)', fontsize=12)
    ax.set_title('Political Exposure Across Crawl Runs', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([str(rid)[:8] + '...' for rid in df_runs['run_id']],
                       rotation=45, ha='right', fontsize=9)

    mean_pct = df_runs['political_percentage'].mean()
    ax.axhline(y=mean_pct, color='#2c3e50', linestyle='--', linewidth=2,
               label=f'Mean: {mean_pct:.1f}%')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_dir / 'exposure_by_run.png', dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: exposure_by_run.png")


def export_tables(summary: Dict, output_dir: Path):
    summary['by_iteration'].to_csv(
        output_dir / 'table_iteration_metrics.csv',
        index=False
    )
    logger.info(f"Saved: table_iteration_metrics.csv")

    summary['by_position'].to_csv(
        output_dir / 'table_position_metrics.csv',
        index=False
    )
    logger.info(f"Saved: table_position_metrics.csv")

    summary['top_videos'].to_csv(
        output_dir / 'table_top_political_videos.csv',
        index=False
    )
    logger.info(f"Saved: table_top_political_videos.csv")

    summary['top_channels'].to_csv(
        output_dir / 'table_top_political_channels.csv',
        index=False
    )
    logger.info(f"Saved: table_top_political_channels.csv")

    overall_df = pd.DataFrame([summary['overall']])
    overall_df.to_csv(
        output_dir / 'table_overall_metrics.csv',
        index=False
    )
    logger.info(f"Saved: table_overall_metrics.csv")


def generate_all_visualizations(summary: Dict, output_dir: str = "analysis/outputs"):
    output_path = setup_output_dir(output_dir)

    logger.info("\n" + "=" * 60)
    logger.info("GENERATING VISUALIZATIONS")
    logger.info("=" * 60 + "\n")


    plot_overall_exposure(summary['overall'], output_path)
    plot_exposure_by_iteration(summary['by_iteration'], output_path)
    plot_exposure_by_position(summary['by_position'], output_path)
    plot_top_videos(summary['top_videos'], output_path)
    plot_top_channels(summary['top_channels'], output_path)
    plot_run_comparison(summary['by_run'], output_path)

    logger.info("\n" + "=" * 60)
    logger.info("EXPORTING TABLES")
    logger.info("=" * 60 + "\n")


    export_tables(summary, output_path)

    logger.info("\n" + "=" * 60)
    logger.info(f"All outputs saved to: {output_path.absolute()}")
    logger.info("=" * 60)
