import type { NextConfig } from "next";
import path from "path";
import dotenv from "dotenv";

const { parsed: localEnv } = dotenv.config({
  path: path.resolve(__dirname, `../.env`),
});

const nextConfig: NextConfig = {
  env: {
    API_URL: `${localEnv?.BACKEND_URL}:${localEnv?.BACKEND_PORT}`,
  },
  devIndicators: false,
};

export default nextConfig;
