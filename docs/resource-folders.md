# Folders

Organize uploaded files into folders.

```python
client.folders  # FoldersResource
```

## Methods overview

| Method | HTTP | Scope |
|---|---|---|
| [`list`](#list) | `GET /folders` | `folders.lists` |
| [`create`](#create) | `POST /folders` | `folders.create` |
| [`rename`](#rename) | `PATCH /folders/{id}` | `folders.update` |
| [`delete`](#delete) | `DELETE /folders/{id}` | `folders.delete` |

---

### `list`

```python
def list(
    *,
    q: str | None = None,
    as_json: bool | None = None,
) -> Paginated[Folder] | dict
```

`q` filters by folder name.

```python
page = client.folders.list()
for folder in page.records:
    print(folder.id, folder.name)
```

---

### `create`

```python
def create(
    body: FolderCreateRequest | BaseModel | dict,
    *,
    as_json: bool | None = None,
) -> Folder | dict
```

```python
folder = client.folders.create({"name": "Q3 Assets"})
print(folder.id)
```

---

### `rename`

```python
def rename(
    folder_id: str,
    body: FolderRenameRequest | BaseModel | dict,
    *,
    as_json: bool | None = None,
) -> Folder | dict
```

```python
client.folders.rename("fld_1", {"name": "Q3 Assets (Archived)"})
```

---

### `delete`

```python
def delete(
    folder_id: str,
    *,
    as_json: bool | None = None,
) -> DeleteFolderResponse | dict
```

> **Files inside the folder are not deleted.** They lose their folder association and become uncategorized.

```python
client.folders.delete("fld_1")
```

## Recipes

### Create a folder and upload directly into it

```python
folder = client.folders.create({"name": "Brand Assets 2026"})

client.files.upload(
    ["logo.png", "brand-guide.pdf"],
    folder_id=folder.id,
)
```

### Find or create

```python
page = client.folders.list(q="Brand Assets 2026")
if page.records:
    folder = page.records[0]
else:
    folder = client.folders.create({"name": "Brand Assets 2026"})
```
