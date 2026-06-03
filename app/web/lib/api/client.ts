export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? ''

export const isRestApiConfigured = () => API_BASE_URL.length > 0
