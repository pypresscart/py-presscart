# Resource: Files

Upload assets (brand guides, writing samples, images) and manage them.

```python
client.files  # FilesResource
```

## Methods overview

| Method | HTTP | Scope |
|---|---|---|
| [`list`](#list) | `GET /files` | `files.lists` |
| [`get`](#get) | `GET /files/{file_id}` | `files.read` |
| [`upload`](#upload) | `POST /files/upload` | `files.create` |
| [`download`](#download) | `GET /files/{file_id}/download` | `files.read` |
| [`move`](#move) | `POST /files/move` | `files.update` |
| [`delete`](#delete) | `DELETE /files/{file_id}` | `files.delete` |

---

### `list`

```python
def list(
    *,
    limit: int = 25,
    page: int = 1,
    sort_by: str | None = None,
    order_by: str | None = None,
    q: str | None = None,
    folder_id: str | None = None,
    as_json: bool | None = None,
) -> Paginated[File] | dict
```

Pass `q="..."` to search by filename, `folder_id="..."` to scope to one folder.

---

### `get`

```python
def get(
    file_id: str,
    *,
    as_json: bool | None = None,
) -> File | dict
```

`file_id` accepts either the UUID `id` or the `file_key`.

---

### `upload`

```python
def upload(
    files,           # see below
    *,
    folder_id: str | None = None,
    as_json: bool | None = None,
) -> UploadFilesResponse | dict
```

**`files`** accepts any of:

- A path (`str` or `pathlib.Path`)
- An open binary file handle (`io.BytesIO`, `open(..., "rb")`)
- A `(filename, fileobj, content_type)` tuple (for custom filename or content type)
- A list mixing any of the above (up to 5 per request)

**Limits** (server-enforced):
- Images (`jpg`, `jpeg`, `png`, `webp`): max 5 MB each
- Documents (`docx`, `pdf`, `txt`): max 25 MB each
- 1–5 files per request

**Examples**

```python
from pathlib import Path

# Single path
resp = client.files.upload(Path("brand-guide.pdf"))

# Multiple files, targeting a folder
resp = client.files.upload(
    [Path("a.png"), Path("b.png"), Path("c.png")],
    folder_id="fld_1",
)

# From an in-memory buffer with a custom name
import io
buf = io.BytesIO(pdf_bytes)
resp = client.files.upload([("report.pdf", buf, "application/pdf")])

for f in resp.files:
    print(f.id, f.file_url, f.size)
```

`pypresscart` opens any file paths you pass and closes them automatically.

---

### `download`

```python
def download(
    file_id: str,
) -> bytes
```

Returns the raw bytes of the file. **This method does not support dual-mode** — there's no JSON to return.

```python
data = client.files.download("file_1")
Path("local-copy.pdf").write_bytes(data)
```

For very large files, consider an alternative transport — this endpoint reads the full response into memory.

---

### `move`

```python
def move(
    body: MoveFilesRequest | BaseModel | dict,
    *,
    as_json: bool | None = None,
) -> MoveFilesResponse | dict
```

**Body** ([`MoveFilesRequest`](models-reference.md#movefilesrequest)):

| Field | Type | Notes |
|---|---|---|
| `file_ids` | `list[str]` | 1–50 per call |
| `folder_id` | `str \| None` | `None` moves to root |

```python
from pypresscart import MoveFilesRequest

client.files.move(
    MoveFilesRequest(file_ids=["f_1", "f_2"], folder_id="fld_archive")
)
# MoveFilesResponse(moved_count=2)
```

---

### `delete`

```python
def delete(
    file_id: str,
    *,
    as_json: bool | None = None,
) -> DeleteFileResponse | dict
```

Returns `{"success": true}`.

## Recipes

### Upload and link to a campaign questionnaire

```python
uploaded = client.files.upload("writing-samples.docx").files[0]

client.campaigns.link_questionnaire(
    "cmp_1",
    {
        "file_id": uploaded.file_key,
        "file_url": uploaded.file_url,
        "file_name": uploaded.name,
        "file_size": uploaded.size,
    },
)
```

### Cleanup old files

```python
from datetime import datetime, timedelta, timezone

cutoff = datetime.now(timezone.utc) - timedelta(days=90)
page = client.files.list(limit=200, sort_by="created_at", order_by="asc")
stale = [f.id for f in page.records if f.created_at and f.created_at < cutoff]
for file_id in stale:
    client.files.delete(file_id)
```
