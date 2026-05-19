<template>
  <div class="symbol-detail">
    <a-spin :spinning="loading">
      <template v-if="data">
        <!-- 基础信息 -->
        <a-card size="small" style="margin-bottom: 12px">
          <a-descriptions :column="2" size="small">
            <a-descriptions-item label="代码">
              <strong>{{ data.symbol }}</strong>
            </a-descriptions-item>
            <a-descriptions-item label="名称">{{ data.name }}</a-descriptions-item>
            <a-descriptions-item label="数据范围">
              {{ data.date_range.start || '-' }} ~ {{ data.date_range.end || '-' }}
            </a-descriptions-item>
            <a-descriptions-item label="数据天数">
              {{ data.timeline.length }} 天
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <!-- 日期范围选择 -->
        <div class="date-range-bar">
          <a-radio-group v-model="dateRange" size="small" button-style="solid" @change="onDateRangeChange">
            <a-radio-button value="7">近7天</a-radio-button>
            <a-radio-button value="30">近30天</a-radio-button>
            <a-radio-button value="all">全部</a-radio-button>
          </a-radio-group>
          <a-range-picker
            v-model="customRange"
            size="small"
            style="margin-left: 8px"
            value-format="YYYY-MM-DD"
            @change="onCustomRangeChange"
          />
        </div>

        <!-- 时序表格 -->
        <a-table
          :columns="timelineColumns"
          :data-source="data.timeline"
          :pagination="false"
          size="small"
          row-key="data_date"
          :scroll="{ y: 400 }"
          style="margin-top: 12px"
        >
          <template slot="trend" slot-scope="text">
            <span :class="trendClass(text)">{{ text }}</span>
          </template>
          <template slot="rp_status" slot-scope="text">
            <a-tag :color="rpColor(text)" size="small">{{ text }}</a-tag>
          </template>
          <template slot="lev_status" slot-scope="text">
            <span :style="{ color: text === '加杠杆' ? '#52c41a' : '#ff4d4f', fontWeight: 500 }">{{ text }}</span>
          </template>
        </a-table>
      </template>

      <a-empty v-else-if="!loading" description="无时序数据" />
    </a-spin>
  </div>
</template>

<script>
import { getSymbolTimeline } from '@/api/marketOverview'
import moment from 'moment'

export default {
  name: 'SymbolDetail',
  props: {
    symbol: { type: String, required: true }
  },
  data () {
    return {
      loading: false,
      data: null,
      dateRange: '30',
      customRange: null,
      timelineColumns: [
        { title: '日期', dataIndex: 'data_date', width: 100, fixed: 'left' },
        { title: '日趋势', dataIndex: 'd_trend', width: 80, scopedSlots: { customRender: 'trend' } },
        { title: '周趋势', dataIndex: 'w_trend', width: 80, scopedSlots: { customRender: 'trend' } },
        { title: '月趋势', dataIndex: 'm_trend', width: 80, scopedSlots: { customRender: 'trend' } },
        { title: '比价', dataIndex: 'relative_price_status', width: 90, scopedSlots: { customRender: 'rp_status' } },
        { title: '比价天数', dataIndex: 'relative_price_duration', width: 65 },
        { title: '杠杆', dataIndex: 'leverage_status', width: 70, scopedSlots: { customRender: 'lev_status' } },
        { title: '杠杆值', dataIndex: 'leverage_value', width: 65, customRender: v => v != null ? Number(v).toFixed(1) : '-' },
        { title: '杠杆变动', dataIndex: 'leverage_change', width: 65, customRender: v => v != null ? Number(v).toFixed(1) : '-' },
        { title: '相对强度', dataIndex: 'relative_strength', width: 65 },
        { title: '60日位', dataIndex: 'price_position_60d', width: 60, customRender: v => v != null ? Number(v).toFixed(2) : '-' }
      ]
    }
  },
  created () {
    this.loadTimeline()
  },
  methods: {
    async loadTimeline (startDate, endDate) {
      this.loading = true
      try {
        const params = {}
        if (startDate) params.start_date = startDate
        if (endDate) params.end_date = endDate
        const res = await getSymbolTimeline(this.symbol, params)
        if (res.data && res.data.code === 1) {
          this.data = res.data.data
        }
      } catch (e) {
        console.error('加载时序数据失败:', e)
      } finally {
        this.loading = false
      }
    },
    onDateRangeChange (e) {
      this.customRange = null
      const val = e.target.value
      if (val === 'all') {
        this.loadTimeline()
      } else {
        const days = parseInt(val)
        const start = moment().subtract(days, 'days').format('YYYY-MM-DD')
        this.loadTimeline(start)
      }
    },
    onCustomRangeChange (dates) {
      if (dates && dates.length === 2) {
        this.dateRange = ''
        this.loadTimeline(dates[0], dates[1])
      }
    },
    trendClass (trend) {
      if (trend === '上行趋势') return 'text-green'
      if (trend === '下行趋势') return 'text-red'
      return 'text-yellow'
    },
    rpColor (status) {
      const map = { 'lead': 'green', 'Improving': 'blue', 'Weakening': 'orange', 'Lag': 'red' }
      return map[status] || ''
    }
  }
}
</script>

<style lang="less" scoped>
.symbol-detail {
  padding: 0;
}
.date-range-bar {
  display: flex;
  align-items: center;
  margin-bottom: 0;
}
.text-green { color: #52c41a; font-weight: 500; }
.text-red { color: #ff4d4f; font-weight: 500; }
.text-yellow { color: #faad14; font-weight: 500; }
</style>
