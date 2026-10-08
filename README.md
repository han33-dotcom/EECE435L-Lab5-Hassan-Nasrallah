# EECE435L Lab 5 Postman and APIs

Hassan Nasrallah

A Flask REST API for managing users in SQLite, with the `Flask user app`
Postman collection, saved response examples, and the `Flask local` environment.

## Run the app

From this project folder in PowerShell, with Python 3.12 or newer:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

The server listens at `http://127.0.0.1:5000`. It creates `database.db` and the
`users` table automatically. `sqlite3` is included with Python. The database
path is relative to the source file, so changing the working directory does
not create a different database.

## Postman graded exercise

1. Import `postman/Flask_user_app.postman_collection.json` into Postman.
2. Import `postman/Flask_local.postman_environment.json`.
3. Select the **Flask local** environment.
4. Open **Flask user app** and run the six requests in their numbered order.
5. Expand each request to view its saved response example.

Every request uses `{{base_url}}`, an environment variable containing
`http://127.0.0.1:5000`. After adding a user, the test script saves the returned
`user_id` into the environment. Later requests use that value rather than a
hard-coded ID. The PUT body includes `"user_id": {{user_id}}` without quotes
around the variable because the API expects an integer.

The six saved examples contain real response bodies captured from the running
API. The first five requests cover all required CRUD endpoints; the sixth
confirms that a deleted user returns HTTP 404. Successful POST returns 201,
successful GET/PUT/DELETE return 200, invalid fields return 400, and a missing
user returns 404. POST and PUT use raw JSON and `Content-Type: application/json`.

Postman's current desktop version requires signing in to use collections and
environments. Its Lightweight API Client can send individual requests without
an account. These exports are also executable with Newman:

```powershell
npx newman run postman/Flask_user_app.postman_collection.json -e postman/Flask_local.postman_environment.json
```

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/users` | List users |
| GET | `/api/users/<user_id>` | Retrieve one user |
| POST | `/api/users/add` | Create a user |
| PUT | `/api/users/update` | Update the specified user |
| DELETE | `/api/users/delete/<user_id>` | Delete the specified user |

User fields: `user_id`, `name`, `email`, `phone`, `address`, `country`.
SQLite generates `user_id`; it is omitted from the POST body.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

- Python: 5 tests passed, covering CRUD persistence, invalid input, missing IDs,
  parameterized SQL with quoted text, and JSON/CORS behavior.
- Newman: 6 requests and 22 assertions passed with no failures.
- Raw execution results are in `verification/`.
- Uncropped full-screen evidence is in `screenshots/`.

## Git and GitHub

Repository: https://github.com/han33-dotcom/EECE435L-Lab5-Hassan-Nasrallah

The SQLite implementation was committed on `main`. The Flask implementation
and tests were committed on `codex/rest-api`, then merged into `main` with a
merge commit. Both branches were pushed to GitHub. The collection, environment,
report and evidence are included in the final submission commit.

## References

- Lab5-Postman and APIs.docx, supplied course handout.
- https://learning.postman.com/docs/getting-started/first-steps/overview/
- https://learning.postman.com/docs/sending-requests/requests/
