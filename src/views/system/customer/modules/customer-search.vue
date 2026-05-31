<template>
  <ArtSearchBar
    ref="searchBarRef"
    v-model="formData"
    :items="formItems"
    :rules="rules"
    @reset="handleReset"
    @search="handleSearch"
  />
</template>

<script setup lang="ts">
  // Props: modelValue=CustomerSearchParams(来自父页面 v-model, 定义在 api.d.ts)
  interface Props {
    modelValue: Api.CustomerManage.CustomerSearchParams
  }

  // Emits: search(查询)/reset(重置)/update:modelValue(v-model 双向绑定)
  interface Emits {
    (e: 'update:modelValue', value: Api.CustomerManage.CustomerSearchParams): void
    (e: 'search', params: Api.CustomerManage.CustomerSearchParams): void
    (e: 'reset'): void
  }

  const props = defineProps<Props>()
  const emit = defineEmits<Emits>()

  // ArtSearchBar 实例引用, 用于 handleSearch 中调用 validate()
  const searchBarRef = ref()

  const formData = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
  })

  // 校验规则(空=不校验, 必填验证在弹窗中做)
  const rules = {}

  // 状态下拉选项(模拟异步加载, 实际可替换为真实 API)
  const statusOptions = ref<{ label: string; value: string }[]>([])

  function fetchStatusOptions(): Promise<typeof statusOptions.value> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          { label: '启用', value: '1' },
          { label: '禁用', value: '2' }
        ])
      }, 500)
    })
  }

  onMounted(async () => {
    statusOptions.value = await fetchStatusOptions()
  })

  // 搜索表单项配置, ArtSearchBar 据此自动渲染 ElInput/ElSelect/ElDatePicker
  const formItems = computed(() => [
    {
      label: '客户名称',
      key: 'name',
      type: 'input',
      props: { placeholder: '请输入客户名称', clearable: true }
    },
    {
      label: '状态',
      key: 'status',
      type: 'select',
      props: { placeholder: '全部', clearable: true, options: statusOptions.value }
    },
    {
      label: '创建时间',
      key: 'createTime',
      type: 'daterange',
      props: {
        rangeSeparator: '~',
        startPlaceholder: '开始日期',
        endPlaceholder: '结束日期',
        valueFormat: 'YYYY-MM-DD',
        clearable: true
      }
    }
  ])

  // 重置: 通知父页面调 resetSearchParams
  function handleReset() {
    emit('reset')
  }

  // 搜索: validate -> daterange 拆为 startTime/endTime -> emit, 父页面调 replaceSearchParams+getData
  async function handleSearch(params: Api.CustomerManage.CustomerSearchParams) {
    await searchBarRef.value.validate()
    // daterange 类型会产生 createTime 字段，映射为 API 需要的 startTime/endTime
    const mappedParams: any = { ...params }
    if (mappedParams.createTime) {
      mappedParams.startTime = mappedParams.createTime[0] || null
      mappedParams.endTime = mappedParams.createTime[1] || null
      delete mappedParams.createTime
    }
    emit('search', mappedParams as Api.CustomerManage.CustomerSearchParams)
  }
</script>
