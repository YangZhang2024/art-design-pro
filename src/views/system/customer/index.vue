<!-- index.vue - 客户管理主页面
职责：组合搜索栏+表格+弹窗，管理数据与业务逻辑
关联：customer-search(搜索)/customer-dialog(弹窗)/useTable(核心hook)/api/customer-manage(接口)
-->

<style lang="scss" scoped>
  .customer-page {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
</style>
<template>
  <div class="customer-page art-full-height">
    <CustomerSearch v-model="searchForm" @search="handleSearch" @reset="resetSearchParams" />

    <ElCard class="art-table-card">
      <ArtTableHeader v-model:columns="columnChecks" :loading="loading" @refresh="refreshData">
        <template #left>
          <ElSpace wrap>
            <ElButton @click="showDialog('add')" v-ripple>新增客户</ElButton>
          </ElSpace>
        </template>
      </ArtTableHeader>

      <ArtTable
        :loading="loading"
        :data="data"
        :columns="columns"
        :pagination="pagination"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      >
      </ArtTable>

      <CustomerDialog
        v-model:visible="dialogVisible"
        :type="dialogType"
        :customer-data="currentCustomerData"
        @submit="handleDialogSubmit"
      />
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  // useTable: 项目核心 table hook，自动管理 loading/分页/搜索/缓存/刷新策略
  import { useTable } from '@/hooks/core/useTable'
  // API 函数对应 backend/routers/business/customer.py 的 4 个接口
  import {
    fetchGetCustomerList,
    fetchCreateCustomer,
    fetchUpdateCustomer
  } from '@/api/customer-manage'
  import { fetchDeleteCustomer } from '@/api/customer-manage'
  // 子组件: CustomerSearch(搜索栏) CustomerDialog(新增/编辑弹窗)
  import CustomerSearch from './modules/customer-search.vue'
  import CustomerDialog from './modules/customer-dialog.vue'
  // ElTag 渲染状态标签, ElMessageBox 确认对话框
  import { ElTag, ElMessageBox } from 'element-plus'
  // DialogType = 'add' | 'edit', 定义在 @/types/common/index.ts
  import { DialogType } from '@/types'
  // ArtButtonTable: 项目统一的操作列(编辑/删除)按钮组件
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'

  defineOptions({ name: 'Customer' })

  type CustomerItem = Api.CustomerManage.CustomerListItem

  const dialogType = ref<DialogType>('add')
  const dialogVisible = ref(false)
  const currentCustomerData = ref<Partial<CustomerItem>>({})

  // 搜索表单数据, 与 customer-search.vue 通过 v-model 双向绑定
  const searchForm = ref<Api.CustomerManage.CustomerSearchParams>({
    name: undefined,
    status: undefined,
    startTime: undefined,
    endTime: undefined
  })

  // 状态字典: '1'(启用/success绿) / '2'(禁用/info灰) → ElTag 样式
  const CUSTOMER_STATUS_CONFIG = {
    '1': { type: 'success' as const, text: '启用' },
    '2': { type: 'info' as const, text: '禁用' }
  } as const

  const getCustomerStatusConfig = (status: string) => {
    return (
      CUSTOMER_STATUS_CONFIG[status as keyof typeof CUSTOMER_STATUS_CONFIG] || {
        type: 'info' as const,
        text: '未知'
      }
    )
  }

  // useTable 返回值: columns/data/loading/pagination/getData/replaceSearchParams/resetSearchParams/handleSizeChange/handleCurrentChange/refreshCreate/refreshUpdate/refreshRemove/refreshData
  const {
    columns,
    columnChecks,
    data,
    loading,
    pagination,
    getData,
    replaceSearchParams,
    resetSearchParams,
    handleSizeChange,
    handleCurrentChange,
    refreshCreate,
    refreshUpdate,
    refreshRemove,
    refreshData
  } = useTable({
    core: {
      apiFn: fetchGetCustomerList,
      apiParams: {
        current: 1,
        size: 20,
        ...searchForm.value
      },
      columnsFactory: () => [
        { type: 'index', width: 60, label: '序号' },
        { prop: 'name', label: '客户名称', minWidth: 200, showOverflowTooltip: true },
        { prop: 'contactName', label: '联系人', width: 120 },
        { prop: 'phone', label: '手机号', width: 140 },
        {
          prop: 'status',
          label: '状态',
          width: 100,
          formatter: (row: CustomerItem) => {
            const config = getCustomerStatusConfig(row.status)
            return h(ElTag, { type: config.type }, () => config.text)
          }
        },
        { prop: 'createdAt', label: '创建时间', width: 180 },
        {
          prop: 'operation',
          label: '操作',
          width: 140,
          fixed: 'right',
          formatter: (row: CustomerItem) =>
            h('div', [
              h(ArtButtonTable, {
                type: 'edit',
                onClick: () => showDialog('edit', row)
              }),
              h(ArtButtonTable, {
                type: 'delete',
                onClick: () => deleteCustomer(row)
              })
            ])
        }
      ]
    }
  })

  // 搜索回调: 替换参数 -> getData 回到第一页
  const handleSearch = (params: Api.CustomerManage.CustomerSearchParams) => {
    replaceSearchParams(params)
    getData()
  }

  // 打开弹窗: 设置类型和数据, nextTick 确保渲染后再显示
  const showDialog = (type: DialogType, row?: CustomerItem) => {
    dialogType.value = type
    currentCustomerData.value = row || {}
    nextTick(() => {
      dialogVisible.value = true
    })
  }

  // 删除: 确认框 -> fetchDelete -> refreshRemove(智能刷新)
  const deleteCustomer = async (row: CustomerItem) => {
    try {
      await ElMessageBox.confirm('确定要删除该客户吗？', '删除确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error'
      })
      await fetchDeleteCustomer(row.id)
      refreshRemove()
    } catch {
      // cancelled or error, do nothing
    }
  }

  // 提交: add 调 fetchCreate+refreshCreate, edit 调 fetchUpdate+refreshUpdate
  const handleDialogSubmit = async (data: Record<string, any>) => {
    try {
      if (dialogType.value === 'add') {
        await fetchCreateCustomer(data as unknown as Api.CustomerManage.CustomerCreateParams)
        refreshCreate()
      } else {
        await fetchUpdateCustomer({
          ...data,
          id: currentCustomerData.value.id
        } as unknown as Api.CustomerManage.CustomerUpdateParams)
        refreshUpdate()
      }
      dialogVisible.value = false
      currentCustomerData.value = {}
    } catch (error) {
      console.error('提交失败:', error)
    }
  }
</script>

<style lang="scss" scoped>
  .customer-page {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
</style>
