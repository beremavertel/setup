# setup

Add setup/scripts to your $PATH, or navigate to setup/scripts and:

Run find_modules.py

If you want to only run on installed modules, create a text file named "modules" in the same folder that you're running the script in, containing the names of the installed modules (This can be achieved by running `odoomodules $DATABASENAME > modules`)



<br>
<br>

`$ git clone git@github.com:beremavertel/setup.git`


**1. ADD "setup" TO PATH**

```
$ echo $PATH
/path/to/dir:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
$ export PATH=$PATH:~/setup/scripts
$ echo $PATH
/path/to/dir:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/setup/scripts
```

Source: https://hackprogramming.com/2-ways-to-permanently-set-path-variable-in-ubuntu/

**2. ADD INSTALLED MODULES IN FILE**

Print installed modules in a file, "modules". <br>
`$ odoomodules l10n_se_app > modules` <br>

**3. FIND ERRORS IN MODULES**

`$ find_modules.py`

