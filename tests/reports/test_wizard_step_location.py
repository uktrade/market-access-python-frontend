# CASES TO TEST #
#
# 1. Happy path - Continue with just country data passes onto
#    trade-direction step - ensure session data saved to DB &
#    cleaned_data correct
#
# 2. Happy path - Continue with just trading bloc data passes
#    onto trade-direction step - ensure session data saved to DB
#    & cleaned_data correct
#
# 3. Happy path - Continue with country and 'caused by trading
#    bloc' data passes onto trade-direction step - ensure session
#    data saved to DB & cleaned_data correct
#
# 4. Happy path - Continue with country, 'caused by trading bloc'
#    and admin areas data passes onto trade-direction step - ensure
#    session data saved to DB & cleaned_data correct
#
# 5. Error - Attempt to continue without selecting country
#
# 6. Init check - check trading bloc fields created to match
#    metadata list of trading blocs
#
# 7. Init check - check location select choices includes trading
#    blocs and countries
#
# 8. Error - Attempt to submit country selection as the placeholder
#    value
#
# 9. Error - No admin areas selected, but user indicated barrier
#    does not affect whole country
