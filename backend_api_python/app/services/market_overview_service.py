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
