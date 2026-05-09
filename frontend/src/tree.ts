import type { TagNode } from "./types";

export const starterTree: TagNode = {
  name: "root",
  children: [
    {
      name: "child1",
      children: [
        { name: "child1-child1", data: "c1-c1 Hello" },
        { name: "child1-child2", data: "c1-c2 JS" },
      ],
    },
    { name: "child2", data: "c2 World" },
  ],
};

export const newChild = (): TagNode => ({
  name: "New Child",
  data: "Data",
});

export const createClientId = () => {
  if ("crypto" in window && "randomUUID" in window.crypto) {
    return window.crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

export const cloneTree = (tree: TagNode): TagNode => ({
  name: tree.name,
  ...(tree.children
    ? { children: tree.children.map((child) => cloneTree(child)) }
    : { data: tree.data ?? "" }),
});

export const cleanTree = cloneTree;

export const formatJson = (tree: TagNode) => JSON.stringify(cleanTree(tree), null, 2);

