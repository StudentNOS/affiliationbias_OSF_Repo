## This is the contribution policy for the authors 
## Making Changes

1. **Work Privately**: With your private repository, you can freely make changes without public visibility. Feel free to experiment with new code or work with confidential data.

2. **Commit Your Changes**: After making your changes, commit them in your local affiliationbias repository.

   ```
   git add .
   git commit -m "Describe your changes here"
   ```

## Sharing Your Changes

When you're ready to make some changes public, create a patch and apply it to the public affiliationbias repository:

1. **Create a Patch**: This command generates a patch file containing all changes made since the last commit:

   ```
   git diff > changes.patch
   ```

2. **Apply the Patch to the Public affiliationbias Repository**: First, move the patch file to your local affiliation bias repository. Then, from the root directory of your local public repository, apply the patch:

   ```
   git apply path_to_your_patch/changes.patch
   ```

3. **Commit and Push**: Now commit these changes and push to the public repository:

   ```
   git add .
   git commit -m "Applying changes from affiliation bias"
   git push origin master
   ```

Note: If you are comfortable with advanced Git operations, you could also consider using `git merge` or `git rebase` to combine your changes. Be careful with these operations, ensure you understand them well!

---