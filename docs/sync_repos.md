## Background
Step by step guidance to:
(1) do the migration, create new GitHub repo and migrate the legacy repo content to the new repo, in consideration of the original repo have GitHub page, branches, workflow, published package and wiki etc.
(2) do the sync up, set up sync up mechanism from one GitHub repo to another once there are files changes or periodically timer expired, note the repo to sync files from are public and the repo to sync files to are private.

## Proposal

### do the migration
Here is a detailed step-by-step guide to migrate a GitHub repo to a new GitHub repo, preserving GitHub Pages, branches, workflows, published packages, and wiki:

#### Step 1: Mirror the original repo

1. Clone the original repo using the `--mirror` flag to include all branches and tags:
   ```
   git clone --mirror https://github.com/username/original-repo.git
   ```
2. Change into the cloned repo directory:
   ```
   cd original-repo.git
   ```

#### Step 2: Create a new empty GitHub repo

1. Go to https://github.com/new
2. Enter a name for the new repository, but do not initialize it with a README, license, or .gitignore
3. Click "Create repository"

#### Step 3: Push the mirrored repo to the new GitHub repo

1. Set the new repo as the remote origin:
   ```
   git remote set-url origin https://github.com/username/new-repo.git
   ```
2. Push all branches and tags to the new repo:
   ```
   git push --mirror
   ```

#### Step 4: Configure GitHub Pages in the new repo

1. Go to the new repo's settings on GitHub
2. Scroll down to the "GitHub Pages" section
3. Select the branch and directory for your GitHub Pages site (e.g., `main` branch and `/docs` folder)
4. Click "Save"

#### Step 5: Migrate GitHub Actions workflows

1. If your original repo had any GitHub Actions workflows (in the `.github/workflows` directory), they should have been copied over in Step 3
2. Review the workflows in the new repo and update any references to the old repo name

#### Step 6: Migrate published packages

1. If you had any packages published from the original repo, you'll need to update the package metadata to point to the new repo
2. For each package, update the repository URL in the package's configuration file (e.g., `package.json` for npm, `setup.py` for Python)
3. Publish the updated packages from the new repo

#### Step 7: Migrate the wiki

1. Clone the original repo's wiki:
   ```
   git clone https://github.com/username/original-repo.wiki.git
   ```
2. Change into the cloned wiki directory:
   ```
   cd original-repo.wiki
   ```
3. Set the new repo's wiki as the remote origin:
   ```
   git remote set-url origin https://github.com/username/new-repo.wiki.git
   ```
4. Push the wiki to the new repo:
   ```
   git push origin master
   ```

After completing these steps, your new GitHub repo should have all the content, branches, tags, GitHub Pages, workflows, packages, and wiki from the original repo. Remember to update any references to the old repo URL in your project's documentation, README, and other relevant places.

### do the sync up
Syncing files from one GitHub repository to another can be accomplished using a few different methods, including manually copying files, using webhooks for automatic updates, or setting up a scheduled job to sync periodically. For a repository where you want to periodically sync changes from a public repo to a private one, you can use GitHub Actions or set up a cron job on a server that has access to both repositories.

Here's a step-by-step guide to setting up a GitHub Action to sync changes from a public repository to a private one:

#### Step 1: Set up the Private Repository

1. **Create a private repository** on GitHub if you haven't already.
2. **Generate a personal access token (PAT)** that will be used to authenticate and provide the necessary permissions to sync the repositories:
   - Go to your GitHub settings.
   - Select "Developer settings" from the sidebar.
   - Click on "Personal access tokens".
   - Generate a new token with the appropriate permissions (at least `repo` scope for private repos).
3. **Add the PAT as a secret** to your private repository:
   - Go to the settings of your private repository.
   - Click on "Secrets" in the sidebar.
   - Add a new secret, name it something like `REPO_SYNC_PAT`, and paste the personal access token you generated.

#### Step 2: Set up GitHub Actions in the Private Repository

1. In your private repository, create a new directory named `.github` and within it another directory named `workflows` if they don't already exist.
2. Inside the `workflows` directory, create a new file for your sync workflow, such as `sync.yml`.
3. Edit `sync.yml` to define the workflow. Here's a basic example of what the file might look like:

```yaml
name: Sync Public Repo to Private Repo

on:
  schedule:
    - cron: '0 * * * *'  # This sets the action to run every hour

jobs:
  repo-sync:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout private repo
      uses: actions/checkout@v2
      with:
        repository: <username>/<private-repo-name>
        token: ${{ secrets.REPO_SYNC_PAT }}
        path: private-repo

    - name: Pull changes from public repo
      run: |
        cd private-repo
        git pull https://github.com/<username>/<public-repo-name>.git main  # Replace 'main' with default branch if different

    - name: Push changes to private repo
      run: |
        cd private-repo
        git config user.name 'GitHub Action'
        git config user.email 'action@github.com'
        git add .
        git commit -m 'Sync public repository updates'
        git push
```

Replace `<username>`, `<private-repo-name>`, and `<public-repo-name>` with the appropriate names for your repositories. Also, replace `main` with the name of the default branch if it's different.

#### Step 3: Commit and Push the Workflow File

1. Commit the `.github/workflows/sync.yml` file to your private repository.
2. Push the commit to GitHub.

#### Step 4: Verify the Action

1. After pushing the workflow file to your private repository, navigate to the "Actions" tab of your private repository on GitHub.
2. You should see the workflow you've just created. It will run according to the schedule you've set (in this case, every hour).
3. Verify that the action completes successfully. If there are any issues, the logs provided by GitHub Actions will be helpful in troubleshooting.

### Additional Notes

- Complex scenario not considered for now e.g. handling merge conflicts or only syncing certain files.
- The cron schedule syntax in the GitHub Action allows you to run the workflow at specific times. The example provided runs it every hour. Adjust the cron schedule according to your needs.
- Always be cautious with personal access tokens.
