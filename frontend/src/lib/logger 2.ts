export const logger = {
  info: (message: string, data?: unknown) => {
    if (process.env.NODE_ENV !== "production") {
      console.log(`[INFO] ${message}`, data);
    }
  },
  error: (message: string, error?: unknown) => {
    console.error(`[ERROR] ${message}`, error);
  },
  warn: (message: string, data?: unknown) => {
    console.warn(`[WARN] ${message}`, data);
  },
};
