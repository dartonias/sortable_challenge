# Code to complete the sortable coding challenge @ http://sortable.com/challenge/
# Stephen Inglis, 2016.11.07
#
# Data assumptions:
# - Each price listing matches at most one product
#
# Data notes:
# - Product names use underscores instead of spaces in the product listing
# - Not all listings have an associated product, i.e.
# 		{"title":"WOWWEE Mini combo pack : Raptor, Tribot et Wrex","manufacturer":"WOWWEE","currency":"EUR","price":"59.99"}
# 		There is no WOWWEE manufacturer in the product listing at all, 
#		and this doesn't even seem like a listing for a digital camera at all
# - Spaces are sometimes relevant, i.e. 
# 	- SD980 IS and SD980IS are probably the same product
#	- DSC-W310 [other text] and DSC-W310S are likely subtly different products 
#	(this usually occurs at the end of a model number)
# - Hyphens are sometimes omitted in the listings
#	- DSC-W310 and DSCW310 are probably the same product
# - Manufacturer is a little flexible, i.e. Fujifilm CA, Fujifilm Canada, 
#	FUJIFILM, all correspond to the Fujifilm manufacturer
#
# Boundary cases:
# - Sony T Series DSC-T99 [etc..] appears to be the same as the Cyber-Shot, but simply 
#	listed under a different family name; hard to create a rule for this rare case, as 
#	ignoring the need for the family name in the descriptor confuses other brands where
#	the same model number is used for different products
# - Sony A390 Digital SLR Camera (Black) has the (likely) product spec of 
#	Sony_Alpha_DSLR-A390, reversal of arguments occurs sometimes, but this one is also 
#	missing the family name
# - One user added a space in the model name (M552 -> M 552); this might only occur at the 
#	boundary between letter-number in the model name, so we can examine these specific cases

import json
import re

PRODUCT_FILENAME = 'products.txt'
LABELED_LISTING_FILENAME = 'labeled_listings.txt'
LISTING_FILENAME = 'listings.txt'
RESULT_FILENAME = 'results.txt'
HR_RESULT_FILENAME = 'hr_results.txt'

# Price conversion as of 2016.11.07
# Can replace with a web lookup call at some later point if
# price cutoff to determine false positives is useful
PRICE_CONVERSION = {'CAD' : 1.0, 
					'USD' : 1.34,
					'EUR' : 1.48,
					'GBP' : 1.66}

def load_data(filename):
	with open(filename,'r') as fin:
		data = []
		for lines in fin:
			data.append(json.loads(lines))
		return data

def iterate_data(filename):
	with open(filename,'r') as fin:
		for lines in fin:
			yield json.loads(lines)

def create_placeholder(data):
	return {x["product_name"]: [] for x in data}

def simplify_string(str):
	# Code for simplifying the listing
	temp = str.lower()
	# Characters to ignore
	ignore_chars = ['-','+','(',')']
	for c in ignore_chars:
		temp = temp.replace(c,'')
	# We also remove additional spaces after removing the extra characters
	return re.sub('\s+', ' ', temp).strip()
	
def string_segments(str):
	# Code for simplfying the model and family name into a list of parts
	# possibly seperated by any number of strange characters
	# We want to isolate the numerical and alphabetical parts, using any other characters as splitting points
	# First, replace all non-alphanumeric with spaces
	s = ''.join([ c if c.isalnum() else " " for c in str ])
	# Lower the case, and split based on numeric and alphabetical parts
	s = s.lower()
	s = re.split('(\d+)',s)
	# Append all the results into one list, splitting by the original spaces as needed
	r = []
	for i in s:
		r += i.split()
	return r
	
	
# We add metadata here to prevent doing the same string operations over and over
# We gain CPU time at the cost of memory
def add_metadata(products):
	for p in products:
		# We convert to lowercase to cover some atypical capitalization that often refers to the same brand
		p["Lmanufacturer"] = p["manufacturer"].lower()
		# Convert to lowercase to avoid inconsistent capitalization
		# Get rid of dashes which are sometimes omitted
		Lmodel = string_segments(p["model"])
		try:
			Lfamily = string_segments(p["family"])
		except KeyError:
			Lfamily = []
		# List of all the string segments corresponding to a product
		p["Lfullnames"] = [p["Lmanufacturer"]] + Lfamily + Lmodel
		# From the above, we generate a regex pattern for matching the product
		pattern  = ''
		for parts in p["Lfullnames"]:
			pattern += parts + r'\W?'
		# We require a trailing nonalphanumeric, to avoid variants
		pattern += r'\W'
		p["re_pattern"] = re.compile(pattern)
		
def assign_to_results(listing, products, results, unmatched):
	# results : passed in by reference, so we can modify it here
	# Iterate over products, and once we assign the listing, break
	listing_manufacturer = listing["manufacturer"].lower()
	# We take the listing title and reduce it to lower case, and strip out and dashes
	# as we did for the model name
	listing_title = simplify_string(listing["title"])
	# DEBUG
	#print listing_title
	found = False
	for p in products:
		# This should never be false for a correctly labeled product
		if p["Lmanufacturer"] in listing_manufacturer:
			# Now we use the compiled regex pattern to search the simplified title
			if p["re_pattern"].search(listing_title):
				results[p["product_name"]].append(listing)
				found = True
				break
	# Catch all the unmatched listings for debugging
	if __debug__:
		if not found:
			unmatched.append(listing)

def test():
	# Load all the products into memory 
	products = load_data(PRODUCT_FILENAME)
	# Create placeholder for the results
	results = create_placeholder(products)
	# Add some metadata to the product dictionary
	add_metadata(products)
	# Debugging tool to check unmatched listings
	unmatched = []
	# Iterate over the labeled listings, and assign them to the results
	for listing in iterate_data(LABELED_LISTING_FILENAME):
		assign_to_results(listing, products, results, unmatched)
	# Verify known cases
	for r in results:
		for l in results[r]:
			if l["product_name"] != r:
				print l["title"].encode('ascii','replace') + ' misclassified as ' + r + '\n'
	for l in unmatched:
		if l["product_name"] != 'Unmatched':
			print l["title"].encode('ascii','replace') + ' misclassified as Unmatched' + '\n'
	print 'Test complete'

class Prices:
	def __init__(self):
		self.p = {}
		self.p2 = {}
		self.count = {}
	def add(self,name,price):
		if name in self.p:
			self.p[name] += price
			self.p2[name] += price*price
			self.count[name] += 1
		else:
			self.p[name] = price
			self.p2[name] = price*price
			self.count[name] = 1
	def get_stats(self,name):
		if name in self.p:
			mean = self.p[name] / self.count[name]
			std = (self.p2[name] / self.count[name] - (self.p[name] / self.count[name])**2)**0.5
			return mean,std
		return 0,0
			
def trim_on_price(results):
	deleted = []
	prices = Prices()
	for r in results:
		# Add all the prices for a particular entry
		for l in results[r]:
			currency = PRICE_CONVERSION[l["currency"]]
			val = float(l["price"]) * currency
			prices.add(r,val)
		# Now trim those below 2-sigma from the mean
		mean, std = prices.get_stats(r)
		cutoff = mean - 2*std
		for i in reversed(xrange(len(results[r]))):
			if float(results[r][i]["price"]) < cutoff:
				print results[r][i]["price"], cutoff
				if __debug__:
					deleted.append(results[r][i])
				del results[r][i]
	return deleted

def main():
	# Load all the products into memory 
	products = load_data(PRODUCT_FILENAME)
	# Create placeholder for the results
	results = create_placeholder(products)
	# Add some metadata to the product dictionary
	add_metadata(products)
	# Debugging tool to check unmatched listings
	unmatched = []
	# Iterate over the listings, and assign them to the results
	for listing in iterate_data(LISTING_FILENAME):
		assign_to_results(listing, products, results, unmatched)
	# From here, we can filter out products that are significantly less than the typical product for each group.
	# This would filter out specialized products (i.e. a battery or case for a very specific camera) which might
	# get matched by the previous step
	# -----
	# Removed this function -- on testing it was removing too many positive results, even at 2-sigma deviations
	# Perhaps some more complicated filtering based on price can be possible on a later iteration
	# deleted = trim_on_price(results)
	# -----
	if __debug__:
		with open(HR_RESULT_FILENAME,'w') as fout:
			for r in results:
				fout.write(r + '\n')
				for l in results[r]:
					fout.write(l["title"].encode('ascii','replace') + '\n')
				fout.write('\n')
			fout.write('Unmatched\n')
			for l in unmatched:
				fout.write(l["title"].encode('ascii','replace') + '\n')
			fout.write('Deleted\n')
			#for l in deleted:
			#	fout.write(l["title"].encode('ascii','replace') + '\n')
	with open(RESULT_FILENAME,'w') as fout:
		for r in results:
			fout.write(json.dumps({"product_name": r, "listings" : results[r]}) + '\n')

if __name__ == "__main__":
	if __debug__:
		test()
	main()