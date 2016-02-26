# git-credential-libsecret
Handles storing and providing usernames and passwords to Git using libsecret.

1. Download the file and make it executable and put it somewhere onn your ``$PATH``.

1. Add it as a helper to your ``~/.gitconfig``
  ```
  [credential]                                                                    
     helper = !git-credential-libsecret.py
  ```
