import { get, post } from './client'
import type { DataExportResponse, DataDeleteRequest, DataDeleteResponse } from '@/types/api'

export function exportData(): Promise<DataExportResponse> {
  return get<DataExportResponse>('/api/data/export')
}

export function deleteData(body: DataDeleteRequest): Promise<DataDeleteResponse> {
  return post<DataDeleteResponse>('/api/data/delete', body)
}
