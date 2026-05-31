import request from '@/utils/http'

/** 获取客户列表 */
export function fetchGetCustomerList(params: Api.CustomerManage.CustomerSearchParams) {
  return request.get<Api.CustomerManage.CustomerList>({
    url: '/api/customer/list',
    params
  })
}

/** 新增客户 */
export function fetchCreateCustomer(params: Api.CustomerManage.CustomerCreateParams) {
  return request.post<null>({
    url: '/api/customer/create',
    params,
    showSuccessMessage: true
  })
}

/** 编辑客户 */
export function fetchUpdateCustomer(params: Api.CustomerManage.CustomerUpdateParams) {
  return request.put<null>({
    url: '/api/customer/update',
    params,
    showSuccessMessage: true
  })
}

/** 删除客户 */
export function fetchDeleteCustomer(id: number) {
  return request.del<null>({
    url: '/api/customer/delete',
    params: { id },
    showSuccessMessage: true
  })
}
