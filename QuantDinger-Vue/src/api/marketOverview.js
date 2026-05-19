import request from '@/utils/request'

const api = {
  upload: '/api/market-overview/upload',
  uploads: '/api/market-overview/uploads',
  dates: '/api/market-overview/dates'
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
