export const formatDate = (dateString: string): string => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
};

export const getFullVideoUrl = (videoPath: string | null | undefined): string => {
  if (!videoPath) return "";
  if (videoPath.startsWith("http://") || videoPath.startsWith("https://")) {
    return videoPath;
  }
  // Normalize Windows backslashes if any
  const normalized = videoPath.replace(/\\/g, "/");
  const cleanPath = normalized.startsWith("/") ? normalized : `/${normalized}`;
  
  // If path contains output/, serve via backend static endpoint
  const backendServer = import.meta.env.VITE_BACKEND_SERVER_URL || "http://localhost:8000";
  if (cleanPath.includes("output")) {
    const filename = cleanPath.split("output/").pop();
    return `${backendServer}/output/${filename}`;
  }
  
  return `${backendServer}${cleanPath}`;
};
