# Test Output

**Date:** 15 October 2026

## 1. Full Test Suite

**Command:** `python manage.py test -v 2`

**Result:** PASS — 31 tests passed.

**System check:** No issues identified.

The test suite covered API requests, model validation, box recommendations, weight limits, product rotation, and packing geometry.

**Actual terminal output:**

(.venv) PS D:\personal\projects\assignment\box-selector> python manage.py test -v 2
Found 31 test(s).
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Operations to perform:
  Synchronize unmigrated apps: messages, staticfiles
  Apply all migrations: admin, auth, contenttypes, packing, sessions
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying packing.0001_initial... OK
  Applying sessions.0001_initial... OK
System check identified no issues (0 silenced).
test_bad_payloads_return_400_and_create_nothing (packing.tests.ApiTests.test_bad_payloads_return_400_and_create_nothing) ... ok
test_create_order (packing.tests.ApiTests.test_create_order) ... ok
test_invalid_json_returns_400 (packing.tests.ApiTests.test_invalid_json_returns_400) ... ok
test_list_orders (packing.tests.ApiTests.test_list_orders) ... ok
test_recommendation_for_empty_order_is_400 (packing.tests.ApiTests.test_recommendation_for_empty_order_is_400) ... ok
test_recommendation_for_missing_order_is_404 (packing.tests.ApiTests.test_recommendation_for_missing_order_is_404) ... ok
test_recommendation_returns_cheapest_box (packing.tests.ApiTests.test_recommendation_returns_cheapest_box) ... ok
test_recommendation_when_nothing_fits (packing.tests.ApiTests.test_recommendation_when_nothing_fits) ... ok
test_retrieve_missing_order_is_404 (packing.tests.ApiTests.test_retrieve_missing_order_is_404) ... ok
test_retrieve_order (packing.tests.ApiTests.test_retrieve_order) ... ok
test_wrong_method_is_405 (packing.tests.ApiTests.test_wrong_method_is_405) ... ok
test_negative_box_cost_is_rejected (packing.tests.ModelValidationTests.test_negative_box_cost_is_rejected) ... ok
test_same_product_twice_in_one_order_is_rejected (packing.tests.ModelValidationTests.test_same_product_twice_in_one_order_is_rejected) ... ok
test_valid_product_passes (packing.tests.ModelValidationTests.test_valid_product_passes) ... ok
test_zero_dimension_is_rejected (packing.tests.ModelValidationTests.test_zero_dimension_is_rejected) ... ok
test_zero_quantity_is_rejected (packing.tests.ModelValidationTests.test_zero_quantity_is_rejected) ... ok
test_zero_weight_is_rejected (packing.tests.ModelValidationTests.test_zero_weight_is_rejected) ... ok
test_cheapest_fitting_box_is_chosen (packing.tests.RecommendBoxTests.test_cheapest_fitting_box_is_chosen) ... ok
test_empty_order_raises (packing.tests.RecommendBoxTests.test_empty_order_raises) ... ok
test_equal_cost_prefers_smaller_box (packing.tests.RecommendBoxTests.test_equal_cost_prefers_smaller_box) ... ok
test_returns_none_when_nothing_fits (packing.tests.RecommendBoxTests.test_returns_none_when_nothing_fits) ... ok
test_returns_none_when_too_heavy_for_every_box (packing.tests.RecommendBoxTests.test_returns_none_when_too_heavy_for_every_box) ...
 ok
test_too_big_for_cheap_box_goes_to_bigger_one (packing.tests.RecommendBoxTests.test_too_big_for_cheap_box_goes_to_bigger_one) ... ok
test_weight_limit_is_respected (packing.tests.RecommendBoxTests.test_weight_limit_is_respected) ... ok
test_fifth_cube_does_not_fit (packing.tests.CanPackTests.test_fifth_cube_does_not_fit) ... ok
test_four_cubes_fill_a_box_exactly (packing.tests.CanPackTests.test_four_cubes_fill_a_box_exactly) ... ok
test_item_too_tall_in_every_rotation (packing.tests.CanPackTests.test_item_too_tall_in_every_rotation) ... ok
test_only_one_large_cube_fits_in_a_bigger_cube (packing.tests.CanPackTests.test_only_one_large_cube_fits_in_a_bigger_cube) ... ok  
test_rotation_is_allowed (packing.tests.CanPackTests.test_rotation_is_allowed) ... ok
test_two_items_fit_exactly (packing.tests.CanPackTests.test_two_items_fit_exactly) ... ok
test_volume_passes_but_geometry_fails (packing.tests.CanPackTests.test_volume_passes_but_geometry_fails) ... ok

----------------------------------------------------------------------
Ran 31 tests in 0.118s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...

## 2. Packing Geometry Tests

**Command:** `python manage.py test packing.tests.CanPackTests`

**Result:** PASS — 7 tests passed.

**Actual terminal output:**
Found 7 test(s).
System check identified no issues (0 silenced).
.......
----------------------------------------------------------------------
Ran 7 tests in 0.001s

OK


Found 33 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.................................
----------------------------------------------------------------------
Ran 33 tests in 0.100s

OK
Destroying test database for alias 'default'...
