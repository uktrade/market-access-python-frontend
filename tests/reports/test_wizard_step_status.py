# CASES TO TEST #
#
# 1. Continue with proper data passes onto location step - ensure session
#    data saved to DB & cleaned_data correct
#
# 2. Continue without status radio selected triggers error
#
# 3. Continue with an invalid format for month (partially resolved date field)
#    triggers error
#
# 4. Continue with an invalid format for year (partially resolved date field)
#    triggers error
#
# 5. Continue with an invalid format for month (resolved date field)
#    triggers error
#
# 6. Continue with an invalid format for year (resolved date field)
#    triggers error
#
# 7. Continue with an invalid format for month (start date field)
#    triggers error
#
# 8. Continue with an invalid format for year (start date field)
#    triggers error
#
# 9. Continue with date in the far past (partially resolved date field)
#    triggers error
#
# 10. Continue with date in the far future (partially resolved date field)
#     triggers error
#
# 11. Continue with date in the far past (resolved date field) triggers error
#
# 12. Continue with date in the far future (resolved date field) triggers error
#
# 13. Continue with date in the far past (start date field) triggers error
#
# 14. Continue with date in the far future (start date field) triggers error
#
# 15. Continue with partially resolved selected but without
#     partially_resolved_date triggers error
#
# 16. Continue with partially resolved selected but without
#     partially_resolved_description triggers error
#
# 17. Continue with resolved selected but without resolved_date triggers error
#
# 18. Continue with resolved selected but without resolved_description
#     triggers error
#
# 19. Continue with both start date and start date known checkbox
#     empty triggers error
#
# 20. Continue with both start date entered and start date known checked
#     triggers error
#
# 21. Continue with start date known checkbox checked, without selecting
#     value for currently_active triggers error
