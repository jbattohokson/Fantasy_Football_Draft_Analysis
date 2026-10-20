#FANTASYPROS PPR FOOTBALL PYTHON ANALYSIS
#Data sourced from MySQL fantasy_football_combined table (Results 1-16)
#Analysis Period: 2021-2025 Seasons

from pathlib import Path
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

#Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

#PPR PERFORMANCE BENCHMARKS (Universal across all positions)
PPR_ELITE = 25          #Elite Performance: 25+ points
PPR_STARTER = 20        #Solid/Starter Quality: 12-20 points (threshold at 20)
PPR_FLEX = 12           #Flex/Average: 8-12 points (threshold at 12)
PPR_BELOW_AVG = 8       #Below Average: Under 8 points


def classify_ppr_tier(pts):
    #Classifies a player into a PPR performance tier based on average points.
    #Defined outside the loop so it is only created once.
    if pts >= PPR_ELITE:
        return 'Elite Performance (25+ pts)'
    elif pts >= PPR_STARTER:
        return 'Solid/Starter (20-24.9 pts)'
    elif pts >= PPR_FLEX:
        return 'Flex/Average (12-19.9 pts)'
    else:
        return 'Below Average (< 12 pts)'


if __name__ == "__main__":

    #Script lives in python/, SQL results live in sql/, outputs go to python/Outputs/
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    RESULTS_PATH = PROJECT_ROOT / "sql"
    OUTPUT_PATH = PROJECT_ROOT / "python" / "Outputs"
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    #SECTION 1: LOAD DATA FROM CSV FILES

    print("FANTASY FOOTBALL ANALYTICS - PYTHON ANALYSIS")
    print()
    print("Loading data from MySQL query results...")
    print()

    #Map each result key to its CSV path in the sql folder
    result_files = {
        'result_1':  RESULTS_PATH / 'Result1.csv',   #Draft Value Scoring Model
        'result_2':  RESULTS_PATH / 'Result2.csv',   #Fantasy Points by Position
        'result_3':  RESULTS_PATH / 'Result3.csv',   #Year-Over-Year Consistency
        'result_4':  RESULTS_PATH / 'Result4.csv',   #Top Performers (Multi-Year)
        'result_5':  RESULTS_PATH / 'Result5.csv',   #Top 5 QBs
        'result_6':  RESULTS_PATH / 'Result6.csv',   #Top 5 RBs
        'result_7':  RESULTS_PATH / 'Result7.csv',   #Top 5 WRs
        'result_8':  RESULTS_PATH / 'Result8.csv',   #Top 5 TEs
        'result_9':  RESULTS_PATH / 'Result9.csv',   #Position Predictability
        'result_10': RESULTS_PATH / 'Result10.csv',  #Player Consistency
        'result_11': RESULTS_PATH / 'Result11.csv',  #Draft Value Analysis
        'result_12': RESULTS_PATH / 'Result12.csv',  #Tier Classification
        'result_13': RESULTS_PATH / 'Result13.csv',  #Summary by Position
        'result_14': RESULTS_PATH / 'Result14.csv',  #Season Trends
        'result_15': RESULTS_PATH / 'Result15.csv',  #Complete Export Dataset
        'result_16': RESULTS_PATH / 'Result16.csv'   #Draft Value Scoring Model
    }

    #Load data — missing files are logged and skipped so the rest of the script can continue
    data = {}
    for key, filepath in result_files.items():
        try:
            data[key] = pd.read_csv(filepath)
            print(f"Loaded {filepath.name} ({len(data[key])} rows)")
        except FileNotFoundError:
            print(f"File not found: {filepath}")

    print()

    #SECTION 2: EXPLORATORY DATA ANALYSIS

    print("EXPLORATORY DATA ANALYSIS")
    print()

    #Result 2: Fantasy Points by Position
    print("Fantasy Points by Position (All Seasons):")
    print(data['result_2'])
    print()

    #Result 13: Summary by Position
    print("Summary Statistics by Position:")
    print(data['result_13'])
    print()

    #Result 14: Season Trends
    print("Season Trends (2021-2025):")
    print(data['result_14'].head(20))
    print()

    #SECTION 3: VISUALIZATION 1 FANTASY POINTS BY POSITION

    print("Creating visualization 1: Fantasy Points by Position...")

    fig, ax = plt.subplots(figsize=(10, 6))

    result_2 = data['result_2'].sort_values('avg_points', ascending=True)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    bars = ax.barh(result_2['position'], result_2['avg_points'], color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax.set_xlabel('Average Fantasy Points', fontsize=12, fontweight='bold')
    ax.set_ylabel('Position', fontsize=12, fontweight='bold')
    ax.set_title('Average Fantasy Points by Position (2021-2025)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')

    #Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height() / 2., f'{width:.1f}',
                ha='left', va='center', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH / '01_fantasy_points_by_position.png', dpi=300, bbox_inches='tight')
    print("Saved: 01_fantasy_points_by_position.png")
    plt.close()

    #SECTION 4: VISUALIZATION 2 SEASON TRENDS

    print("Creating visualization 2: Season Trends...")

    fig, ax = plt.subplots(figsize=(12, 7))

    result_14 = data['result_14']
    positions = result_14['pos'].unique()
    colors_pos = {'QB': '#1f77b4', 'RB': '#ff7f0e', 'WR': '#2ca02c', 'TE': '#d62728'}

    for pos in positions:
        pos_data = result_14[result_14['pos'] == pos].sort_values('yr')
        ax.plot(pos_data['yr'], pos_data['avg_pts'], marker='o', linewidth=2.5,
                markersize=8, label=pos, color=colors_pos.get(pos, '#1f77b4'))

    ax.set_xlabel('Season', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Fantasy Points', fontsize=12, fontweight='bold')
    ax.set_title('Fantasy Points Trends by Season and Position', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH / '02_season_trends.png', dpi=300, bbox_inches='tight')
    print("Saved: 02_season_trends.png")
    plt.close()

    #SECTION 5: VISUALIZATION 3 TOP PERFORMERS BY POSITION

    print("Creating visualization 3: Top Performers...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Top 5 Players by Position (Average Fantasy Points)', fontsize=16, fontweight='bold')

    #QB
    ax = axes[0, 0]
    qb_data = data['result_5'].head(5)
    ax.barh(qb_data['player_name'], qb_data['avg_points'], color='#1f77b4', alpha=0.7, edgecolor='black')
    ax.set_title('Top 5 QBs', fontsize=12, fontweight='bold')
    ax.set_xlabel('Average Fantasy Points')
    ax.invert_yaxis()

    #RB
    ax = axes[0, 1]
    rb_data = data['result_6'].head(5)
    ax.barh(rb_data['player_name'], rb_data['avg_points'], color='#ff7f0e', alpha=0.7, edgecolor='black')
    ax.set_title('Top 5 RBs', fontsize=12, fontweight='bold')
    ax.set_xlabel('Average Fantasy Points')
    ax.invert_yaxis()

    #WR
    ax = axes[1, 0]
    wr_data = data['result_7'].head(5)
    ax.barh(wr_data['player_name'], wr_data['avg_points'], color='#2ca02c', alpha=0.7, edgecolor='black')
    ax.set_title('Top 5 WRs', fontsize=12, fontweight='bold')
    ax.set_xlabel('Average Fantasy Points')
    ax.invert_yaxis()

    #TE
    ax = axes[1, 1]
    te_data = data['result_8'].head(5)
    ax.barh(te_data['player_name'], te_data['avg_points'], color='#d62728', alpha=0.7, edgecolor='black')
    ax.set_title('Top 5 TEs', fontsize=12, fontweight='bold')
    ax.set_xlabel('Average Fantasy Points')
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH / '03_top_performers.png', dpi=300, bbox_inches='tight')
    print("Saved: 03_top_performers.png")
    plt.close()

    #SECTION 6: VISUALIZATION 4 DRAFT VALUE BY ROUND

    print("Creating visualization 4: Draft Value Analysis...")

    fig, ax = plt.subplots(figsize=(12, 7))

    result_11 = data['result_11']
    qb_draft = result_11[result_11['pos'] == 'QB'].sort_values('avg_pts', ascending=False)

    x = np.arange(len(qb_draft))
    width = 0.35

    ax.bar(x - width / 2, qb_draft['avg_pts'], width, label='Average Points', color='steelblue', alpha=0.7, edgecolor='black')
    ax.bar(x + width / 2, qb_draft['std_dev'], width, label='Std Deviation', color='coral', alpha=0.7, edgecolor='black')

    ax.set_xlabel('Draft Round', fontsize=12, fontweight='bold')
    ax.set_ylabel('Fantasy Points', fontsize=12, fontweight='bold')
    ax.set_title('QB Draft Value by Round (Average Points & Variance)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(qb_draft['draft_round'])
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH / '04_draft_value_by_round.png', dpi=300, bbox_inches='tight')
    print("Saved: 04_draft_value_by_round.png")
    plt.close()

    #SECTION 7: VISUALIZATION 5 TIER DISTRIBUTION

    print("Creating visualization 5: Tier Distribution...")

    fig, ax = plt.subplots(figsize=(12, 7))

    result_12 = data['result_12']
    tier_counts = result_12.groupby('tier').size().sort_values(ascending=False)

    colors_tier = {
        'Elite (Top 3)':    '#2ecc71',
        'High Tier (4-10)': '#3498db',
        'Mid Tier (11-20)': '#f39c12',
        'Low Tier (21-30)': '#e74c3c',
        'Bench/Flex':       '#95a5a6'
    }

    bar_colors = [colors_tier.get(tier, '#1f77b4') for tier in tier_counts.index]
    bars = ax.bar(tier_counts.index, tier_counts.values, color=bar_colors, alpha=0.7, edgecolor='black', linewidth=2)

    ax.set_ylabel('Player Count', fontsize=12, fontweight='bold')
    ax.set_title('Player Distribution by Tier Classification', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    #Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH / '05_tier_distribution.png', dpi=300, bbox_inches='tight')
    print("Saved: 05_tier_distribution.png")
    plt.close()

    #SECTION 8: KEY INSIGHTS

    print()
    print("KEY INSIGHTS & FINDINGS")
    print()

    #Insight 1: Position Performance
    print("1. POSITION PERFORMANCE (Average Fantasy Points):")
    result_2_sorted = data['result_2'].sort_values('avg_points', ascending=False)
    for _, row in result_2_sorted.iterrows():
        print(f"   {row['position']}: {row['avg_points']:.2f} avg pts (std = {row['std_dev']:.2f})")
    print()

    #Insight 2: Top Players by Position
    print("2. ELITE PERFORMERS BY POSITION (5-Year Average):")
    result_4 = data['result_4']
    for pos in ['QB', 'RB', 'WR', 'TE']:
        pos_data = result_4[result_4['pos'] == pos].head(5)
        print(f"\n   {pos} - Top 5:")
        for idx, (_, row) in enumerate(pos_data.iterrows(), 1):
            print(f"      {idx}. {row['player_name']}: {row['avg_pts']:.1f} pts (Seasons: {int(row['seasons'])}, Consistency: {row['consistency']:.1f})")
    print()

    #Insight 3: Best Draft Values by Position
    print("3. BEST DRAFT VALUES (Elite Steals) BY POSITION:")
    result_1 = data['result_1']

    for pos in ['QB', 'RB', 'WR', 'TE']:
        pos_data = result_1[result_1['pos'] == pos]

        if len(pos_data) > 0:
            pos_steals = pos_data.nlargest(5, 'value_gained')
            print(f"\n   {pos} - Top 5 Steals:")
            for idx, (_, row) in enumerate(pos_steals.iterrows(), 1):
                print(f"      {idx}. {row['player_name']} (Yr {int(row['yr'])}): Rank {int(row['draft_rank'])}, Value +{row['value_gained']:.1f} pts, Score: {row['pts']:.1f}")
        else:
            print(f"\n   {pos} - No data found")
    print()

    #Insight 4: Most Consistent Players by Position
    print("4. MOST CONSISTENT PLAYERS BY POSITION (Lowest Variance):")
    result_10 = data['result_10'].dropna()
    for pos in ['QB', 'RB', 'WR', 'TE']:
        pos_consistent = result_10[result_10['pos'] == pos].nsmallest(5, 'variance')
        print(f"\n   {pos} - Top 5 Most Consistent:")
        if len(pos_consistent) > 0:
            for idx, (_, row) in enumerate(pos_consistent.iterrows(), 1):
                print(f"      {idx}. {row['player_name']}: {row['variance']:.1f} variance (Avg: {row['avg_pts']:.1f} pts)")
        else:
            print(f"      No data found for {pos}")
    print()

    #Insight 5: Season Trends by Position
    print("5. SEASON TRENDS - YEAR-OVER-YEAR CHANGES BY POSITION:")
    result_14_years = data['result_14']
    for pos in ['QB', 'RB', 'WR', 'TE']:
        pos_trends = result_14_years[result_14_years['pos'] == pos].sort_values('yr')
        print(f"\n   {pos} - 5-Year Trend:")
        if len(pos_trends) > 0:
            for _, row in pos_trends.iterrows():
                print(f"      {int(row['yr'])}: {row['avg_pts']:.1f} pts")
            yr_first = pos_trends.iloc[0]
            yr_last = pos_trends.iloc[-1]
            change = yr_last['avg_pts'] - yr_first['avg_pts']
            change_pct = (change / yr_first['avg_pts']) * 100 if yr_first['avg_pts'] != 0 else 0
            print(f"      Change: {change:+.1f} pts ({change_pct:+.1f}%)")
        else:
            print(f"      No data found for {pos}")
    print()

    #SECTION 9: CALCULATE PPR-BASED PERFORMANCE TIERS

    print("CALCULATING PPR-BASED PERFORMANCE TIERS FOR ALL EXPORTS")
    print()

    #ELITE STEALS: Players exceeding average with high points and value
    print("Calculating elite steals (high avg_pts + high value_gained)...")
    elite_steals_all = []

    result_1 = data['result_1']

    for pos in ['QB', 'RB', 'WR', 'TE']:
        pos_data = result_1[result_1['pos'] == pos]

        if len(pos_data) > 0:
            #Elite steals: high average performance + high value gained
            elite_steals = pos_data.nlargest(5, 'value_gained')
            elite_steals_all.append(elite_steals)
            print(f"  Found {len(elite_steals)} elite steals for {pos}")

    elite_steals_df = pd.concat(elite_steals_all, ignore_index=True)
    elite_steals_df = elite_steals_df.sort_values('value_gained', ascending=False)
    print(f"Total elite steals: {len(elite_steals_df)} (5 per position with highest value_gained)")
    print()

    #TOP PERFORMERS: High average fantasy points across seasons
    print("Calculating top performers (high average points + consistency)...")
    top_performers_all = []

    result_4 = data['result_4']

    for pos in ['QB', 'RB', 'WR', 'TE']:
        pos_data = result_4[result_4['pos'] == pos]

        if len(pos_data) > 0:
            #Top performers: highest avg pts (quality) + multiple seasons (consistency)
            top_performers = pos_data.nlargest(6, 'avg_pts')
            top_performers_all.append(top_performers)
            print(f"  Found {len(top_performers)} top performers for {pos} (avg_pts >= {top_performers['avg_pts'].min():.1f})")

    top_performers_df = pd.concat(top_performers_all, ignore_index=True)
    top_performers_df = top_performers_df.sort_values('avg_pts', ascending=False)
    print(f"Total top performers: {len(top_performers_df)} (6 per position - highest average scoring)")
    print()

    #CONSISTENT PLAYERS: Low variance (reliable, predictable scoring)
    print("Calculating consistent players (lowest variance = most reliable)...")
    consistent_all = []

    result_10 = data['result_10'].dropna()

    for pos in ['QB', 'RB', 'WR', 'TE']:
        pos_data = result_10[result_10['pos'] == pos]

        if len(pos_data) > 0:
            #Consistent players: lowest variance = most predictable week-to-week
            consistent = pos_data.nsmallest(5, 'variance')
            consistent_all.append(consistent)
            avg_pts_threshold = consistent['avg_pts'].min()
            print(f"  Found {len(consistent)} consistent players for {pos} (variance <= {consistent['variance'].max():.2f}, avg_pts >= {avg_pts_threshold:.1f})")

    consistent_players_df = pd.concat(consistent_all, ignore_index=True)
    consistent_players_df = consistent_players_df.sort_values('variance')
    print(f"Total consistent players: {len(consistent_players_df)} (5 per position - lowest variance)")
    print()

    #TIER CLASSIFICATION: PPR-based performance tiers (Elite, Starter, Flex, Below Avg)
    print("Calculating PPR-based tier classification...")
    print(f"  PPR Benchmarks:")
    print(f"    Elite Performance: {PPR_ELITE}+ points")
    print(f"    Solid/Starter: {PPR_STARTER}-{PPR_ELITE - 0.1} points")
    print(f"    Flex/Average: {PPR_FLEX}-{PPR_STARTER - 0.1} points")
    print(f"    Below Average: < {PPR_BELOW_AVG} points")
    print()

    tier_all_positions = []

    result_12 = data['result_12']

    for pos in ['QB', 'RB', 'WR', 'TE']:
        pos_data = result_12[result_12['pos'] == pos]

        if len(pos_data) > 0:
            #Get top performers per position (approximately top 12-15)
            top_tiers = pos_data.head(15).copy()

            #Apply PPR tier using the module-level classify_ppr_tier function
            top_tiers['ppr_tier'] = top_tiers['pts'].apply(classify_ppr_tier)
            tier_all_positions.append(top_tiers)

            elite_count   = len(top_tiers[top_tiers['pts'] >= PPR_ELITE])
            starter_count = len(top_tiers[(top_tiers['pts'] >= PPR_STARTER) & (top_tiers['pts'] < PPR_ELITE)])
            flex_count    = len(top_tiers[(top_tiers['pts'] >= PPR_FLEX) & (top_tiers['pts'] < PPR_STARTER)])
            below_count   = len(top_tiers[top_tiers['pts'] < PPR_BELOW_AVG])

            print(f"  {pos}: {elite_count} Elite | {starter_count} Starter | {flex_count} Flex | {below_count} Below Avg")

    tier_classification_df = pd.concat(tier_all_positions, ignore_index=True)
    tier_classification_df = tier_classification_df.sort_values('pts', ascending=False)
    print(f"Total players classified: {len(tier_classification_df)} across all positions with PPR tiers")
    print()

    #SECTION 10: EXPORT ANALYSIS SUMMARY

    print("EXPORTING ANALYSIS SUMMARY")
    print()

    #Export key results with PPR-based logic applied to all positions
    export_results = {
        'fantasy_points_by_position': data['result_2'],
        'top_performers':             top_performers_df,
        'draft_value_analysis':       data['result_11'],
        'tier_classification':        tier_classification_df,
        'position_summary':           data['result_13'],
        'season_trends':              data['result_14'],
        'elite_steals':               elite_steals_df,
        'consistent_players':         consistent_players_df
    }

    for export_name, export_df in export_results.items():
        filepath = OUTPUT_PATH / f'{export_name}_analysis.csv'
        export_df.to_csv(filepath, index=False)
        print(f"Saved: {export_name}_analysis.csv ({len(export_df)} rows)")

    print()
    print("ANALYSIS COMPLETE!")
    print()
    print("Generated visualizations:")
    print("  01_fantasy_points_by_position.png")
    print("  02_season_trends.png")
    print("  03_top_performers.png")
    print("  04_draft_value_by_round.png")
    print("  05_tier_distribution.png")
    print()
    print("Generated analysis exports (with PPR-based logic):")
    for export_name in export_results.keys():
        print(f"  {export_name}_analysis.csv ({len(export_results[export_name])} rows)")
    print()
    print("PPR PERFORMANCE BENCHMARKS APPLIED:")
    print(f"  Elite Performance: {PPR_ELITE}+ points (winning performances)")
    print(f"  Solid/Starter: {PPR_STARTER}-{PPR_ELITE - 0.1} points (dependable starters)")
    print(f"  Flex/Average: {PPR_FLEX}-{PPR_STARTER - 0.1} points (weekly flex plays)")
    print(f"  Below Average: < {PPR_BELOW_AVG} points (benchmarked or injuries)")
    print()
    print("All output files saved to:", OUTPUT_PATH)
