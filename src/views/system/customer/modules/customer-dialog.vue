<template>
  <ElDialog
    v-model="dialogVisible"
    :title="dialogType === 'add' ? '新增客户' : '编辑客户'"
    width="40%"
    align-center
  >
    <ElForm ref="formRef" :model="formData" :rules="rules" label-width="100px">
      <ElFormItem label="客户名称" prop="name">
        <ElInput v-model="formData.name" placeholder="请输入客户名称" />
      </ElFormItem>
      <ElRow :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="联系人" prop="contactName">
            <ElInput v-model="formData.contactName" placeholder="请输入联系人" />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="手机号" prop="phone">
            <ElInput v-model="formData.phone" placeholder="请输入手机号" />
          </ElFormItem>
        </ElCol>
      </ElRow>
      <ElRow :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="邮箱" prop="email">
            <ElInput v-model="formData.email" placeholder="请输入邮箱" />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="状态" prop="status">
            <ElSelect v-model="formData.status">
              <ElOption label="启用" value="1" />
              <ElOption label="禁用" value="2" />
            </ElSelect>
          </ElFormItem>
        </ElCol>
      </ElRow>
      <ElFormItem label="地址" prop="address">
        <ElInput v-model="formData.address" placeholder="请输入地址" />
      </ElFormItem>
      <ElFormItem label="备注" prop="remark">
        <ElInput v-model="formData.remark" type="textarea" :rows="3" placeholder="请输入备注" />
      </ElFormItem>
    </ElForm>
    <template #footer>
      <div class="dialog-footer">
        <ElButton @click="dialogVisible = false">取消</ElButton>
        <ElButton type="primary" @click="handleSubmit">提交</ElButton>
      </div>
    </template>
  </ElDialog>
</template>

<script setup lang="ts">
  import type { FormInstance, FormRules } from 'element-plus'

  // Props: visible(显隐/v-model)/type(add或edit)/customerData(编辑时当前行)
  interface Props {
    visible: boolean
    type: string
    customerData?: Partial<Api.CustomerManage.CustomerListItem>
  }

  // Emits: update:visible(关闭)/submit(提交数据给父页面调 API)
  interface Emits {
    (e: 'update:visible', value: boolean): void
    (e: 'submit', data: Record<string, any>): void
  }

  const props = defineProps<Props>()
  const emit = defineEmits<Emits>()

  // 弹窗显隐双向绑定: get 从 props 读, set emit 通知父组件更新 v-model
  const dialogVisible = computed({
    get: () => props.visible,
    set: (value) => emit('update:visible', value)
  })

  const dialogType = computed(() => props.type)
  // ElForm 实例引用, 用于调用 validate() 和 clearValidate()
  const formRef = ref<FormInstance>()

  // 表单响应式数据, status 默认 '1'(启用)
  const formData = reactive({
    name: '',
    contactName: '',
    phone: '',
    email: '',
    status: '1',
    address: '',
    remark: ''
  })

  // 表单校验规则: name/contactName/phone/email 必填, phone 正则, email 类型校验
  const rules: FormRules = {
    name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
    contactName: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
    phone: [
      { required: true, message: '请输入手机号', trigger: 'blur' },
      { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
    ],
    email: [
      { required: true, message: '请输入邮箱', trigger: 'blur' },
      { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
    ]
  }

  // 初始化: 新增置空, 编辑从 customerData 填充
  const initFormData = () => {
    const isEdit = props.type === 'edit' && props.customerData
    const row = props.customerData

    Object.assign(formData, {
      name: isEdit && row ? row.name || '' : '',
      contactName: isEdit && row ? row.contactName || '' : '',
      phone: isEdit && row ? row.phone || '' : '',
      email: isEdit && row ? row.email || '' : '',
      status: isEdit && row ? row.status || '1' : '1',
      address: isEdit && row ? row.address || '' : '',
      remark: isEdit && row ? row.remark || '' : ''
    })
  }

  // 监听弹窗: visible=true 时 initFormData + 清除校验状态
  watch(
    () => [props.visible, props.type, props.customerData],
    ([visible]) => {
      if (visible) {
        initFormData()
        nextTick(() => {
          formRef.value?.clearValidate()
        })
      }
    },
    { immediate: true }
  )

  // 提交: validate -> emit submit -> 父页面调 API -> 关闭弹窗
  const handleSubmit = async () => {
    if (!formRef.value) return
    await formRef.value.validate((valid) => {
      if (valid) {
        emit('submit', { ...formData })
        dialogVisible.value = false
      }
    })
  }
</script>
