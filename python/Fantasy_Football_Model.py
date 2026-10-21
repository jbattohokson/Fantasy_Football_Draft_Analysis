#FANTASY FOOTBALL DRAFT ANALYSIS: PREDICTABILITY AND POSITIONAL VALUE
#Reads the SQL results in ../sql (Result<N>.csv = Query <N> in Fantasy_Football_MYSQL.sql)
#Analysis Period: 2021-2025 Seasons
#
#AUDITED 2026-10-21: rebuilt. The old version
#  * applied weekly PPR cutoffs (25/20/12 pts) to SEASON totals, so every
#    top-15 player at every position landed in "Elite",
#  * ranked "steals" by an end-of-season rank, which is circular,
#  * ranked consistency on raw season totals, so players who scored 0 every
#    year came out "most consistent",
#  * read columns (consistency, variance) the SQL no longer produced.
#Without ADP the data can't say who was mispriced on draft day. It can say
#which positions are predictable from one season to the next, how steeply
#value falls off by positional finish, and whether target share carries
#signal beyond last season's production. That's what this script answers.

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless: charts are only written to disk
import matplotlib.pyplot as plt
from scipy import stats

POSITIONS = ['QB', 'RB', 'WR', 'TE']
COLORS = {'QB': '#1f77b4', 'RB': '#ff7f0e', 'WR': '#2ca02c', 'TE': '#d62728'}
#12-team league starters: QB12, RB24, WR36 (incl. flex), TE12
STARTERS = {'QB': 12, 'RB': 24, 'WR': 36, 'TE': 12}

RESULT_FILES = {
    'position_summary': 'Result1.csv',
    'season_trends':    'Result2.csv',
    'multi_season':     'Result3.csv',
    'finishes':         'Result4.csv',
    'vor':              'Result5.csv',
    'pairs':            'Result6.csv',
    'all_seasons':      'Result7.csv',
}


def load_results(results_dir):
    missing = [f for f in RESULT_FILES.values() if not (results_dir / f).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing {missing} in {results_dir}. Run sql/load_raw_tables.py --sqlite and sql/run_sqlite.py first."
        )
    return {key: pd.read_csv(results_dir / f) for key, f in RESULT_FILES.items()}


def corr_with_ci(x, y):
    #Pearson r with a 95% CI (Fisher z). Returns (r, low, high, n, p)
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = ~(np.isnan(x) | np.isnan(y))
    x, y = x[ok], y[ok]
    n = len(x)
    if n < 4 or np.std(x) == 0 or np.std(y) == 0:
        return np.nan, np.nan, np.nan, n, np.nan
    r, p = stats.pearsonr(x, y)
    z, se = np.arctanh(r), 1 / np.sqrt(n - 3)
    return r, np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se), n, p


def position_predictability(pairs, finishes):
    """How well does a player's points per game predict his next season's? (qualifying seasons only)

    Two views per position:
      all players      every pair, backups to stars. The wide talent range inflates r.
      starters only    players who finished as a starter in season N (QB12/RB24/WR36/TE12),
                       the range a draft actually chooses from
    Pairs need 8+ games in BOTH seasons, so a starter who got hurt and missed the next
    season isn't counted. The drop rates are therefore a floor.
    """
    d = pairs.merge(finishes[['player_name', 'pos', 'yr', 'pos_finish']], on=['player_name', 'pos', 'yr'], how='left')
    rows = []
    for pos in POSITIONS:
        a = d[d['pos'] == pos]
        s = a[a['pos_finish'] <= STARTERS[pos]]
        r, lo, hi, n, p = corr_with_ci(a['ppg'], a['next_ppg'])
        rs, slo, shi, sn, _ = corr_with_ci(s['ppg'], s['next_ppg'])
        rows.append({'pos': pos, 'pairs': n, 'yoy_r': r, 'ci_low': lo, 'ci_high': hi,
                     'r_squared': r ** 2 if pd.notna(r) else np.nan, 'p_value': p,
                     'starter_pairs': sn, 'starter_yoy_r': rs, 'starter_ci_low': slo, 'starter_ci_high': shi,
                     'starter_avg_ppg_change': (s['next_ppg'] - s['ppg']).mean(),
                     'starter_share_dropping_20pct': ((s['next_ppg'] / s['ppg']) < 0.8).mean()})
    return pd.DataFrame(rows).sort_values('starter_yoy_r', ascending=False).reset_index(drop=True)


def target_share_signal(pairs):
    #WR/TE: does this season's target share predict next season's ppg, and does it add anything once ppg is known?
    import statsmodels.formula.api as smf
    rows = []
    for pos in ['WR', 'TE']:
        d = pairs[(pairs['pos'] == pos)].dropna(subset=['ppg', 'next_ppg', 'target_share'])
        r_share, *_ = corr_with_ci(d['target_share'], d['next_ppg'])
        r_ppg, *_ = corr_with_ci(d['ppg'], d['next_ppg'])
        base = smf.ols('next_ppg ~ ppg', data=d).fit()
        full = smf.ols('next_ppg ~ ppg + target_share', data=d).fit()
        rows.append({
            'pos': pos, 'pairs': len(d),
            'r_target_share_vs_next_ppg': r_share,
            'r_ppg_vs_next_ppg': r_ppg,
            'r2_ppg_only': base.rsquared,
            'r2_ppg_plus_share': full.rsquared,
            'share_coef_per_pct_pt': full.params['target_share'],
            'share_p_value': full.pvalues['target_share'],
        })
    return pd.DataFrame(rows)


def vor_by_finish(vor):
    #Average value over replacement for each positional finish, across seasons
    out = (vor.groupby(['pos', 'pos_finish'])['vor'].mean().reset_index()
           .rename(columns={'vor': 'avg_vor'}))
    return out[out['pos_finish'] <= 40]


def vor_summary(vor_curve):
    rows = []
    for pos in POSITIONS:
        c = vor_curve[vor_curve['pos'] == pos].set_index('pos_finish')['avg_vor']
        rows.append({'pos': pos, 'replacement_finish': STARTERS[pos],
                     'vor_finish_1': c.get(1), 'vor_finish_3': c.get(3), 'vor_finish_6': c.get(6),
                     'drop_1_to_6': c.get(1) - c.get(6)})
    return pd.DataFrame(rows).sort_values('vor_finish_3', ascending=False).reset_index(drop=True)


def consistent_starters(multi, finishes, min_seasons=3):
    #Most reliable among players who were actually starters: 3+ qualifying seasons and a career
    #average at or above the position's starter cutoff (the ppg of the last starter in an average season)
    q = finishes[finishes['games_played'] >= 8]
    cutoffs = {}
    for pos in POSITIONS:
        by_year = (q[q['pos'] == pos].sort_values('ppg', ascending=False)
                   .groupby('yr')['ppg'].apply(lambda s: s.iloc[STARTERS[pos] - 1] if len(s) >= STARTERS[pos] else np.nan))
        cutoffs[pos] = by_year.mean()
    m = multi[(multi['seasons'] >= min_seasons)].copy()
    m['starter_cutoff_ppg'] = m['pos'].map(cutoffs)
    m = m[m['avg_ppg'] >= m['starter_cutoff_ppg']]
    return m.sort_values(['pos', 'cv_ppg']).groupby('pos').head(5).reset_index(drop=True), cutoffs


def top_players(multi, n=5):
    return multi.sort_values(['pos', 'avg_ppg'], ascending=[True, False]).groupby('pos').head(n).reset_index(drop=True)


def plot_ppg_distribution(all_seasons, out):
    q = all_seasons[all_seasons['games_played'] >= 8]
    fig, ax = plt.subplots(figsize=(10, 6))
    data = [q.loc[q['pos'] == p, 'ppg'] for p in POSITIONS]
    bp = ax.boxplot(data, tick_labels=POSITIONS, patch_artist=True, showfliers=False)
    for patch, pos in zip(bp['boxes'], POSITIONS):
        patch.set_facecolor(COLORS[pos])
        patch.set_alpha(0.6)
    ax.set_ylabel('Points per game (PPR, no touchdowns)')
    ax.set_title('Per-game production by position, qualifying seasons (8+ games)', fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(out / '01_ppg_by_position.png', dpi=150)
    plt.close()


def plot_yoy(pairs, pred, out):
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    for ax, pos in zip(axes.flat, POSITIONS):
        d = pairs[pairs['pos'] == pos]
        row = pred.set_index('pos').loc[pos]
        ax.scatter(d['ppg'], d['next_ppg'], s=14, alpha=0.5, color=COLORS[pos])
        lim = max(d['ppg'].max(), d['next_ppg'].max()) * 1.05
        ax.plot([0, lim], [0, lim], color='grey', linewidth=0.8, linestyle='--')
        ax.set_xlim(0, lim)
        ax.set_ylim(0, lim)
        ax.set_title(f"{pos}: r = {row['yoy_r']:.2f} all, {row['starter_yoy_r']:.2f} starters (n = {int(row['pairs'])})", fontweight='bold')
        ax.set_xlabel('Points per game, season N')
        ax.set_ylabel('Points per game, season N+1')
        ax.grid(alpha=0.3)
    fig.suptitle('How well does this season predict next season?', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(out / '02_year_over_year_predictability.png', dpi=150)
    plt.close()


def plot_vor_curve(curve, out):
    fig, ax = plt.subplots(figsize=(11, 6))
    for pos in POSITIONS:
        c = curve[curve['pos'] == pos]
        ax.plot(c['pos_finish'], c['avg_vor'], marker='o', markersize=3, linewidth=2, label=pos, color=COLORS[pos])
    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_xlabel('Positional finish (1 = best at the position that season)')
    ax.set_ylabel('Season points above replacement (avg 2021-2025)')
    ax.set_title('Value over replacement by finish (replacement = QB12 / RB24 / WR36 / TE12)', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out / '03_value_over_replacement.png', dpi=150)
    plt.close()


def plot_target_share(pairs, signal, out):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, pos in zip(axes, ['WR', 'TE']):
        d = pairs[pairs['pos'] == pos].dropna(subset=['target_share', 'next_ppg'])
        r = signal.set_index('pos').loc[pos, 'r_target_share_vs_next_ppg']
        ax.scatter(d['target_share'], d['next_ppg'], s=14, alpha=0.5, color=COLORS[pos])
        ax.set_title(f'{pos}: target share vs next-season ppg (r = {r:.2f})', fontweight='bold')
        ax.set_xlabel('Share of team targets, season N (%)')
        ax.set_ylabel('Points per game, season N+1')
        ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out / '04_target_share_signal.png', dpi=150)
    plt.close()


def plot_top_players(top, out):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Highest points per game, 2+ qualifying seasons (PPR, no touchdowns)', fontsize=14, fontweight='bold')
    for ax, pos in zip(axes.flat, POSITIONS):
        d = top[top['pos'] == pos]
        ax.barh(d['player_name'], d['avg_ppg'], color=COLORS[pos], alpha=0.75, edgecolor='black')
        ax.set_title(f'Top 5 {pos}s', fontweight='bold')
        ax.set_xlabel('Average points per game')
        ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(out / '05_top_players.png', dpi=150)
    plt.close()


def key_findings(pred, signal, vsum, cutoffs):
    p = pred.set_index('pos')
    order = ', '.join(f"{pos} r={p.loc[pos, 'yoy_r']:.2f}" for pos in pred['pos'])
    v = vsum.set_index('pos')
    s = signal.set_index('pos')
    starters = ', '.join(f"{pos} r={p.loc[pos, 'starter_yoy_r']:.2f}" for pos in pred['pos'])
    drops = ', '.join(f"{pos} {p.loc[pos, 'starter_share_dropping_20pct']:.0%}" for pos in pred['pos'])
    lines = [
        f"1. Predictability (points per game, season N vs N+1), all players: {order}.",
        f"   Starters only (the range a draft picks from): {starters}.",
        f"   Starters lose {abs(pred['starter_avg_ppg_change'].max()):.1f}-{abs(pred['starter_avg_ppg_change'].min()):.1f} ppg on average the next season;",
        f"   share falling 20%+ (a floor; injured-out seasons aren't counted): {drops}.",
        "2. Value over replacement, avg season points above the last starter:",
        *[f"   {pos}: #1 finisher +{v.loc[pos, 'vor_finish_1']:.0f}, #3 +{v.loc[pos, 'vor_finish_3']:.0f}, "
          f"#6 +{v.loc[pos, 'vor_finish_6']:.0f}" for pos in vsum['pos']],
        "3. Target share (WR/TE):",
        *[f"   {pos}: r with next-season ppg {s.loc[pos, 'r_target_share_vs_next_ppg']:.2f}; adding it to last "
          f"season's ppg moves R^2 {s.loc[pos, 'r2_ppg_only']:.3f} -> {s.loc[pos, 'r2_ppg_plus_share']:.3f} "
          f"(p={s.loc[pos, 'share_p_value']:.3f})" for pos in ['WR', 'TE']],
        "4. Starter cutoffs (ppg of the last starter, avg season): "
        + ', '.join(f"{pos} {cutoffs[pos]:.1f}" for pos in POSITIONS),
        "Caveat: points exclude touchdowns (and QB rushing / RB receiving yards), so compare within a position.",
    ]
    return '\n'.join(lines)


def main():
    project_root = Path(__file__).resolve().parent.parent
    results = load_results(project_root / 'sql')
    out = project_root / 'python' / 'Outputs'
    out.mkdir(parents=True, exist_ok=True)

    print("FANTASY FOOTBALL DRAFT ANALYSIS")
    print(results['position_summary'].to_string(index=False))
    print()

    pairs = results['pairs']
    pred = position_predictability(pairs, results['finishes'])
    signal = target_share_signal(pairs)
    curve = vor_by_finish(results['vor'])
    vsum = vor_summary(curve)
    consistent, cutoffs = consistent_starters(results['multi_season'], results['finishes'])
    top = top_players(results['multi_season'])

    exports = {
        'position_predictability': pred,
        'target_share_signal': signal,
        'vor_by_finish': curve,
        'vor_summary': vsum,
        'consistent_starters': consistent,
        'top_players': top,
        'season_trends': results['season_trends'],
    }
    for name, df in exports.items():
        df.round(4).to_csv(out / f'{name}.csv', index=False)
        print(f"Saved: {name}.csv ({len(df)} rows)")

    plot_ppg_distribution(results['all_seasons'], out)
    plot_yoy(pairs, pred, out)
    plot_vor_curve(curve, out)
    plot_target_share(pairs, signal, out)
    plot_top_players(top, out)
    print("Saved: 01-05 charts")

    print("\nKEY FINDINGS")
    print(key_findings(pred, signal, vsum, cutoffs))
    print("\nMost reliable starters (3+ qualifying seasons, lowest season-to-season spread):")
    print(consistent[['pos', 'player_name', 'seasons', 'avg_ppg', 'cv_ppg']].to_string(index=False))
    print("\nAll output files saved to:", out)


if __name__ == "__main__":
    main()
