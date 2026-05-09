export type TagNode = {
  name: string;
  children?: TagNode[];
  data?: string;
};

export type TreeRecord = {
  id: number;
  tree: TagNode;
  created_at: string;
  updated_at: string;
};

export type TreeDraft = {
  clientId: string;
  id?: number;
  tree: TagNode;
  exportedJson?: string;
  status?: string;
  saving?: boolean;
};

