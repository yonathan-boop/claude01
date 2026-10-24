---
name: google-drive
description: Script and credentials for Google Drive access (Methodist-11 documents)
metadata:
  node_type: memory
  type: reference
  originSessionId: 0611ce83-9a44-45c3-97b9-476137003ba6
  modified: 2026-10-24T01:35:57.975Z
---

Akses Google Drive via Node.js script tanpa dependensi eksternal.

- **Script:** `C:\Users\yonat\OPENCODE\COMMON\scripts\gdrive.js`
- **Kredensial:** `C:\Users\yonat\OPENCODE\COMMON\credentials\google_service_account.json`
- **Akun Service:** `hemers@rising-environs-510602-q2.iam.gserviceaccount.com`
- **Folder Utama:** `Methodist-11 Document` (`1iGiNuaMbIXxDvRYrcH6nY6hs7DE2m4s1`)

### Perintah CLI
- Tes koneksi: `node C:\Users\yonat\OPENCODE\COMMON\scripts\gdrive.js test`
- List file: `node C:\Users\yonat\OPENCODE\COMMON\scripts\gdrive.js list [query]`
- Detail file: `node C:\Users\yonat\OPENCODE\COMMON\scripts\gdrive.js get <fileId>`
- Download: `node C:\Users\yonat\OPENCODE\COMMON\scripts\gdrive.js download <fileId> <dest_path>`
- Upload: `node C:\Users\yonat\OPENCODE\COMMON\scripts\gdrive.js upload <file_path> [folderId]`
