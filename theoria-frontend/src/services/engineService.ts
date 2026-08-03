import { apiFetch } from "@/services/api"

export interface VideoResponse {
  id?: number
  status: string
  video: string
  topic: string
  extracted_parameters?: Record<string, any>
  approach?: Record<string, any>
  created_at?: string
}

export interface VideoHistoryItem {
  id: number
  topic: string
  status: string
  video_path?: string
  extracted_parameters?: Record<string, any>
  approach?: Record<string, any>
  created_at: string
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

  async getVideoById(videoId: number): Promise<VideoHistoryItem> {
    return apiFetch<VideoHistoryItem>(`/engine/videos/${videoId}`, {
      method: "GET",
      requiresAuth: false,
    })
  },
}
