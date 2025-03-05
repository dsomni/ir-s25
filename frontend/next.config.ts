import type { NextConfig } from "next";
const path = require("path");
const dotenv = require("dotenv");

const { parsed: localEnv } = dotenv.config({
  allowEmptyValues: false,
  path: path.resolve(__dirname, `../.env`),
});

const nextConfig: NextConfig = {
  env: {
    API_URL: `${localEnv.BACKEND_URL}:${localEnv.BACKEND_PORT}`,
  },
};

export default nextConfig;
