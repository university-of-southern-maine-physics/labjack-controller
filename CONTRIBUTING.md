# So You Want to Be A Contributor

## The USM-Physics Guide for Success In Life

Welcome! Thanks for wanting to contribute. We welcome any improvements for this library.
To make life easier for you (and to prevent PRs from getting rejected all the time),
we've outlined some general contributing guidelines for you to follow to ensure all of
your code is awesome.

## If You Found a Bug

### Issues

If you find a bug we didn't, please [create an issue][2]. We have pre-created templates to
make life easier for you. In general, you should:

* Use (at least moderately) clear English.
* Ensure your issue title is clear, concise, and descriptive.
* Be as thorough as possible when describing the problem you encountered.

## If You Want to Contribute Code

We use a pretty standard method for managing contributions. Before you begin, make sure your
code is licenced through the [MIT licence][10], because that's the licence we distribute our code under.

You should also talk with someone associated with this project before doing anything crazy,
like refactoring code.


The major points are outlined below.

### Coding Style

We're love terminals from the 70s, and therefore expect everyone to follow [pep-8][0] in its entirity,
meaning, among other things, that you keep your line widths less than 80 characters.
We encourage you to use a linter like [flake8][1] to whip everything into shape.

We also conform to the [pep-484][4] standard, meaning that all functions must have type hinting.

All code is documented using a style compatible with [numpydoc][5].

### Fork, Modify and Open a Pull Request

If you know how to use Git, but don't know how to fork and merge (a strange combination), read [this guide][3].
If you've never done any of this before, here's what you need to do:

1. [Fork this repository][6]

2. [Clone a copy][7] onto your computer

3. Create a topic branch that is dedicated to the development of your new feature/bugfix/etc
  ```
  git checkout -b YOUR_NEW_BRANCH_NAME_HERE
  ```
4. Add and commit your changes.

5. Push your topic branch to your origin.
  ```
  git push origin YOUR_NEW_BRANCH_NAME_HERE
  ```
 
6. [Open a pull request][8] (PR) with our repository.
Make sure the PR has a clear title and description, because otherwise we may not know what it is or why we need it.

## Thanks

A big thank-you to [d2si-oss][9]. This guide is further proof that nobody is completely original.

[0]: https://www.python.org/dev/peps/pep-0008/
[1]: http://flake8.pycqa.org/en/latest/
[2]: https://guides.github.com/features/issues/
[3]: https://www.atlassian.com/git/tutorials/comparing-workflows#forking-workflow
[4]: https://www.python.org/dev/peps/pep-0484/
[5]: https://numpydoc.readthedocs.io/en/latest/format.html
[6]: https://help.github.com/en/articles/fork-a-repo
[7]: https://help.github.com/en/articles/cloning-a-repository
[8]: https://help.github.com/articles/about-pull-requests
[9]: https://github.com/d2si-oss/contributing-guidelines/blob/master/README.md
[10]: https://github.com/university-of-southern-maine-physics/labjack-controller/blob/master/LICENSE
