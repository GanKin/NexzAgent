"""
市场概览数据服务

数据导入（UPSERT）、上传历史查询、可用日期查询、文件名解析。
"""

import os
import re
from typing import Dict, List, Optional, Tuple

from app.utils.db import get_db_connection
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 文件名正则：匹配日期和数据类型
_DATE_RE = re.compile(r'(\d{2})-(\d{2})-(\d{2})')
_TYPE_MAP = {
    '美股市场': 'us_market',
    '核心数据集': 'core',
    '押注工具': 'betting_tool',
}
_TYPE_RE = re.compile(r'（(.*?)）.*?(?:（|$)')


class MarketOverviewService:
    """市场概览数据服务"""

    # UPSERT SQL：INSERT ON CONFLICT DO UPDATE
    _UPSERT_SQL = """
        INSERT INTO market_overview_data (
            data_date, symbol, name, data_type,
            relative_strength, strength_momentum, early_reversal,
            relative_price_status, relative_price_duration, relative_price_return,
            prev_relative_price_status, prev_relative_price_duration,
            d_trend, d_trend_duration,
            w_trend, w_trend_duration,
            m_trend, m_trend_duration,
            price_position_60d,
            leverage_status, leverage_duration, leverage_return,
            prev_leverage_status, leverage_value, leverage_change
        ) VALUES (
            %(data_date)s, %(symbol)s, %(name)s, %(data_type)s,
            %(relative_strength)s, %(strength_momentum)s, %(early_reversal)s,
            %(relative_price_status)s, %(relative_price_duration)s, %(relative_price_return)s,
            %(prev_relative_price_status)s, %(prev_relative_price_duration)s,
            %(d_trend)s, %(d_trend_duration)s,
            %(w_trend)s, %(w_trend_duration)s,
            %(m_trend)s, %(m_trend_duration)s,
            %(price_position_60d)s,
            %(leverage_status)s, %(leverage_duration)s, %(leverage_return)s,
            %(prev_leverage_status)s, %(leverage_value)s, %(leverage_change)s
        )
        ON CONFLICT (data_date, symbol) DO UPDATE SET
            name = EXCLUDED.name,
            data_type = EXCLUDED.data_type,
            relative_strength = EXCLUDED.relative_strength,
            strength_momentum = EXCLUDED.strength_momentum,
            early_reversal = EXCLUDED.early_reversal,
            relative_price_status = EXCLUDED.relative_price_status,
            relative_price_duration = EXCLUDED.relative_price_duration,
            relative_price_return = EXCLUDED.relative_price_return,
            prev_relative_price_status = EXCLUDED.prev_relative_price_status,
            prev_relative_price_duration = EXCLUDED.prev_relative_price_duration,
            d_trend = EXCLUDED.d_trend,
            d_trend_duration = EXCLUDED.d_trend_duration,
            w_trend = EXCLUDED.w_trend,
            w_trend_duration = EXCLUDED.w_trend_duration,
            m_trend = EXCLUDED.m_trend,
            m_trend_duration = EXCLUDED.m_trend_duration,
            price_position_60d = EXCLUDED.price_position_60d,
            leverage_status = EXCLUDED.leverage_status,
            leverage_duration = EXCLUDED.leverage_duration,
            leverage_return = EXCLUDED.leverage_return,
            prev_leverage_status = EXCLUDED.prev_leverage_status,
            leverage_value = EXCLUDED.leverage_value,
            leverage_change = EXCLUDED.leverage_change,
            updated_at = NOW()
    """

    def import_data(
        self,
        data_date: str,
        data_type: str,
        records: List[Dict],
        admin_id: int,
        filename: str,
        file_path: str,
    ) -> Dict:
        """
        批量导入数据（UPSERT 模式）。

        使用 INSERT ... ON CONFLICT (data_date, symbol) DO UPDATE。
        通过 xmax 系统列区分新增（xmax=0）和更新（xmax>0）。

        Returns:
            {total, new_rows, updated_rows, upload_id}
        """
        upload_id = None

        try:
            with get_db_connection() as conn:
                cur = conn.cursor()

                # 1. 创建 upload 记录
                cur.execute(
                    """
                    INSERT INTO market_overview_uploads
                        (filename, data_date, data_type, status, admin_id, file_path)
                    VALUES (%s, %s, %s, 'processing', %s, %s)
                    RETURNING id
                    """,
                    (filename, data_date, data_type, admin_id, file_path),
                )
                upload_id = cur.fetchone()[0]
                conn.commit()

                # 2. 逐行 UPSERT
                new_rows = 0
                updated_rows = 0
                total = 0

                for record in records:
                    record['data_date'] = data_date
                    record['data_type'] = data_type

                    cur.execute(
                        """
                        INSERT INTO market_overview_data (
                            data_date, symbol, name, data_type,
                            relative_strength, strength_momentum, early_reversal,
                            relative_price_status, relative_price_duration, relative_price_return,
                            prev_relative_price_status, prev_relative_price_duration,
                            d_trend, d_trend_duration,
                            w_trend, w_trend_duration,
                            m_trend, m_trend_duration,
                            price_position_60d,
                            leverage_status, leverage_duration, leverage_return,
                            prev_leverage_status, leverage_value, leverage_change
                        ) VALUES (
                            %(data_date)s, %(symbol)s, %(name)s, %(data_type)s,
                            %(relative_strength)s, %(strength_momentum)s, %(early_reversal)s,
                            %(relative_price_status)s, %(relative_price_duration)s, %(relative_price_return)s,
                            %(prev_relative_price_status)s, %(prev_relative_price_duration)s,
                            %(d_trend)s, %(d_trend_duration)s,
                            %(w_trend)s, %(w_trend_duration)s,
                            %(m_trend)s, %(m_trend_duration)s,
                            %(price_position_60d)s,
                            %(leverage_status)s, %(leverage_duration)s, %(leverage_return)s,
                            %(prev_leverage_status)s, %(leverage_value)s, %(leverage_change)s
                        )
                        ON CONFLICT (data_date, symbol) DO UPDATE SET
                            name = EXCLUDED.name,
                            data_type = EXCLUDED.data_type,
                            relative_strength = EXCLUDED.relative_strength,
                            strength_momentum = EXCLUDED.strength_momentum,
                            early_reversal = EXCLUDED.early_reversal,
                            relative_price_status = EXCLUDED.relative_price_status,
                            relative_price_duration = EXCLUDED.relative_price_duration,
                            relative_price_return = EXCLUDED.relative_price_return,
                            prev_relative_price_status = EXCLUDED.prev_relative_price_status,
                            prev_relative_price_duration = EXCLUDED.prev_relative_price_duration,
                            d_trend = EXCLUDED.d_trend,
                            d_trend_duration = EXCLUDED.d_trend_duration,
                            w_trend = EXCLUDED.w_trend,
                            w_trend_duration = EXCLUDED.w_trend_duration,
                            m_trend = EXCLUDED.m_trend,
                            m_trend_duration = EXCLUDED.m_trend_duration,
                            price_position_60d = EXCLUDED.price_position_60d,
                            leverage_status = EXCLUDED.leverage_status,
                            leverage_duration = EXCLUDED.leverage_duration,
                            leverage_return = EXCLUDED.leverage_return,
                            prev_leverage_status = EXCLUDED.prev_leverage_status,
                            leverage_value = EXCLUDED.leverage_value,
                            leverage_change = EXCLUDED.leverage_change,
                            updated_at = NOW()
                        RETURNING xmax
                        """,
                        record,
                    )
                    xmax = cur.fetchone()[0]
                    if xmax == 0:
                        new_rows += 1
                    else:
                        updated_rows += 1
                    total += 1

                conn.commit()

                # 3. 更新 upload 记录
                cur.execute(
                    """
                    UPDATE market_overview_uploads
                    SET status = 'completed',
                        total_rows = %s,
                        new_rows = %s,
                        updated_rows = %s
                    WHERE id = %s
                    """,
                    (total, new_rows, updated_rows, upload_id),
                )
                conn.commit()

                logger.info(
                    f"导入完成: date={data_date}, type={data_type}, "
                    f"total={total}, new={new_rows}, updated={updated_rows}"
                )

                return {
                    'total': total,
                    'new_rows': new_rows,
                    'updated_rows': updated_rows,
                    'upload_id': upload_id,
                }

        except Exception as e:
            logger.error(f"导入失败: {e}", exc_info=True)
            # 更新 upload 记录为 failed
            if upload_id:
                try:
                    with get_db_connection() as conn:
                        cur = conn.cursor()
                        cur.execute(
                            """
                            UPDATE market_overview_uploads
                            SET status = 'failed', error_message = %s
                            WHERE id = %s
                            """,
                            (str(e)[:500], upload_id),
                        )
                        conn.commit()
                except Exception:
                    logger.error("更新 upload 失败状态时出错", exc_info=True)
            raise

    def get_uploads(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        """获取上传历史列表，按 created_at DESC 排序"""
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT id, filename, data_date, data_type,
                           total_rows, new_rows, updated_rows,
                           status, error_message, admin_id, created_at
                    FROM market_overview_uploads
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset),
                )
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"获取上传历史失败: {e}", exc_info=True)
            return []

    def get_available_dates(self, data_type: Optional[str] = None) -> List[str]:
        """
        获取可用日期列表（降序）。

        用于 Dashboard 日期切换。
        """
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                if data_type:
                    cur.execute(
                        """
                        SELECT DISTINCT data_date::text
                        FROM market_overview_data
                        WHERE data_type = %s
                        ORDER BY data_date DESC
                        """,
                        (data_type,),
                    )
                else:
                    cur.execute(
                        """
                        SELECT DISTINCT data_date::text
                        FROM market_overview_data
                        ORDER BY data_date DESC
                        """
                    )
                return [row[0] for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"获取可用日期失败: {e}", exc_info=True)
            return []

    def get_date_stats(self, data_date: str, data_type: Optional[str] = None) -> Dict:
        """获取某日期的统计摘要"""
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()

                base_query = """
                    SELECT
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE d_trend = '上行趋势') as d_up,
                        COUNT(*) FILTER (WHERE d_trend = '下行趋势') as d_down,
                        COUNT(*) FILTER (WHERE d_trend = '无趋势') as d_flat,
                        COUNT(*) FILTER (WHERE w_trend = '上行趋势') as w_up,
                        COUNT(*) FILTER (WHERE w_trend = '下行趋势') as w_down,
                        COUNT(*) FILTER (WHERE leverage_status = '加杠杆') as leverage_long,
                        COUNT(*) FILTER (WHERE leverage_status = '去杠杆') as leverage_short
                    FROM market_overview_data
                    WHERE data_date = %s
                """

                if data_type:
                    cur.execute(base_query + " AND data_type = %s", (data_date, data_type))
                else:
                    cur.execute(base_query, (data_date,))

                columns = [desc[0] for desc in cur.description]
                row = cur.fetchone()
                return dict(zip(columns, row)) if row else {}
        except Exception as e:
            logger.error(f"获取日期统计失败: {e}", exc_info=True)
            return {}

    @staticmethod
    def parse_filename(filename: str) -> Tuple[Optional[str], Optional[str]]:
        """
        从文件名自动提取日期和数据类型。

        示例: '26-05-18 数据总表（趋势识别＋相对比价＋资金监控）（美股市场）.xlsx'
        → ('2026-05-18', 'us_market')

        Returns:
            (date_str, data_type) 或 (None, None)
        """
        # 提取日期
        date_match = _DATE_RE.search(filename)
        if not date_match:
            return None, None

        yy, mm, dd = date_match.groups()
        date_str = f"20{yy}-{mm}-{dd}"

        # 提取数据类型
        data_type = 'us_market'  # 默认
        for cn_name, en_type in _TYPE_MAP.items():
            if cn_name in filename:
                data_type = en_type
                break

        return date_str, data_type

    # ================================================================
    # Dashboard 数据聚合
    # ================================================================

    # 持仓名单
    HOLDINGS = frozenset({
        "PYPL", "MSFT", "ALB", "IXC", "AEIS", "AMPX", "MU",
        "SNDK", "PLTR", "META", "TSM", "GOOG", "UNH", "BE", "TAN", "SOXS"
    })

    def get_dashboard_data(self, data_date: str) -> Dict:
        """
        获取 Dashboard 全量数据。

        一次调用返回趋势分布、资金面、比价状态、四分类汇总、
        持仓快照和变化对比。

        Args:
            data_date: 数据日期 (YYYY-MM-DD)

        Returns:
            {date, prev_date, stats, holdings, changes_summary}
        """
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()

                # 1. 查询当日全量统计数据（一条聚合查询）
                cur.execute(
                    """
                    SELECT
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE d_trend = '上行趋势') as d_up,
                        COUNT(*) FILTER (WHERE d_trend = '无趋势') as d_flat,
                        COUNT(*) FILTER (WHERE d_trend = '下行趋势') as d_down,
                        COUNT(*) FILTER (WHERE w_trend = '上行趋势') as w_up,
                        COUNT(*) FILTER (WHERE w_trend = '无趋势') as w_flat,
                        COUNT(*) FILTER (WHERE w_trend = '下行趋势') as w_down,
                        COUNT(*) FILTER (WHERE m_trend = '上行趋势') as m_up,
                        COUNT(*) FILTER (WHERE m_trend = '无趋势') as m_flat,
                        COUNT(*) FILTER (WHERE m_trend = '下行趋势') as m_down,
                        COUNT(*) FILTER (WHERE leverage_status = '加杠杆') as lev_long,
                        COUNT(*) FILTER (WHERE leverage_status = '去杠杆') as lev_short,
                        COUNT(*) FILTER (WHERE relative_price_status = 'lead') as rp_lead,
                        COUNT(*) FILTER (WHERE relative_price_status = 'Improving') as rp_improving,
                        COUNT(*) FILTER (WHERE relative_price_status = 'Weakening') as rp_weakening,
                        COUNT(*) FILTER (WHERE relative_price_status = 'Lag') as rp_lag
                    FROM market_overview_data
                    WHERE data_date = %s
                    """,
                    (data_date,),
                )
                columns = [desc[0] for desc in cur.description]
                row = cur.fetchone()
                agg = dict(zip(columns, row))

                total = agg.get('total', 0) or 0

                # 趋势分布
                trends = {
                    'daily': {'up': agg.get('d_up', 0) or 0, 'flat': agg.get('d_flat', 0) or 0, 'down': agg.get('d_down', 0) or 0},
                    'weekly': {'up': agg.get('w_up', 0) or 0, 'flat': agg.get('w_flat', 0) or 0, 'down': agg.get('w_down', 0) or 0},
                    'monthly': {'up': agg.get('m_up', 0) or 0, 'flat': agg.get('m_flat', 0) or 0, 'down': agg.get('m_down', 0) or 0},
                    'total': total,
                }

                # 资金面
                lev_long = agg.get('lev_long', 0) or 0
                lev_short = agg.get('lev_short', 0) or 0
                leverage = {
                    'long': lev_long,
                    'short': lev_short,
                    'long_pct': round(lev_long / total * 100, 1) if total else 0,
                    'short_pct': round(lev_short / total * 100, 1) if total else 0,
                }

                # 比价状态
                relative_price = {
                    'lead': agg.get('rp_lead', 0) or 0,
                    'improving': agg.get('rp_improving', 0) or 0,
                    'weakening': agg.get('rp_weakening', 0) or 0,
                    'lag': agg.get('rp_lag', 0) or 0,
                    'total': total,
                }

                # 2. 四分类汇总（查询全量行在 Python 中分类）
                cur.execute(
                    """
                    SELECT symbol, d_trend, w_trend, m_trend,
                           d_trend_duration, leverage_status,
                           relative_price_status, early_reversal, relative_strength
                    FROM market_overview_data
                    WHERE data_date = %s
                    """,
                    (data_date,),
                )
                all_rows = cur.fetchall()

                categories = {'main_trend': 0, 'main_pullback': 0, 'new_signal': 0, 'avoid': 0}
                main_trend_set = set()
                main_pullback_set = set()

                for r in all_rows:
                    sym, d, w, m, d_dur, lev, rp, early, rs = (r[0], r[1], r[2], r[3],
                                                                r[4] or 0, r[5], r[6],
                                                                float(r[7] or 0), float(r[8] or 0))

                    is_main = (d == '上行趋势' and w == '上行趋势' and lev == '加杠杆')
                    if is_main:
                        categories['main_trend'] += 1
                        main_trend_set.add(sym)
                        continue

                    is_pullback = ((d == '上行趋势' or w == '上行趋势') and
                                   (rp in ('Lag', 'Improving') or lev == '去杠杆'))
                    if is_pullback:
                        categories['main_pullback'] += 1
                        main_pullback_set.add(sym)
                        continue

                    is_new_signal = (
                        (d == '上行趋势' and (d_dur or 0) <= 5) or
                        (d == '上行趋势' and rp == 'Improving' and lev == '加杠杆') or
                        (early > 110 and rs > 95 and lev == '加杠杆')
                    )
                    if is_new_signal:
                        categories['new_signal'] += 1
                        continue

                    is_avoid = (d == '下行趋势' and w == '下行趋势' and lev == '去杠杆')
                    if is_avoid:
                        categories['avoid'] += 1

                # 3. 查询持仓数据
                holdings_list = list(self.HOLDINGS)
                placeholders = ','.join(['%s'] * len(holdings_list))
                cur.execute(
                    f"""
                    SELECT symbol, name,
                           d_trend, d_trend_duration,
                           w_trend, w_trend_duration,
                           m_trend, m_trend_duration,
                           relative_price_status,
                           leverage_status, leverage_value, leverage_change,
                           price_position_60d
                    FROM market_overview_data
                    WHERE data_date = %s AND symbol IN ({placeholders})
                    ORDER BY symbol
                    """,
                    [data_date] + holdings_list,
                )
                h_columns = [desc[0] for desc in cur.description]
                h_rows = cur.fetchall()
                holdings = [dict(zip(h_columns, row)) for row in h_rows]

                # 4. 变化对比（前一交易日）
                prev_date = None
                cur.execute(
                    """
                    SELECT MAX(data_date)::text
                    FROM market_overview_data
                    WHERE data_date < %s
                    """,
                    (data_date,),
                )
                prev_row = cur.fetchone()
                if prev_row and prev_row[0]:
                    prev_date = prev_row[0]

                changes_summary = {'improved': 0, 'worsened': 0, 'new_symbols': 0}

                if prev_date:
                    # 查询前一天持仓数据
                    cur.execute(
                        f"""
                        SELECT symbol, d_trend, w_trend, m_trend,
                               leverage_status, relative_price_status
                        FROM market_overview_data
                        WHERE data_date = %s AND symbol IN ({placeholders})
                        """,
                        [prev_date] + holdings_list,
                    )
                    pc = [desc[0] for desc in cur.description]
                    prev_rows = cur.fetchall()
                    prev_map = {row[0]: dict(zip(pc, row)) for row in prev_rows}

                    # 趋势排序：上行趋势(1) > 无趋势(0) > 下行趋势(-1)
                    trend_order = {'上行趋势': 1, '无趋势': 0, '下行趋势': -1}

                    for h in holdings:
                        sym = h['symbol']
                        if sym not in prev_map:
                            h['change'] = 'new'
                            changes_summary['new_symbols'] += 1
                            continue

                        prev = prev_map[sym]
                        cur_trend = trend_order.get(h.get('d_trend', ''), 0)
                        prev_trend = trend_order.get(prev.get('d_trend', ''), 0)

                        if cur_trend > prev_trend:
                            h['change'] = 'improved'
                            changes_summary['improved'] += 1
                        elif cur_trend < prev_trend:
                            h['change'] = 'worsened'
                            changes_summary['worsened'] += 1
                        else:
                            h['change'] = 'stable'
                else:
                    for h in holdings:
                        h['change'] = None

                conn.commit()

                return {
                    'date': data_date,
                    'prev_date': prev_date,
                    'stats': {
                        'trends': trends,
                        'leverage': leverage,
                        'relative_price': relative_price,
                        'categories': categories,
                    },
                    'holdings': holdings,
                    'changes_summary': changes_summary,
                }

        except Exception as e:
            logger.error(f"Dashboard 数据查询失败: {e}", exc_info=True)
            raise
