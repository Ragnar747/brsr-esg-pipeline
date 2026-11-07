# Setup guide (for complete beginners)

Do this once, in order. It takes about 1–2 hours. Everything here is free.

Commands are written for **Windows** (PowerShell, the default terminal in VS Code).
Where Mac is different, it says so.

---

## Part 1: Words you need to know

| Word | Meaning |
|---|---|
| **Git** | A program that saves the history of your project, like save points in a game |
| **Repository (repo)** | A project folder that Git is tracking |
| **Commit** | One save point, with a short message saying what changed |
| **Push** | Upload your commits to GitHub |
| **Pull** | Download commits from GitHub (needed when you work on two computers) |
| **GitHub** | A website that stores your repo online. Recruiters can see it |
| **Virtual environment (venv)** | A private box of Python packages for one project, so projects don't clash |
| **Terminal** | The window where you type commands |

---

## Part 2: Install the tools

### 2.1 Git
1. Download from **https://git-scm.com/downloads** and install. Keep all default options.
2. Close and reopen VS Code.
3. Open the terminal in VS Code: menu **Terminal → New Terminal** (or press `` Ctrl+` ``).
4. Check it works:
   ```
   git --version
   ```
   You should see something like `git version 2.4x`.
5. Tell Git who you are (use the email you'll use for GitHub):
   ```
   git config --global user.name "Shubham Gehlot"
   git config --global user.email "your-email@example.com"
   ```

### 2.2 GitHub account
1. Go to **https://github.com** and sign up (free).
2. Click **+** (top right) → **New repository**.
3. Name it `brsr-esg-pipeline`. Choose **Public** (so recruiters can see it).
4. **Do not** tick "Add a README" (the project already has one).
5. Click **Create repository**. Keep this page open; you'll need its URL.

### 2.3 VS Code extensions
In VS Code, click the **Extensions** icon on the left (four squares), search and install:
- **Python** (by Microsoft): runs and checks Python code
- **SQLite Viewer**: lets you open `data/brsr.db` and see the tables
- **Rainbow CSV**: makes CSV files easy to read

---

## Part 3: Open the project

1. Make a folder, e.g. `Documents\projects`.
2. Unzip `brsr-esg-pipeline.zip` into it.
3. In VS Code: **File → Open Folder** → choose `brsr-esg-pipeline`.
4. Open the terminal (`` Ctrl+` ``). It opens inside your project folder.

---

## Part 4: Create the virtual environment

```
python -m venv .venv
```

Turn it on:
```
.venv\Scripts\activate
```
- **Mac:** `source .venv/bin/activate`
- If Windows says *"running scripts is disabled"*, run this once, then try again:
  ```
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```

When it works, your terminal line starts with **(.venv)**. You need to turn it on
every time you open a new terminal.

Tell VS Code to use it: press `Ctrl+Shift+P` → type **Python: Select Interpreter** →
choose the one that mentions `.venv`.

Install the packages:
```
pip install -r requirements.txt
```

---

## Part 5: Check the project works

```
python pipelines/run.py init-db
python pipelines/run.py status
pytest
```

You should see:
- `Database ready` and `Metric catalog loaded: 22 metrics`
- a list of 8 tables
- `4 passed`

Open `data/brsr.db` in VS Code (click it in the file list). SQLite Viewer shows the
tables. Click `metric_catalog` to see the 22 labels.

---

## Part 6: Your first commit and push

Run these one at a time, from the project folder:

```
git init
git add .
git commit -m "Stage 1: project skeleton and database schema"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/brsr-esg-pipeline.git
git push -u origin main
```

What each line does:
1. `git init`: start tracking this folder
2. `git add .`: choose all changed files for the next save point
3. `git commit -m "..."`: create the save point with a message
4. `git branch -M main`: name the main line of work `main`
5. `git remote add origin ...`: connect to your GitHub repo (copy the URL from Part 2.2)
6. `git push -u origin main`: upload. A browser window opens the first time: log in to GitHub and approve.

Refresh your GitHub page: your files are online. Notice `data/` is **not** there;
`.gitignore` keeps the database and downloaded files on your computer only.

---

## Part 7: Your daily Git routine

After finishing a piece of work:

```
git status                      # see what changed
git add .                       # choose the changes
git commit -m "What you did"    # save point
git push                        # upload
```

Good commit messages say **what** changed, e.g.
`Stage 2: download XBRL files for 5 cement companies`.
Bad: `update`, `changes`, `final`.

**Pull** (`git pull`) is only needed if you change files on GitHub's website or work
on a second computer. Run it before you start working in that case.

**Prefer clicking?** VS Code's **Source Control** icon (left sidebar, branch symbol)
does the same: type a message, click **Commit**, then **Sync Changes**.

---

## Part 8: Later (stage 6 only): a free local AI

Download **Ollama** from **https://ollama.com**, install it, then in a terminal:
```
ollama pull llama3.1:8b
```
This downloads an open model (~5 GB) that runs on your own laptop. No API key, no cost.
If your laptop struggles, we'll pick a smaller model then.
