# AIMonk Nested Tags Tree

Full-stack coding assignment for rendering, editing, exporting, saving, loading, and updating recursive tag trees.

## Tech Stack

- Frontend: React, TypeScript, Vite
- Backend: FastAPI, SQLAlchemy
- Database: SQLite

SQLite is used so the project can be reviewed locally without extra database setup. The backend stores each tree in a normalized SQL schema with a tree record table and recursive tag node table.

## Features

- Recursive `TagView` component for nested tag trees
- Editable `data` fields
- Recursive collapse and expand controls
- `Add Child` behavior that converts a data node into a children node
- Export button that prints clean JSON with only `name`, `children`, and `data`
- Export also saves new trees through `POST /api/trees`
- Export updates existing saved trees through `PUT /api/trees/{id}`
- Initial frontend load fetches all saved trees through `GET /api/trees`
- Multiple saved trees render one below another
- Bonus: click a tag name, edit it, and press Enter to save

## Project Structure

```txt
backend/
  app/
    main.py
    database.py
    models.py
    schemas.py
    tree_store.py
  requirements.txt

frontend/
  src/
    components/TagView.tsx
    App.tsx
    api.ts
    tree.ts
    types.ts
    styles.css
  package.json
```

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## API

### `GET /api/trees`

Returns all saved tree hierarchy records.

### `POST /api/trees`

Saves a new tree hierarchy.

```json
{
  "tree": {
    "name": "root",
    "children": [
      {
        "name": "child1",
        "children": [
          { "name": "child1-child1", "data": "c1-c1 Hello" }
        ]
      }
    ]
  }
}
```

### `PUT /api/trees/{id}`

Replaces the hierarchy for an existing saved tree.

## Environment

Create `frontend/.env.local` only if the backend is not running on port `8000`.

```txt
VITE_API_BASE_URL=http://localhost:8000
```

