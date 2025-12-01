// /frontend/src/types/index.ts
/**
 * TypeScript interfaces for the Gantt Chart application.
 * All major data models are explicitly typed.
 */

export type UserRole = 'admin' | 'editor' | 'viewer'

export type SubTaskStatus = 'PLANNED' | 'IN_PROGRESS' | 'COMPLETED' | 'OVERDUE'

export type GanttScale = 'day' | 'week' | 'month'

export interface User {
  id: number
  email?: string
  full_name: string
  role: UserRole
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Activity {
  id: number
  name: string
  description: string | null
  start_date: string
  end_date: string
  owner_id: number
  owner?: User
  created_at: string
  updated_at: string
}

export interface Topic {
  id: number
  activity_id: number
  title: string
  description: string | null
  subtasks?: SubTask[]
  created_at: string
  updated_at: string
}

export interface SubTask {
  id: number
  topic_id: number
  title: string
  description: string | null
  start_date: string
  end_date: string
  status: SubTaskStatus
  assignee_id: number | null
  assignee?: User
  progress_percent: number
  created_at: string
  updated_at: string
}

export interface GanttData {
  activity: Activity
  topics: Topic[]
  subtasks: SubTask[]
  scale: GanttScale
  today: string
}

// API Response types
export interface LoginResponse {
  token: string
  user: User
}

export interface ApiError {
  error: string
}

// Create/Update DTOs
export interface CreateActivityDTO {
  name: string
  description?: string
  start_date: string
  end_date: string
}

export interface UpdateActivityDTO {
  name?: string
  description?: string | null
  start_date?: string
  end_date?: string
}

export interface CreateTopicDTO {
  title: string
  description?: string
}

export interface UpdateTopicDTO {
  title?: string
  description?: string | null
}

export interface CreateSubTaskDTO {
  title: string
  description?: string
  start_date: string
  end_date: string
  status?: SubTaskStatus
  assignee_id?: number | null
  progress_percent?: number
}

export interface UpdateSubTaskDTO {
  title?: string
  description?: string | null
  start_date?: string
  end_date?: string
  status?: SubTaskStatus
  assignee_id?: number | null
  progress_percent?: number
}

// Drag & Drop patch
export interface PatchSubTaskDTO {
  start_date?: string
  end_date?: string
  status?: SubTaskStatus
  progress_percent?: number
}

// User Management DTOs
export interface CreateUserDTO {
  email: string
  password: string
  full_name: string
  role?: UserRole
  is_active?: boolean
}

export interface UpdateUserDTO {
  email?: string
  full_name?: string
  role?: UserRole
  is_active?: boolean
}

export interface ChangePasswordDTO {
  old_password?: string  // Required for non-admin users
  new_password: string
}

export interface UsersResponse {
  users: User[]
}

export interface UserResponse {
  user: User
  message?: string
}

// FAZ-2: Notification types
export type NotificationType = 
  | 'TASK_CREATED'
  | 'TASK_UPDATED'
  | 'TASK_DELETED'
  | 'TASK_ASSIGNED'
  | 'TASK_COMPLETED'
  | 'TASK_OVERDUE'
  | 'DATE_CHANGED'
  | 'STATUS_CHANGED'

export interface Notification {
  id: number
  type: NotificationType
  message: string
  activity_id: number | null
  subtask_id: number | null
  target_user_id: number
  created_by_id: number | null
  is_read: boolean
  created_at: string
  // Populated relations
  created_by?: User
  activity?: { id: number; name: string }
  subtask?: { id: number; title: string }
}

export interface NotificationsResponse {
  notifications: Notification[]
  unread_count: number
}

