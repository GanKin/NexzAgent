<template>
  <a-card title="上传数据" :bordered="false">
    <a-upload-dragger
      name="file"
      :multiple="false"
      accept=".xlsx,.xls"
      :before-upload="beforeUpload"
      :custom-request="handleUpload"
      :show-upload-list="false"
      :disabled="uploading"
    >
      <p class="ant-upload-drag-icon">
        <a-icon type="inbox" />
      </p>
      <p class="ant-upload-text">点击或拖拽 Excel 文件到此区域上传</p>
      <p class="ant-upload-hint">支持 .xlsx 格式，单次上传一个文件（最大 10MB）</p>
    </a-upload-dragger>

    <a-progress v-if="uploading" :percent="100" status="active" style="margin-top: 16px" />

    <!-- 上传成功摘要 -->
    <a-alert
      v-if="uploadResult"
      type="success"
      show-icon
      style="margin-top: 16px"
    >
      <template slot="message">
        <span>导入成功</span>
      </template>
      <template slot="description">
        <div>数据日期: <strong>{{ uploadResult.data_date }}</strong></div>
        <div>数据类型: {{ uploadResult.data_type }}</div>
        <div>
          总行数: {{ uploadResult.total_rows }}
          （新增: {{ uploadResult.new_rows }}，更新: {{ uploadResult.updated_rows }}）
        </div>
        <div v-if="uploadResult.warnings && uploadResult.warnings.length > 0" class="warning-text">
          <a-divider style="margin: 8px 0" />
          <div v-for="(w, i) in uploadResult.warnings.slice(0, 5)" :key="i">{{ w }}</div>
          <div v-if="uploadResult.warnings.length > 5">...还有 {{ uploadResult.warnings.length - 5 }} 条警告</div>
        </div>
      </template>
    </a-alert>

    <!-- 上传失败 -->
    <a-alert
      v-if="uploadError"
      type="error"
      show-icon
      style="margin-top: 16px"
    >
      <template slot="message">上传失败</template>
      <template slot="description">
        <div>{{ uploadError }}</div>
      </template>
    </a-alert>
  </a-card>
</template>

<script>
import { uploadMarketData } from '@/api/marketOverview'

export default {
  name: 'UploadCard',
  data () {
    return {
      uploading: false,
      uploadResult: null,
      uploadError: null
    }
  },
  methods: {
    beforeUpload (file) {
      this.uploadResult = null
      this.uploadError = null

      // 验证扩展名
      const ext = file.name.split('.').pop().toLowerCase()
      if (!['xlsx', 'xls'].includes(ext)) {
        this.uploadError = '仅支持 .xlsx 和 .xls 文件格式'
        return false
      }

      // 验证大小（10MB）
      if (file.size > 10 * 1024 * 1024) {
        this.uploadError = '文件大小不能超过 10MB'
        return false
      }

      return true
    },
    async handleUpload (options) {
      const { file } = options
      this.uploading = true
      this.uploadResult = null
      this.uploadError = null

      try {
        const res = await uploadMarketData(file)
        const data = res.data

        if (data.code === 1) {
          this.uploadResult = data.data
          this.$emit('upload-success', data.data)
          this.$message.success('数据导入成功')
        } else {
          this.uploadError = data.msg || '导入失败'
        }
      } catch (e) {
        const msg = (e.response && e.response.data && e.response.data.msg) || e.message || '上传失败'
        this.uploadError = msg
      } finally {
        this.uploading = false
      }
    }
  }
}
</script>

<style lang="less" scoped>
.warning-text {
  color: #faad14;
  font-size: 12px;
}
</style>
