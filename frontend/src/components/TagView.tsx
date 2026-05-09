import { CSSProperties, KeyboardEvent, useEffect, useRef, useState } from "react";

import { newChild } from "../tree";
import type { TagNode } from "../types";

type TagViewProps = {
  node: TagNode;
  depth?: number;
  onChange: (node: TagNode) => void;
};

export function TagView({ node, depth = 0, onChange }: TagViewProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [editingName, setEditingName] = useState(false);
  const [draftName, setDraftName] = useState(node.name);
  const nameInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editingName) {
      nameInputRef.current?.focus();
      nameInputRef.current?.select();
    }
  }, [editingName]);

  useEffect(() => {
    if (!editingName) {
      setDraftName(node.name);
    }
  }, [editingName, node.name]);

  const addChild = () => {
    // A leaf tag becomes a parent tag as soon as a child is added, matching the
    // assignment rule that a tag cannot keep data and children at the same time.
    onChange({
      name: node.name,
      children: [...(node.children ?? []), newChild()],
    });
  };

  const updateChild = (index: number, child: TagNode) => {
    if (!node.children) {
      return;
    }

    const children = node.children.map((current, currentIndex) =>
      currentIndex === index ? child : current,
    );
    onChange({ name: node.name, children });
  };

  const updateData = (data: string) => {
    onChange({ name: node.name, data });
  };

  const commitName = () => {
    const name = draftName.trim();
    if (!name) {
      // Empty names are ignored so the exported tree always stays valid.
      setDraftName(node.name);
      setEditingName(false);
      return;
    }

    onChange(node.children ? { ...node, name } : { name, data: node.data ?? "" });
    setEditingName(false);
  };

  const handleNameKey = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      commitName();
    }

    if (event.key === "Escape") {
      setDraftName(node.name);
      setEditingName(false);
    }
  };

  const style = { "--depth": depth } as CSSProperties;

  return (
    <section className="tag-node" style={style}>
      <header className="tag-header">
        <button
          className="collapse-toggle"
          type="button"
          onClick={() => setCollapsed((value) => !value)}
          aria-label={collapsed ? "Expand tag" : "Collapse tag"}
        >
          {collapsed ? ">" : "v"}
        </button>

        {editingName ? (
          <input
            ref={nameInputRef}
            className="tag-name-input"
            value={draftName}
            onChange={(event) => setDraftName(event.target.value)}
            onBlur={commitName}
            onKeyDown={handleNameKey}
          />
        ) : (
          <button className="tag-name" type="button" onClick={() => setEditingName(true)}>
            {node.name}
          </button>
        )}

        <button className="add-child-button" type="button" onClick={addChild}>
          + Add Child
        </button>
      </header>

      {!collapsed && (
        <div className="tag-content">
          {node.children ? (
            <div className="children-list">
              {/* Recursion keeps TagView responsible for one node at a time. */}
              {node.children.map((child, index) => (
                <TagView
                  key={`${child.name}-${index}`}
                  node={child}
                  depth={depth + 1}
                  onChange={(updatedChild) => updateChild(index, updatedChild)}
                />
              ))}
            </div>
          ) : (
            <label className="data-field">
              <span>Data</span>
              <input
                value={node.data ?? ""}
                onChange={(event) => updateData(event.target.value)}
              />
            </label>
          )}
        </div>
      )}
    </section>
  );
}
