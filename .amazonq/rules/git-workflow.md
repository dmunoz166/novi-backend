# Git Workflow Standards

## Branch Naming
- Use descriptive branch names with prefixes:
  - `feature/` for new features
  - `bugfix/` for bug fixes
  - `hotfix/` for urgent production fixes
  - `chore/` for maintenance tasks
- Use kebab-case: `feature/user-authentication`
- Keep names concise but descriptive

## Commit Practices
- Write clear, concise commit messages
- Use imperative mood: "Add user login" not "Added user login"
- Limit first line to 50 characters
- Include detailed description if needed after blank line
- Reference issue numbers when applicable: "Fix #123: Resolve login timeout"

## Merge Workflow
- Always create pull requests for code review
- Ensure all tests pass before merging
- Use squash and merge for feature branches
- Delete feature branches after successful merge
- Keep main/master branch clean and deployable

## Q Developer Actions
When working on development tasks, Q Developer should:
- Suggest appropriate branch names based on the task
- Recommend commit message structure
- Remind about running tests before commits
- Suggest when to create pull requests
- Advise on merge strategies based on branch type
