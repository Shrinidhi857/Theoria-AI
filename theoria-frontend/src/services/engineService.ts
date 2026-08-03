import { apiFetch } from "@/services/api"

export interface VideoResponse {
  id?: number
  status: string
  video: string
  video_url?: string
  topic: string
  prompt?: string
  extracted_parameters?: Record<string, any>
  approach?: Record<string, any>
  dsl_code?: any
  manim_code?: string
  created_at?: string
  usage_count?: number
  usage_limit?: number
}

export interface VideoHistoryItem {
  id: number
  topic: string
  prompt?: string
  status: string
  video_path?: string
  video_url?: string
  extracted_parameters?: Record<string, any>
  approach?: Record<string, any>
  dsl_code?: any
  manim_code?: string
  created_at: string
}

export interface UserUsageResponse {
  usage_count: number
  usage_limit: number
  is_limit_reached: boolean
}

export const engineService = {
  async generateVideo(topic: string): Promise<VideoResponse> {
    return apiFetch<VideoResponse>("/engine/generate", {
      method: "POST",
      body: JSON.stringify({ topic }),
      requiresAuth: false,
    })
  },

  async getUserVideos(skip = 0, limit = 50): Promise<VideoHistoryItem[]> {
    return apiFetch<VideoHistoryItem[]>(`/engine/videos?skip=${skip}&limit=${limit}`, {
      method: "GET",
      requiresAuth: true,
    })
  },

  async getUserUsage(): Promise<UserUsageResponse> {
    return apiFetch<UserUsageResponse>("/engine/usage", {
      method: "GET",
      requiresAuth: true,
    })
  },

  async getVideoById(videoId: number): Promise<VideoHistoryItem> {
    return apiFetch<VideoHistoryItem>(`/engine/videos/${videoId}`, {
      method: "GET",
      requiresAuth: false,
    })
  },
}
