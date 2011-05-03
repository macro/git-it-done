===========
git-it-done
===========

I wrote this ridiculously simple Django app on a plane when I needed something to manage things todo items and didn't want to install a full-blown Trac instance.

Features
--------

* It is ridiculously simple!
* Complete items directly using git commit hook
* Item pagination
* View commit diffs in-app

Limitations
-----------

* Single player with no access control and single repo (can run another instance to support more than repo)
* Items only references last commit hash
