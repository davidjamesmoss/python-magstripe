import re


class MagStripeError(Exception):
    pass


class MagStripe():
    '''
    For ISO 7813 financial cards. Reads track 1 and 2.
    Not sure what would happen if a 3-track card was used.
    Intended for string input from USB keyboard emulator card reader.
    Compares track 1 and 2, because redundancy.
    '''

    # Track parsing based on
    # https://github.com/eighthave/pyidtech/blob/master/idtech.py
    def parsetrack1(self, trackstr):
        if not trackstr:
            raise MagStripeError('Blank track 1 data')

        if trackstr[1] != 'B':
            raise MagStripeError('Wrong track 1 format (not B)')
        trackdata = trackstr[2:len(trackstr)-1]  # remove start/end sentinel

        try:
            cardnumber, name, data = trackdata.split('^')
        except ValueError:
            raise MagStripeError('Could not parse track 1')

        try:
            lastname, firstname = name.split('/')
        except ValueError:
            raise MagStripeError('Could not parse cardholder name')

        expyear = data[0:2]
        expmonth = data[2:4]

        if not self.validate(cardnumber):
            raise MagStripeError('Card number in track 1 did not validate')

        return {
            'account': cardnumber,
            'expiry_month': expmonth,
            'expiry_year': expyear,
            'name': '%s %s' % (firstname.strip(), lastname.strip())
        }

    def parsetrack2(self, trackstr):
        if not trackstr:
            raise MagStripeError('Blank track 2 data')
        trackdata = trackstr[:len(trackstr)-1]  # remove start/end sentinel

        try:
            cardnumber, data = trackdata.split('=')
        except ValueError:
            raise MagStripeError('Could not parse track 2')

        expyear = data[0:2]
        expmonth = data[2:4]

        if not self.validate(cardnumber):
            raise MagStripeError('Card number in track 2 did not validate')

        return {
            'account': cardnumber,
            'expiry_month': expmonth,
            'expiry_year': expyear
        }

    # http://atlee.ca/blog/2008/05/27/validating-credit-card-numbers-in-python/
    def validate(self, cardnumber):
        """
        Returns True if the credit card number ``cardnumber`` is valid,
        False otherwise.

        Returning True doesn't imply that a card with this number has ever
        been, or ever will be issued.

        Currently supports Visa, Mastercard, American Express, Discovery
        and Diners Cards.

        >>> validate_cc("4111-1111-1111-1111")
        True
        >>> validate_cc("4111 1111 1111 1112")
        False
        >>> validate_cc("5105105105105100")
        True
        >>> validate_cc(5105105105105100)
        True
        """
        # Strip out any non-digits
        s = re.sub("[^0-9]", "", str(cardnumber))
        regexps = [
            "^4\d{15}$",
            "^5[1-5]\d{14}$",
            "^3[4,7]\d{13}$",
            "^3[0,6,8]\d{12}$",
            "^6011\d{12}$",
        ]

        if not any(re.match(r, s) for r in regexps):
            return False

        chksum = 0
        x = len(s) % 2
        for i, c in enumerate(s):
            j = int(c)
            if i % 2 == x:
                k = j*2
                if k >= 10:
                    k -= 9
                chksum += k
            else:
                chksum += j
        return chksum % 10 == 0

    def parse(self, input):
        try:
            track1, track2 = input.split(';')
        except ValueError:
            raise MagStripeError('Did not get expected track 1 and 2')

        t1 = self.parsetrack1(track1)
        t2 = self.parsetrack2(track2)

        if (t1['account'] == t2['account'] and
                t1['expiry_month'] == t2['expiry_month'] and
                t1['expiry_year'] == t2['expiry_year']):
            return t1
        else:
            raise MagStripeError('Track 1 and 2 data did not match')
