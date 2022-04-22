<h1 align="center">
  Incremental Learning with ID5 
</h1>


This implementation is based on the ID5 article [[1]](#1). ID5 is an Incremental ID3, the difference between ID4 and ID5 is that in ID4 the subtree will be pruned but in ID5 the structure of the tree will be retained but updated when every instance adds if needed without loss of data. The steps of this algorithm are explained below:


 <br>


## Steps:

1. Add every instance until the entropy is not equal to zero. Then based on the E-score select an attribute for the main root.
2. Add every instance to the tree.
3. If entropy for that branch remains zero go to step 2.
4. Otherwise, select an attribute as a non-test attribute based on E-score.
5. Check if a pull-up process is needed to exchange the non-test attribute with the current test attribute. (Do that recursively until reaching the main root)
6. Go to step 2.

**_NOTE:_**  INFO phrase in article considered as E-score moreover a test attribute is a partitioner attribute in the tree.

 <br>

## What these codes do (exist in PY files)

There are four PY files that are required to run the main.py. Below, the functionality of each PY file are summarized, but more details are provided in the files themselves.

- instance.py: Contain the Instance Class for each sample in the datasheet.
- tree.py: Contains Tree class and its methods e.g., adding instance.
- main.py: Contains the ID5 algorithm. (loading data (data.xls) -> run algorithm -> evalute algorithm)

<br>


## Evaluation

Done by these concepts:
  - k-fold
  - accuracy

<br>

## References
<a id="1">[1]</a> 
PAUL E.Utgoff (1988). 
ID5: An Incremental ID3. 
Morgan Kaufmann, 107-120.
