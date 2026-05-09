import type { TagNode, TreeRecord } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  // Centralizing fetch handling keeps the component code focused on tree
  // behavior instead of response parsing and error checks.
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export const fetchTrees = () => request<TreeRecord[]>("/api/trees");

export const createTree = (tree: TagNode) =>
  request<TreeRecord>("/api/trees", {
    method: "POST",
    body: JSON.stringify({ tree }),
  });

export const updateTree = (id: number, tree: TagNode) =>
  request<TreeRecord>(`/api/trees/${id}`, {
    method: "PUT",
    body: JSON.stringify({ tree }),
  });
