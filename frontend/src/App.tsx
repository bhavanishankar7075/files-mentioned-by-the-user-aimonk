import { useEffect, useMemo, useState } from "react";

import { createTree, fetchTrees, updateTree } from "./api";
import { TagView } from "./components/TagView";
import { cleanTree, cloneTree, createClientId, formatJson, starterTree } from "./tree";
import type { TagNode, TreeDraft } from "./types";

const makeDraft = (tree: TagNode = starterTree, id?: number): TreeDraft => ({
  clientId: createClientId(),
  id,
  tree: cloneTree(tree),
});

function App() {
  const [trees, setTrees] = useState<TreeDraft[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    let active = true;

    fetchTrees()
      .then((records) => {
        if (!active) {
          return;
        }

        setTrees(records.length ? records.map((record) => makeDraft(record.tree, record.id)) : [makeDraft()]);
      })
      .catch(() => {
        if (!active) {
          return;
        }

        setLoadError("Backend is not reachable yet. You can still edit the starter tree.");
        setTrees([makeDraft()]);
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const savedCount = useMemo(() => trees.filter((tree) => tree.id).length, [trees]);

  const updateDraftTree = (clientId: string, tree: TagNode) => {
    setTrees((current) =>
      current.map((draft) =>
        draft.clientId === clientId
          ? { ...draft, tree, exportedJson: undefined, status: undefined }
          : draft,
      ),
    );
  };

  const addTree = () => {
    setTrees((current) => [...current, makeDraft()]);
  };

  const exportTree = async (clientId: string) => {
    const draft = trees.find((tree) => tree.clientId === clientId);
    if (!draft) {
      return;
    }

    const tree = cleanTree(draft.tree);
    const exportedJson = formatJson(tree);

    setTrees((current) =>
      current.map((item) =>
        item.clientId === clientId
          ? { ...item, exportedJson, saving: true, status: "Saving..." }
          : item,
      ),
    );

    try {
      const saved = draft.id ? await updateTree(draft.id, tree) : await createTree(tree);
      setTrees((current) =>
        current.map((item) =>
          item.clientId === clientId
            ? {
                ...item,
                id: saved.id,
                tree: saved.tree,
                exportedJson,
                saving: false,
                status: draft.id ? "Updated in database" : "Saved in database",
              }
            : item,
        ),
      );
    } catch {
      setTrees((current) =>
        current.map((item) =>
          item.clientId === clientId
            ? {
                ...item,
                exportedJson,
                saving: false,
                status: "Exported locally. Database save failed.",
              }
            : item,
        ),
      );
    }
  };

  return (
    <main className="app-shell">
      <div className="topbar">
        <div>
          <p className="eyebrow">AIMonk assignment</p>
          <h1>Nested Tags Tree</h1>
        </div>
        <div className="topbar-actions">
          <span className="saved-count">{savedCount} saved</span>
          <button className="secondary-button" type="button" onClick={addTree}>
            + New Tree
          </button>
        </div>
      </div>

      {loadError && <div className="notice">{loadError}</div>}

      {loading ? (
        <div className="loading-panel">Loading trees...</div>
      ) : (
        <div className="tree-stack">
          {trees.map((draft, index) => (
            <article className="tree-panel" key={draft.clientId}>
              <div className="tree-panel-header">
                <div>
                  <p className="tree-kicker">{draft.id ? `Record #${draft.id}` : "Unsaved draft"}</p>
                  <h2>Tree {index + 1}</h2>
                </div>
                <button
                  className="export-button"
                  type="button"
                  disabled={draft.saving}
                  onClick={() => exportTree(draft.clientId)}
                >
                  {draft.saving ? "Saving..." : "Export"}
                </button>
              </div>

              <TagView node={draft.tree} onChange={(tree) => updateDraftTree(draft.clientId, tree)} />

              {(draft.status || draft.exportedJson) && (
                <div className="export-area">
                  {draft.status && <p className="status-line">{draft.status}</p>}
                  {draft.exportedJson && <pre>{draft.exportedJson}</pre>}
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </main>
  );
}

export default App;

