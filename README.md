# Running the code
To execute the code, simply run

`python -O sortable_challenge.py`

from the main directory. It will produce `results.txt` that will contain the JSON record of results.

Without the optimization flag, `hr_results.txt` is also generated, as a more human readable version of the results, and a set of test cases in `labeled_listings.txt` is also checked, with errors printed to the console (stdout).

## Notes
There are a few remaining parts of the code that could be further improved.

`trim_on_price(results)` function is currently unused, but the idea is to trim results that stray too far from the typical price range of a device, especially on the low end, as these might represent accessories for the specific device.
So far this concept has not worked, as even 2-sigma deviations many positive results are being removed.

When we generate the regulad expression for searching through the listing, the results are only slightly modified by also requiring the manufacturer name as part of the product.
The reason this is not obviously needed or not, is because the family name of the product is sometimes omitted or present, but there are cases of identical products (by manufacturer and model) that are only differentiated by the family name (i.e. Olympus Stylus and mju or Tough series), and so a more strict interpretation is necessary.
For reducing false positives we include it, but whether it is necessary or not is something that can be bette tested on a large set of labeled data where the aggregate false positives and false negatives can be measured.

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
### validate
Script to run to check if `results.txt` is of the correct format