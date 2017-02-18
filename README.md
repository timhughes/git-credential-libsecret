 :no_entry_sign: This is here in case others find the code useful. The standard gnome-keyring integration provided with git now works. Use `git-credential-gnome-keyring` instead of this.  :no_entry_sign:

# git-credential-libsecret
Handles storing and providing usernames and passwords to Git using libsecret.

1. Download the file and make it executable and put it somewhere on your ``$PATH``.

1. Add it as a helper to your ``~/.gitconfig``
  ```
  [credential]                                                                    
     helper = !git-credential-libsecret.py
  ```

If you are useing [pyenv](https://github.com/yyuu/pyenv) or [virtualenv](https://virtualenv.pypa.io/en/latest/) and getting `ImportError` then change the hashbang (#!) at the top of the script to use your system python
