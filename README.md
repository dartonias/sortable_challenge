# Running the code

To execute the code, simply run

`python -O sortable_challenge.py`

from the main directory. It will produce `results.txt` that will contain the JSON record of results.

Without the optimization flag, `hr_results.txt` is also generated, as a more human readable version of the results, and a set of test cases in `labeled_listings.txt` is also checked, with errors printed to the console (on stdout).

## Files
### sortable_challenge.py  
main python file, only relies on the "re" and "json" libraries
### errors.txt  
list of border cases still to be (possibly) fixed; of course this is difficult to tell and only based on the human algorithm
### labeled_listings.txt  
list of (human) labeled listings for the purpose of checking modifications to the algorithm on a set of known cases
### listings.txt
Provided JSON record of listings
### products.txt
Provided JSON record of products