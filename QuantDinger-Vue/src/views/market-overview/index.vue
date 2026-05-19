<template>
  <div class="market-overview">
    <a-page-header title="市场概览" sub-title="管理员专属">
      <template slot="extra">
        <a-tag color="blue">管理员</a-tag>
      </template>
    </a-page-header>

    <a-tabs v-model="activeTab" style="padding: 0 24px">
      <a-tab-pane key="dashboard" tab="Dashboard">
        <dashboard-tab />
      </a-tab-pane>
      <a-tab-pane key="upload" tab="数据上传">
        <a-row :gutter="16">
          <a-col :span="12">
            <upload-card @upload-success="onUploadSuccess" />
          </a-col>
          <a-col :span="12">
            <a-card title="最近上传" :bordered="false">
              <a-table
                :columns="uploadColumns"
                :data-source="uploads"
                :pagination="{ pageSize: 10 }"
                size="small"
                :loading="loading"
                row-key="id"
              >
                <template slot="status" slot-scope="text">
                  <a-badge
                    :status="text === 'completed' ? 'success' : text === 'failed' ? 'error' : 'processing'"
                    :text="text === 'completed' ? '成功' : text === 'failed' ? '失败' : '处理中'"
                  />
                </template>
                <template slot="data_date" slot-scope="text">
                  {{ text || '-' }}
                </template>
                <template slot="summary" slot-scope="text, record">
                  <span v-if="record.status === 'completed'">
                    新增 {{ record.new_rows }} / 更新 {{ record.updated_rows }}
                  </span>
                  <span v-else-if="record.status === 'failed'" class="error-text">
                    {{ (record.error_message || '').substring(0, 50) }}
                  </span>
                  <span v-else>-</span>
                </template>
                <template slot="created_at" slot-scope="text">
                  {{ text ? text.substring(0, 16).replace('T', ' ') : '-' }}
                </template>
              </a-table>
            </a-card>
          </a-col>
        </a-row>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script>
import DashboardTab from './DashboardTab'
import UploadCard from './UploadCard'
import { getUploadHistory } from '@/api/marketOverview'

export default {
  name: 'MarketOverview',
  components: {
    DashboardTab,
    UploadCard
  },
  data () {
    return {
      activeTab: 'dashboard',
      uploads: [],
      loading: false,
      uploadColumns: [
        { title: '数据日期', dataIndex: 'data_date', key: 'data_date', scopedSlots: { customRender: 'data_date' }, width: 110 },
        { title: '文件名', dataIndex: 'filename', key: 'filename', ellipsis: true },
        { title: '状态', dataIndex: 'status', key: 'status', scopedSlots: { customRender: 'status' }, width: 80 },
        { title: '摘要', key: 'summary', scopedSlots: { customRender: 'summary' }, width: 160 },
        { title: '时间', dataIndex: 'created_at', key: 'created_at', scopedSlots: { customRender: 'created_at' }, width: 130 }
      ]
    }
  },
  created () {
    this.loadUploads()
  },
  methods: {
    async loadUploads () {
      this.loading = true
      try {
        const res = await getUploadHistory({ limit: 20 })
        if (res.data && res.data.code === 1) {
          this.uploads = res.data.data.uploads || []
        }
      } catch (e) {
        console.error('获取上传历史失败:', e)
      } finally {
        this.loading = false
      }
    },
    onUploadSuccess () {
      this.loadUploads()
      // 切换到 dashboard tab 刷新数据
      this.activeTab = 'dashboard'
    }
  }
}
</script>

<style lang="less" scoped>
.market-overview {
  padding: 0;
}
.error-text {
  color: #ff4d4f;
  font-size: 12px;
}
</style>
