Box Selector — Learning Notes
These notes summarize the concepts used while developing the Django Box Selector project and serve as a reference for explaining the implementation.
1. Virtual Environment
A virtual environment creates an isolated environment for a Python project. It helps prevent dependency conflicts between different projects.
Commands used on Windows:
python -m venv .venv
.venv\Scripts\Activate.ps1
# When finished:
deactivate
.venv is the name of the virtual-environment folder. The activation command differs between PowerShell, Command Prompt, and macOS/Linux.

2. Django Project and Apps
A Django project contains the main configuration, settings, and URL routing. Apps organize related functionality. In this project, the packing app contains the product, box, order, order-item, API, and packing logic.
Commands used:
django-admin startproject config .
python manage.py runserver
The development server is intended for local development.

3. Django Models
Models define the structure of data stored in the database.
- Product stores the product name, dimensions, and weight.
- Box stores the box name, internal dimensions, maximum weight, and cost.
- Order represents an order.
- OrderItem connects an order to a product and stores its quantity.

4. Why Use Integers for Dimensions and Weight?
Dimensions are stored in millimetres (mm) and weight in grams (g) using positive integer fields. Consistent integer units make dimension and weight comparisons straightforward and avoid floating-point precision issues in these comparisons.
Useful conversions:
- 1 cm = 10 mm
- 1 m = 1000 mm
- 1 kg = 1000 g
The box cost uses DecimalField because decimal values are appropriate for money and avoid common binary floating-point representation issues.

5. Field Validators and full_clean()
Validators check whether field values meet specified rules. For example, MinValueValidator(1) requires a value to be at least 1.
Django does not automatically call full_clean() when save() is called. Therefore, code that saves model instances should explicitly validate them or use another suitable validation approach.

6. ForeignKey Relationships
A ForeignKey connects one model to another. In this project, each order item refers to an order and a product. The related_name="items" setting allows order items to be accessed with order.items.all().

7. on_delete Options
- CASCADE: deleting an order also deletes its related order items.
- PROTECT: prevents deleting a product that is referenced by an order item.
These options define how related database records behave when a referenced record is deleted.

8. UniqueConstraint
The UniqueConstraint on order and product prevents the same product from appearing in multiple separate order-item rows for one order. Its quantity should instead be represented in that product's order-item row.

9. Database Migrations
- python manage.py makemigrations creates migration files describing changes to models.
- python manage.py migrate applies migrations to the database.
Migration files help keep the database structure synchronized with the Django models.

10. Django Admin
Django Admin provides a browser interface for managing database records. In this project, Product and Box are registered as separate admin sections, while order items can be managed inline on an order's page.

11. Packing Algorithm and Formulas
The packing algorithm recommends a suitable shipping box by considering product dimensions, rotations, quantities, combined fit, weight capacity, and cost. Checking whether each product fits individually does not guarantee that all products fit together.
Product and box volume
Let L mean length, W mean width, and H mean height. Dimensions must use the same unit in each calculation.
Volume = Length × Width × Height
V = L × W × H
For example, a product measuring 10 mm × 5 mm × 4 mm has volume:
10 × 5 × 4 = 200 mm³
Total product weight
For each product type, multiply the weight of one unit by its quantity and add the results:
Total weight = Σ (unit weight × quantity)
A box passes the weight check when:
Total product weight ≤ Box maximum weight
The packaging weight is excluded because it is not provided in the assignment.
Total volume check
Total item volume = Σ (Lᵢ × Wᵢ × Hᵢ)
A necessary condition for fitting is:
Total item volume ≤ Box inner volume
If the total product volume is larger than the box's inner volume, the products cannot fit. If the total volume is smaller, that alone does not prove they can fit together; their dimensions and the available spaces must also be checked.
Product rotations
For an item with dimensions (L, W, H), the code considers the unique permutations of those dimensions. There are at most 3! = 3 × 2 × 1 = 6 axis-aligned orientations:
(L, W, H), (L, H, W), (W, L, H),
(W, H, L), (H, L, W), (H, W, L)
If dimensions are equal, some orientations are duplicates. The implementation uses permutations() and removes duplicates.
An item fits in an available space only if all three dimensions of its chosen orientation fit:
item length ≤ space length
item width  ≤ space width
item height ≤ space height
Splitting the remaining space
When an item (pl, pw, ph) is placed in a corner of an available space (sl, sw, sh), the implementation considers three leftover regions:
Beside the item: (sl - pl, sw, sh)
In front:        (pl, sw - pw, sh)
Above the item:  (pl, pw, sh - ph)
A region is discarded if any of its dimensions is zero or negative. This space-splitting method is a heuristic and does not examine every possible physical arrangement.
Wasted volume and placement
For a candidate placement:
Wasted volume = Available-space volume - Item volume
The algorithm prefers the candidate with the smallest wasted volume among the placements it checks. This is a heuristic choice and does not guarantee a globally optimal packing.
Selecting a box
Candidate boxes are ordered by:
(Box cost, Box inner volume, Box ID)
The service skips boxes that fail the total-weight check or the necessary total-volume check, then runs the geometric packing check. It returns the first box that passes. Equal-cost boxes are ordered by smaller inner volume and then lower ID. Because the packing algorithm is heuristic, it may fail to find a valid arrangement in a cheaper box even when another arrangement could work.

12. Testing and Verification
The project can be checked using Django's system check and automated test suite:
python manage.py check
python manage.py test -v 2
python manage.py test packing.tests.CanPackTests
Test results should be recorded from the actual terminal output. Tests can cover API requests, model validation, box recommendations, weight limits, product rotation, and packing geometry. Passing tests provides evidence for the cases tested, but does not prove that every possible input or packing arrangement is handled correctly.

13. HTTP Status Codes
HTTP status codes communicate the result of an API request.
- 200 OK: the request succeeded.
- 201 Created: a new order was created successfully.
- 400 Bad Request: the request contains invalid data or cannot be processed.
- 404 Not Found: the requested order does not exist.
- 405 Method Not Allowed: the endpoint does not support the HTTP method used.
The client should use the status code and response body to understand the outcome of a request.

14. API Testing Using Postman
Postman allows HTTP requests to be sent to the Django API and makes it possible to inspect response status codes and response bodies.
- GET requests can retrieve orders and recommendations.
- POST requests can create orders.
Useful cases to test include valid requests, invalid JSON, unknown product IDs, invalid quantities, empty item lists, missing order IDs, and unsupported HTTP methods. Record the actual responses rather than assuming the API behaves as expected.            

15. Order Creation and Error Handling   
When creating an order, the API validates the request body and checks whether the requested products exist. It then creates the order and its items inside a database transaction. Invalid requests should return an appropriate error response rather than being treated as successful order creation.

16. Box Recommendation and Weight Validation
The recommendation service calculates the total weight and volume of the products in an order. It checks the box's weight capacity and whether the products can fit geometrically inside the box. Rotating products may allow them to fit, but all products must fit together inside the same box.
Boxes are considered in cost order, with tie-breakers for inner volume and ID. Tests help verify that returned recommendations satisfy the implemented checks. Since the packing algorithm is heuristic, it cannot guarantee that it will find every possible valid arrangement or the globally optimal packing.

17. Project Verification and Documentation
Before submission, run Django system checks and automated tests, test the API using Postman, and inspect errors. Keep a README.md with setup instructions and API examples, an AI_USAGE.md documenting AI assistance accurately, and a TEST_OUTPUT.md containing actual test results. Keep the learning notes as a separate reference document.

