<template>
  <div class="dashboard-tab">
    <!-- 日期选择器 -->
    <div class="date-bar">
      <a-select
        v-model="selectedDate"
        style="width: 200px"
        placeholder="选择日期"
        :loading="datesLoading"
        @change="onDateChange"
      >
        <a-select-option v-for="d in dates" :key="d" :value="d">
          {{ d }}
        </a-select-option>
      </a-select>
      <a-tag v-if="stats" color="blue" style="margin-left: 8px">
        共 {{ stats.trends.total }} 只标的
      </a-tag>
    </div>

    <a-spin :spinning="loading" tip="加载中...">
      <template v-if="stats">
        <!-- 趋势分布 -->
        <a-row :gutter="16" style="margin-bottom: 16px">
          <a-col :span="8" v-for="level in trendLevels" :key="level.key">
            <a-card :title="level.label + '趋势'" size="small">
              <div class="trend-bar">
                <div class="trend-up" :style="{ width: pct(level.key, 'up') + '%' }">
                  {{ pct(level.key, 'up') }}%
                </div>
                <div class="trend-flat" :style="{ width: pct(level.key, 'flat') + '%' }">
                  {{ pct(level.key, 'flat') }}%
                </div>
                <div class="trend-down" :style="{ width: pct(level.key, 'down') + '%' }">
                  {{ pct(level.key, 'down') }}%
                </div>
              </div>
              <div class="trend-labels">
                <span class="label-up">上行 {{ stats.trends[level.key].up }}</span>
                <span class="label-flat">静默 {{ stats.trends[level.key].flat }}</span>
                <span class="label-down">下行 {{ stats.trends[level.key].down }}</span>
              </div>
            </a-card>
          </a-col>
        </a-row>

        <!-- 资金面 + 比价状态 -->
        <a-row :gutter="16" style="margin-bottom: 16px">
          <a-col :span="8">
            <a-card title="资金面" size="small">
              <a-row>
                <a-col :span="12" style="text-align: center">
                  <div class="stat-number" style="color: #52c41a">{{ stats.leverage.long }}</div>
                  <div>加杠杆 {{ stats.leverage.long_pct }}%</div>
                </a-col>
                <a-col :span="12" style="text-align: center">
                  <div class="stat-number" style="color: #ff4d4f">{{ stats.leverage.short }}</div>
                  <div>去杠杆 {{ stats.leverage.short_pct }}%</div>
                </a-col>
              </a-row>
            </a-card>
          </a-col>
          <a-col :span="16">
            <a-card title="比价状态分布" size="small">
              <span style="margin-right: 16px">
                <a-tag color="green">Lead {{ stats.relative_price.lead }}</a-tag>
                <a-tag color="blue">Improving {{ stats.relative_price.improving }}</a-tag>
              </span>
              <span>
                <a-tag color="orange">Weakening {{ stats.relative_price.weakening }}</a-tag>
                <a-tag color="red">Lag {{ stats.relative_price.lag }}</a-tag>
              </span>
            </a-card>
          </a-col>
        </a-row>

        <!-- 筛选分类 + 变化摘要 -->
        <a-row :gutter="16" style="margin-bottom: 16px">
          <a-col :span="16">
            <a-card title="筛选分类" size="small">
              <a-row :gutter="8">
                <a-col :span="6">
                  <a-statistic title="主升浪" :value="stats.categories.main_trend" :value-style="{ color: '#52c41a' }" />
                </a-col>
                <a-col :span="6">
                  <a-statistic title="主升调整" :value="stats.categories.main_pullback" :value-style="{ color: '#faad14' }" />
                </a-col>
                <a-col :span="6">
                  <a-statistic title="新信号/反转" :value="stats.categories.new_signal" :value-style="{ color: '#1890ff' }" />
                </a-col>
                <a-col :span="6">
                  <a-statistic title="规避区" :value="stats.categories.avoid" :value-style="{ color: '#ff4d4f' }" />
                </a-col>
              </a-row>
            </a-card>
          </a-col>
          <a-col :span="8">
            <a-card title="今日变化" size="small">
              <a-row>
                <a-col :span="8" style="text-align: center">
                  <a-statistic title="改善" :value="changesSummary.improved" :value-style="{ color: '#52c41a' }" />
                </a-col>
                <a-col :span="8" style="text-align: center">
                  <a-statistic title="恶化" :value="changesSummary.worsened" :value-style="{ color: '#ff4d4f' }" />
                </a-col>
                <a-col :span="8" style="text-align: center">
                  <a-statistic title="新增" :value="changesSummary.new_symbols" :value-style="{ color: '#1890ff' }" />
                </a-col>
              </a-row>
            </a-card>
          </a-col>
        </a-row>

        <!-- 持仓快照表 -->
        <a-card title="持仓快照" size="small">
          <a-table
            :columns="holdingColumns"
            :data-source="holdings"
            :pagination="false"
            size="small"
            row-key="symbol"
            :scroll="{ x: 900 }"
          >
            <template slot="trend" slot-scope="text">
              <span :class="trendClass(text)">{{ shortTrend(text) }}</span>
            </template>
            <template slot="change" slot-scope="text">
              <a-tag v-if="text === 'improved'" color="green">↑</a-tag>
              <a-tag v-else-if="text === 'worsened'" color="red">↓</a-tag>
              <a-tag v-else-if="text === 'new'" color="blue">NEW</a-tag>
              <span v-else>-</span>
            </template>
          </a-table>
        </a-card>
      </template>

      <a-empty v-else-if="!loading" description="暂无数据，请先上传 Excel 文件" />
    </a-spin>
  </div>
</template>

<script>
import { getDashboardData, getAvailableDates } from '@/api/marketOverview'

export default {
  name: 'DashboardTab',
  data () {
    return {
      loading: false,
      datesLoading: false,
      dates: [],
      selectedDate: null,
      dashboardData: null,
      holdingColumns: [
        { title: '代码', dataIndex: 'symbol', width: 70, fixed: 'left' },
        { title: '名称', dataIndex: 'name', width: 90, ellipsis: true },
        { title: '日趋势', dataIndex: 'd_trend', width: 80, scopedSlots: { customRender: 'trend' } },
        { title: '周趋势', dataIndex: 'w_trend', width: 80, scopedSlots: { customRender: 'trend' } },
        { title: '月趋势', dataIndex: 'm_trend', width: 80, scopedSlots: { customRender: 'trend' } },
        { title: '比价', dataIndex: 'relative_price_status', width: 90 },
        { title: '杠杆', dataIndex: 'leverage_status', width: 70 },
        { title: '杠杆值', dataIndex: 'leverage_value', width: 70, customRender: (v) => v != null ? Number(v).toFixed(1) : '-' },
        { title: '60日位', dataIndex: 'price_position_60d', width: 65, customRender: (v) => v != null ? Number(v).toFixed(2) : '-' },
        { title: '变化', dataIndex: 'change', width: 60, scopedSlots: { customRender: 'change' } }
      ],
      trendLevels: [
        { key: 'daily', label: '日级别' },
        { key: 'weekly', label: '周级别' },
        { key: 'monthly', label: '月级别' }
      ]
    }
  },
  computed: {
    stats () {
      return this.dashboardData ? this.dashboardData.stats : null
    },
    holdings () {
      return this.dashboardData ? (this.dashboardData.holdings || []) : []
    },
    changesSummary () {
      return this.dashboardData ? (this.dashboardData.changes_summary || { improved: 0, worsened: 0, new_symbols: 0 }) : { improved: 0, worsened: 0, new_symbols: 0 }
    }
  },
  created () {
    this.loadDates()
  },
  methods: {
    pct (level, type) {
      if (!this.stats) return 0
      const t = this.stats.trends
      const total = t.total || 1
      const val = t[level] ? t[level][type] || 0 : 0
      return Math.round(val / total * 100)
    },
    trendClass (trend) {
      if (trend === '上行趋势') return 'text-green'
      if (trend === '下行趋势') return 'text-red'
      return 'text-yellow'
    },
    shortTrend (trend) {
      if (trend === '上行趋势') return '↑上行'
      if (trend === '下行趋势') return '↓下行'
      return '-静默'
    },
    async loadDates () {
      this.datesLoading = true
      try {
        const res = await getAvailableDates()
        if (res.data && res.data.code === 1) {
          this.dates = res.data.data.dates || []
          if (this.dates.length > 0) {
            this.selectedDate = this.dates[0]
            this.loadDashboard(this.selectedDate)
          }
        }
      } catch (e) {
        console.error('获取日期列表失败:', e)
      } finally {
        this.datesLoading = false
      }
    },
    async loadDashboard (date) {
      this.loading = true
      try {
        const res = await getDashboardData(date)
        if (res.data && res.data.code === 1) {
          this.dashboardData = res.data.data
        }
      } catch (e) {
        console.error('加载 Dashboard 失败:', e)
        this.$message.error('加载 Dashboard 数据失败')
      } finally {
        this.loading = false
      }
    },
    onDateChange (date) {
      this.selectedDate = date
      this.loadDashboard(date)
    }
  }
}
</script>

<style lang="less" scoped>
.dashboard-tab {
  padding: 0;
}
.date-bar {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}
.trend-bar {
  display: flex;
  height: 28px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}
.trend-up {
  background: #52c41a;
  color: white;
  text-align: center;
  font-size: 12px;
  line-height: 28px;
  min-width: 20px;
}
.trend-flat {
  background: #faad14;
  color: white;
  text-align: center;
  font-size: 12px;
  line-height: 28px;
  min-width: 20px;
}
.trend-down {
  background: #ff4d4f;
  color: white;
  text-align: center;
  font-size: 12px;
  line-height: 28px;
  min-width: 20px;
}
.trend-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
}
.stat-number {
  font-size: 28px;
  font-weight: 600;
  line-height: 1.2;
}
.text-green { color: #52c41a; font-weight: 500; }
.text-red { color: #ff4d4f; font-weight: 500; }
.text-yellow { color: #faad14; font-weight: 500; }
</style>
