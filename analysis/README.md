# Analysis Pipeline

Analysis pipeline for examining political content exposure in YouTube recommendations.

## Quick Start

### 1. Set your database connection
```bash
set DATABASE_URL=postgresql://user:password@host/database
```

### 2. Run the analysis
```bash
python -m analysis.analyze
```

This will load data from your database, label political content, compute metrics, and generate figures and tables in `analysis/outputs/`.

## What Gets Generated

**Metrics:**
- Overall political exposure percentage
- Exposure by crawl depth (iterations 0-30)
- Exposure by recommendation position
- Top political videos and channels

**Outputs in `analysis/outputs/`:**
- PNG figures (300 DPI)
- CSV tables with metrics
- Labeled dataset (CSV and Parquet)

## Customization

### Change the labeling threshold

Edit `analyze.py` and modify `min_signals`:
- `min_signals=1` - Permissive (more videos labeled political)
- `min_signals=2` - Balanced (default)
- `min_signals=3` - Strict (fewer videos labeled political)

### Add known political channels

Edit `analyze.py`:
```python
norwegian_political_channels = [
    'UCxxxxxxxxxxxxxxxxxxxxxx',  # Channel ID
]
```

### Add political keywords

Edit `politcal_keywords.xml` to add keywords in your language.

## How Political Classification Works

Videos are scored 0-6 based on these signals:
1. Video category is "News & Politics"
2. Video has political topics from YouTube API
3. Channel has political topics
4. Title contains political keywords
5. Description contains political keywords
6. Tags contain political keywords

Videos with `signal_count >= min_signals` are labeled as political.

## Files

**Core pipeline:**
- `analyze.py` - Main script, run this
- `load_data.py` - Load data from database
- `political_labeling.py` - Classify videos as political
- `metrics.py` - Compute exposure metrics
- `visualizations.py` - Generate figures and tables

**Utilities:**
- `export_validation_sample.py` - Export sample for manual validation
- `manual_validation.py` - Manual validation workflow
- `calculate_metrics.py` - Calculate validation accuracy
- `politcal_keywords.xml` - Political keywords

## Using Modules Independently

```python
from analysis.load_data import get_labeled_dataset
from analysis.metrics import compute_exposure_summary
from analysis.visualizations import generate_all_visualizations

# Load data (uses cache if available)
df = get_labeled_dataset(min_signals=2, max_age_hours=24)

# Compute metrics and generate visualizations
summary = compute_exposure_summary(df)
generate_all_visualizations(summary, output_dir="analysis/outputs")
```

## Workflow Example

```bash
# Run analysis
python -m analysis.analyze

# Review outputs
cd analysis\outputs
dir

# Edit analyze.py if needed (add channels, change threshold)

# Re-run (uses cache, so it's fast)
python -m analysis.analyze
```

## Caching

The pipeline caches labeled datasets in `analysis/cache/` for 24 hours. To reload from database, delete the cache files.

## Validation (Optional)

To measure classification accuracy:

```bash
# Export sample for manual review
python -m analysis.export_validation_sample

# Open analysis/outputs/manual_validation_sample.csv
# Add 'human_evaluation' column with True/False labels

# Calculate accuracy
python -m analysis.calculate_metrics
```

## Output Files

**Figures:**
- `overall_exposure.png` - Political vs non-political content
- `exposure_by_iteration.png` - Trends across crawl depth
- `exposure_by_position.png` - Political content by rank
- `top_political_videos.png` - Most recommended political videos
- `top_political_channels.png` - Top political channels
- `exposure_by_run.png` - Comparison across runs

**Tables:**
- `table_overall_metrics.csv` - Summary statistics
- `table_iteration_metrics.csv` - Metrics by crawl depth
- `table_position_metrics.csv` - Metrics by rank
- `table_top_political_videos.csv` - Top videos
- `table_top_political_channels.csv` - Top channels

**Data:**
- `labeled_dataset.csv` - Full dataset with political labels
- `labeled_dataset.parquet` - Same data, Parquet format

## Understanding Results

The `labeled_dataset.csv` file contains:
- `is_political` - Final classification (True/False)
- `signal_count` - Number of signals (0-6)
- `signal_category`, `signal_topic`, `signal_channel_topic`, `signal_title`, `signal_description`, `signal_tags` - Individual signal flags

Check these columns to understand why videos were classified as political.

## Troubleshooting

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

**Database not set:**
```bash
set DATABASE_URL=your_connection_string
```

**Clear cache:**
```bash
del analysis\cache\*.parquet
```
