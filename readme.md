# Python-Magstripe

For ISO/IEC 7813 financial cards. Reads track 1 and 2.  
Not sure what would happen if a 3-track card was used.  
Intended for string input from USB keyboard emulator card reader.  

### What it does do
Validates card number.  
Compares account number and expiry on track 1 and 2, because redundancy.  

### What it does not do
Does not read security or service codes.  
Does not verify expiry date.  

### Usage
	from magstripe import MagStripe
	
	data = '%B4242424242424242^SURNAME/FIRSTNAME I^15052011000000000000?;4242424242424242=15052011000000000000?'
	
	m = MagStripe()
	print m.parse(data)
	
Will return a dict containing:

	{
		'account': '4242424242424242',
		'expiry_year': '15',
		'expiry_month': '05',
		'name': 'FIRSTNAME I SURNAME'
	}
	
Or raise a MagStripeError exception.
	
### Tests
Includes basic does-it-parse-or-not test code.
Works on every UK-issued credit and debit card I could lay my hands on (which was about 23).