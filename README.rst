Crumb
=====

Introduction
------------

In software development, some projects involve writing programs that are not merely "correct" or "incorrect" but
instead is measured against some metric of success. For example, a spell-checker is measured by accuracy against a test
dataset, and a machine learning algorithm might be measured by its cross-validation score on a training set.

A typical approach to this sort of task is:

1. write the code to evaluate the results
2. write a benchmark using the simplest possible algorithm
3. progressively increase the evaluation score by improving/replacing
   the algorithm until you've reached the objective or no further
   gains can be made.

As far as I know this methodology has no name, but it could be called "objective-driven development" in
analogy to its deterministic cousin, "test-driven development".

The downside to this approach is that it requires keeping track of the evaluation score (and possibly other
attributes such as parameters) at each change of the algorithm. Fear of not being able to revert and recreate
good results can creep in and impede experimentation. Version-control alleviates this to a point,
but it is still a pain to manually track the attributes associated with each commit.

That's where Crumb comes in. Crumb exists to automate the tracking, in a way that does not get in your way as a developer.

Crumb's functionality boils down to this:

- clone your git repository into a temporary directory
- run a given command in that directory
- parse the output of the command for tracked attributes
- annotate the git commit with the values of the attributes
  and some metadata
- export the commit history (along with the attributes) to
  a spreadsheet for analysis and easy viewing

This results in a "breadcrumb trail" (hence the name) of commits and their scores. In cloning your commit to a temporary
directory, Crumb provides a degree of security in ensuring that the results will be reproducable at another time.

