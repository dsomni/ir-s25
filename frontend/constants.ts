export const indexerMap: Map<string, string> = new Map<string, string>([
  ["llm_tree_idx", "LLM + Tree"],
  ["inverted_idx", "Inverted Index"],
]);

export interface Proposal {
  document: string;
  score: number;
}
export const THINK_REGEX = /<think>.*?<\/think>/gs;
