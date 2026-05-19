import request from '@/utils/request'

const api = {
  upload: '/api/market-overview/upload',
  uploads: '/api/market-overview/uploads',
  dates: '/api/market-overview/dates',
  dashboard: '/api/market-overview/dashboard',
  symbols: '/api/market-overview/symbols',
  symbolTimeline: '/api/market-overview/symbols/'
}

export default api

/**
 * 上传 Excel 文件
 * @param {File} file - Excel 文件对象
 * @returns {Promise} 导入摘要
 */
export function uploadMarketData (file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: api.upload,
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 30000 // 30秒超时（大文件上传）
  })
}

/**
 * 获取上传历史
 */
export function getUploadHistory (parameter) {
  return request({
    url: api.uploads,
    method: 'get',
    params: parameter
  })
}

/**
 * 获取可用日期列表
 */
export function getAvailableDates (parameter) {
  return request({
    url: api.dates,
    method: 'get',
    params: parameter
  })
}


/**
 * 获取 Dashboard 数据
 * @param {string} date - 可选，默认最新日期
 */
export function getDashboardData (date) {
  return request({
    url: api.dashboard,
    method: 'get',
    params: date ? { date } : {}
  })
}


/**
 * 获取代码列表（筛选+排序+分页）
 */
export function getSymbolList (params) {
  return request({
    url: api.symbols,
    method: 'get',
    params
  })
}

/**
 * 获取标的时序数据
 */
export function getSymbolTimeline (symbol, params) {
  return request({
    url: api.symbolTimeline + symbol + '/timeline',
    method: 'get',
    params
  })
}
