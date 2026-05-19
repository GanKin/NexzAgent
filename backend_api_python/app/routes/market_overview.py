"""
市场概览 API 路由

数据上传、上传历史查询、可用日期列表。
所有端点仅限管理员访问。
"""

import os
import time
import uuid

from flask import Blueprint, request, jsonify, g
from werkzeug.utils import secure_filename

from app.utils.auth import login_required, admin_required
from app.utils.logger import get_logger
from app.services.market_overview_service import MarketOverviewService
from app.services.market_overview_parser import MarketOverviewParser

logger = get_logger(__name__)

market_overview_bp = Blueprint('market_overview', __name__)

UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'uploads', 'market_overview'
)
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

_service = MarketOverviewService()
_parser = MarketOverviewParser()


def _allowed_file(filename: str) -> bool:
    """检查文件扩展名是否合法"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@market_overview_bp.route('/upload', methods=['POST'])
@login_required
@admin_required
def upload():
    """
    上传 Excel 文件并导入数据。

    接受 multipart/form-data，字段名 file。
    解析后 UPSERT 入库，返回导入摘要。
    """
    # 检查文件是否存在
    if 'file' not in request.files:
        return jsonify({'code': 0, 'msg': '未找到上传文件', 'data': None}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 0, 'msg': '未选择文件', 'data': None}), 400

    # 验证扩展名
    if not _allowed_file(file.filename):
        return jsonify({
            'code': 0,
            'msg': '文件格式不正确，仅支持 .xlsx 和 .xls 文件',
            'data': None,
        }), 400

    # 读取文件内容检查大小
    file_content = file.read()
    if len(file_content) > MAX_FILE_SIZE:
        return jsonify({
            'code': 0,
            'msg': f'文件过大，最大支持 {MAX_FILE_SIZE // (1024*1024)}MB',
            'data': None,
        }), 400

    # 从文件名提取日期和类型
    filename = secure_filename(file.filename)
    # secure_filename 会移除中文，使用原始文件名解析
    original_filename = request.files['file'].filename or filename
    data_date, data_type = MarketOverviewService.parse_filename(original_filename)

    if not data_date:
        return jsonify({
            'code': 0,
            'msg': f'无法从文件名识别日期。文件名格式示例: 26-05-18 数据总表（美股市场）.xlsx',
            'data': None,
        }), 400

    # 确保上传目录存在
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 保存文件（{date}_{type}_{timestamp}_{uuid}.xlsx）
    timestamp = int(time.time())
    ext = original_filename.rsplit('.', 1)[-1] if '.' in original_filename else 'xlsx'
    saved_filename = f"{data_date}_{data_type}_{timestamp}_{uuid.uuid4().hex[:8]}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)

    try:
        with open(file_path, 'wb') as f:
            f.write(file_content)
    except Exception as e:
        logger.error(f"文件保存失败: {e}", exc_info=True)
        return jsonify({'code': 0, 'msg': f'文件保存失败: {str(e)}', 'data': None}), 500

    # 解析 Excel
    try:
        records, parse_errors = _parser.parse(file_path)
    except Exception as e:
        logger.error(f"Excel 解析异常: {e}", exc_info=True)
        return jsonify({
            'code': 0,
            'msg': f'Excel 解析失败: {str(e)}',
            'data': None,
        }), 400

    if not records:
        error_detail = '; '.join(
            f"行{e.get('row', '?')} {e.get('field', '?')}: {e.get('error', '')}"
            for e in parse_errors[:5]
        )
        return jsonify({
            'code': 0,
            'msg': f'解析无有效数据。原因: {error_detail}',
            'data': {'parse_errors': parse_errors},
        }), 400

    # 导入数据
    try:
        admin_id = g.user_id
        result = _service.import_data(
            data_date=data_date,
            data_type=data_type,
            records=records,
            admin_id=admin_id,
            filename=original_filename,
            file_path=file_path,
        )
    except Exception as e:
        logger.error(f"数据导入失败: {e}", exc_info=True)
        return jsonify({
            'code': 0,
            'msg': f'数据导入失败: {str(e)}',
            'data': None,
        }), 500

    # 构建返回结果（导入摘要）
    warnings = []
    if parse_errors:
        warnings = [
            f"行{e.get('row', '?')} {e.get('field', '?')}: {e.get('error', '')}"
            for e in parse_errors[:10]
        ]

    return jsonify({
        'code': 1,
        'msg': 'success',
        'data': {
            'data_date': data_date,
            'data_type': data_type,
            'total_rows': result['total'],
            'new_rows': result['new_rows'],
            'updated_rows': result['updated_rows'],
            'upload_id': result.get('upload_id'),
            'warnings': warnings,
        },
    }), 200


@market_overview_bp.route('/uploads', methods=['GET'])
@login_required
@admin_required
def get_uploads():
    """获取上传历史列表"""
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    limit = min(limit, 100)  # 限制最大值

    uploads = _service.get_uploads(limit=limit, offset=offset)

    return jsonify({
        'code': 1,
        'msg': 'success',
        'data': {
            'uploads': uploads,
            'limit': limit,
            'offset': offset,
        },
    }), 200


@market_overview_bp.route('/dates', methods=['GET'])
@login_required
@admin_required
def get_dates():
    """获取可用日期列表（降序）"""
    data_type = request.args.get('data_type', None)

    dates = _service.get_available_dates(data_type=data_type)

    return jsonify({
        'code': 1,
        'msg': 'success',
        'data': {
            'dates': dates,
        },
    }), 200


@market_overview_bp.route('/dashboard', methods=['GET'])
@login_required
@admin_required
def get_dashboard():
    """获取 Dashboard 全量数据"""
    date = request.args.get('date', None)

    if not date:
        # 默认取最新日期
        dates = _service.get_available_dates()
        if not dates:
            return jsonify({'code': 1, 'msg': 'success', 'data': None}), 200
        date = dates[0]

    try:
        data = _service.get_dashboard_data(date)
    except Exception as e:
        logger.error(f"Dashboard 数据查询失败: {e}", exc_info=True)
        return jsonify({'code': 0, 'msg': f'查询失败: {str(e)}', 'data': None}), 500

    return jsonify({
        'code': 1,
        'msg': 'success',
        'data': data,
    }), 200


@market_overview_bp.route('/symbols', methods=['GET'])
@login_required
@admin_required
def get_symbols():
    """代码列表查询（筛选+排序+分页）"""
    data_date = request.args.get('date', None)
    search = request.args.get('search', None)
    trend_level = request.args.get('trend_level', 'daily')
    trend = request.args.get('trend', None)
    relative_price = request.args.get('relative_price', None)
    leverage = request.args.get('leverage', None)
    sort = request.args.get('sort', 'relative_strength')
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 50, type=int)

    page = max(1, page)
    page_size = max(1, min(200, page_size))

    try:
        result = _service.get_symbols(
            data_date=data_date, search=search,
            trend_level=trend_level, trend=trend,
            relative_price=relative_price, leverage=leverage,
            sort=sort, page=page, page_size=page_size,
        )
    except Exception as e:
        logger.error(f"列表查询失败: {e}", exc_info=True)
        return jsonify({'code': 0, 'msg': f'查询失败: {str(e)}', 'data': None}), 500

    return jsonify({'code': 1, 'msg': 'success', 'data': result}), 200


@market_overview_bp.route('/symbols/<symbol>/timeline', methods=['GET'])
@login_required
@admin_required
def get_symbol_timeline(symbol):
    """标的时序数据"""
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    try:
        result = _service.get_symbol_timeline(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )
    except Exception as e:
        logger.error(f"时序查询失败 ({symbol}): {e}", exc_info=True)
        return jsonify({'code': 0, 'msg': f'查询失败: {str(e)}', 'data': None}), 500

    if result is None:
        return jsonify({'code': 0, 'msg': '标的不存在', 'data': None}), 404

    return jsonify({'code': 1, 'msg': 'success', 'data': result}), 200
