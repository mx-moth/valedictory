===========
valedictory
===========

Valedictory validates dicts. It operates in a manner superficially similar to
Django forms, but is tuned for use in API validation, and other situations
where you are receiving JSON as opposed to key-value POST form data. It takes
in a dict of data (probably obtained from a JSON POST request), and validates
that data against some criteria.

Input data can be typed, unlike regular Django forms, and validators can be
nested, again unlike Django forms.

Additionally, Validator themselves are stateless once constructed. You can
reuse the same Validator instance to validate input data multiple times, from
multiple sources.

Django is not a requirement. It is just useful as a comparison.
