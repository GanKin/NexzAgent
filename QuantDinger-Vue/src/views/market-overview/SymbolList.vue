<template>
  <div class="symbol-list">
    <!-- 顶部筛选栏 -->
    <div class="filter-bar">
      <a-input-search
        v-model="filters.search"
        placeholder="搜索代码或名称"
        style="width: 180px"
        allow-clear
        @search="onFilter"
      />
      <a-select v-model="filters.trendLevel" style="width: 90px" @change="onFilter">
        <a-select-option value="daily">日级别</a-select-option>
        <a-select-option value="weekly">周级别</a-select-option>
        <a-select-option value="monthly">月级别</a-select-option>
      </a-select>
      <a-select v-model="filters.trend" style="width: 100px" allow-clear placeholder="趋势" @change="onFilter">
        <a-select-option value="上行趋势">上行</a-select-option>
        <a-select-option value="无趋势">静默</a-select-option>
        <a-select-option value="下行趋势">下行</a-select-option>
      </a-select>
      <a-select v-model="filters.relativePrice" style="width: 110px" allow-clear placeholder="比价状态" @change="onFilter">
        <a-select-option value="lead">Lead</a-select-option>
        <a-select-option value="Improving">Improving</a-select-option>
        <a-select-option value="Weakening">Weakening</a-select-option>
        <a-select-option value="Lag">Lag</a-select-option>
      </a-select>
      <a-select v-model="filters.leverage" style="width: 100px" allow-clear placeholder="杠杆状态" @change="onFilter">
        <a-select-option value="加杠杆">加杠杆</a-select-option>
        <a-select-option value="去杠杆">去杠杆</a-select-option>
      </a-select>
      <a-select v-model="filters.sort" style="width: 120px" @change="onFilter">
        <a-select-option value="relative_strength">相对强度↓</a-select-option>
        <a-select-option value="early_reversal">早期转折↓</a-select-option>
        <a-select-option value="leverage_value">杠杆资金↓</a-select-option>
        <a-select-option value="trend_duration">趋势持续↑</a-select-option>
      </a-select>
      <a-button icon="undo" size="small" @click="resetFilters">重置</a-button>
      <span style="margin-left: auto; color: #999; font-size: 12px">
        共 {{ total }} 条
      </span>
    </div>

    <!-- 数据表格 -->
    <a-table
      :columns="columns"
      :data-source="items"
      :loading="loading"
      :pagination="pagination"
      row-key="symbol"
      size="small"
      :scroll="{ x: 1200 }"
      :custom-row="customRow"
      :row-class-name="rowClassName"
      @change="onTableChange"
    >
      <template slot="trend" slot-scope="text">
        <span :class="trendClass(text)">{{ text }}</span>
      </template>
      <template slot="holding" slot-scope="text">
        <a-tag v-if="text" color="blue" size="small">持仓</a-tag>
      </template>
    </a-table>

    <!-- 详情抽屉 -->
    <a-drawer
      :title="drawerTitle"
      placement="right"
      :width="640"
      :visible="drawerVisible"
      @close="drawerVisible = false"
    >
      <symbol-detail v-if="drawerVisible" :symbol="selectedSymbol" />
    </a-drawer>
  </div>
</template>

<script>
import { getSymbolList } from '@/api/marketOverview'
import SymbolDetail from './SymbolDetail'

export default {
  name: 'SymbolList',
  components: { SymbolDetail },
  data () {
    return {
      loading: false,
      items: [],
      total: 0,
      filters: {
        search: undefined,
        trendLevel: 'daily',
        trend: undefined,
        relativePrice: undefined,
        leverage: undefined,
        sort: 'relative_strength'
      },
      currentPage: 1,
      pageSize: 50,
      drawerVisible: false,
      selectedSymbol: null,
      columns: [
        { title: '', dataIndex: 'is_holding', width: 45, scopedSlots: { customRender: 'holding' } },
        { title: '代码', dataIndex: 'symbol', width: 70, fixed: 'left' },
        { title: '名称', dataIndex: 'name', width: 90, ellipsis: true },
        { title: '相对强度', dataIndex: 'relative_strength', width: 75, sorter: true },
        { title: '早期转折', dataIndex: 'early_reversal', width: 75 },
        { title: '日趋势', dataIndex: 'd_trend', width: 80, scopedSlots: { customRender: 'trend' } },
        { title: '周趋势', dataIndex: 'w_trend', width: 80, scopedSlots: { customRender: 'trend' } },
        { title: '月趋势', dataIndex: 'm_trend', width: 80, scopedSlots: { customRender: 'trend' } },
        { title: '比价', dataIndex: 'relative_price_status', width: 90 },
        { title: '杠杆', dataIndex: 'leverage_status', width: 70 },
        { title: '60日位', dataIndex: 'price_position_60d', width: 65, customRender: v => v != null ? Number(v).toFixed(2) : '-' }
      ]
    }
  },
  computed: {
    pagination () {
      return {
        current: this.currentPage,
        pageSize: this.pageSize,
        total: this.total,
        showSizeChanger: true,
        pageSizeOptions: ['20', '50', '100'],
        showTotal: (total) => `共 ${total} 条`
      }
    },
    drawerTitle () {
      return this.selectedSymbol ? `标的详情 — ${this.selectedSymbol}` : '标的详情'
    }
  },
  created () {
    this.loadData()
  },
  methods: {
    async loadData () {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          trend_level: this.filters.trendLevel,
          sort: this.filters.sort
        }
        if (this.filters.search) params.search = this.filters.search
        if (this.filters.trend) params.trend = this.filters.trend
        if (this.filters.relativePrice) params.relative_price = this.filters.relativePrice
        if (this.filters.leverage) params.leverage = this.filters.leverage

        const res = await getSymbolList(params)
        if (res.data && res.data.code === 1) {
          const data = res.data.data
          this.items = data.items || []
          this.total = data.total || 0
        }
      } catch (e) {
        console.error('加载列表失败:', e)
      } finally {
        this.loading = false
      }
    },
    onFilter () {
      this.currentPage = 1
      this.loadData()
    },
    onTableChange (pagination) {
      this.currentPage = pagination.current
      this.pageSize = pagination.pageSize
      this.loadData()
    },
    resetFilters () {
      this.filters = {
        search: undefined,
        trendLevel: 'daily',
        trend: undefined,
        relativePrice: undefined,
        leverage: undefined,
        sort: 'relative_strength'
      }
      this.currentPage = 1
      this.loadData()
    },
    customRow (record) {
      return {
        on: {
          click: () => {
            this.selectedSymbol = record.symbol
            this.drawerVisible = true
          }
        },
        style: { cursor: 'pointer' }
      }
    },
    rowClassName (record) {
      return record.is_holding ? 'holding-row' : ''
    },
    trendClass (trend) {
      if (trend === '上行趋势') return 'text-green'
      if (trend === '下行趋势') return 'text-red'
      return 'text-yellow'
    }
  }
}
</script>

<style lang="less" scoped>
.symbol-list {
  padding: 0;
}
.filter-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  align-items: center;
  flex-wrap: wrap;
}
.holding-row {
  background-color: #e6f7ff;
}
.holding-row:hover > td {
  background-color: #bae7ff !important;
}
.text-green { color: #52c41a; font-weight: 500; }
.text-red { color: #ff4d4f; font-weight: 500; }
.text-yellow { color: #faad14; font-weight: 500; }
</style>
