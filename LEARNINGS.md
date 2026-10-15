1. Virtual Environment
A virtual environment creates an isolated environment for a Python project. It helps prevent dependency conflicts between different projects.
used the command python -m venv .venv and to activate i used .venv\Scripts\activate .venv is the anme of my virtual environmnent and in future i can deactivate it by using the command deactivate

2. Django Project and Apps

A Django project contains the main configuration, settings, and URLs. Apps organize related functionality within the project.
In this project, the packing app contains the product, box, order, and order-item models.
used command django-admin startproject config . and to run the development server i used python manage.py runserver 

3. Django Models

Models define the structure of data stored in the database.
Product stores the product name, dimensions, and weight.
Box stores the box name, internal dimensions, maximum weight, and cost.
Order represents an order.
OrderItem connects an order to a product and stores its quantity.

4. Why Use Integers for Dimensions and Weight?

Dimensions are stored in millimetres and weight in grams using positive integer fields. This avoids floating-point precision issues when comparing dimensions during packing.

The box cost uses DecimalField because decimal values are appropriate for storing money.

5. Field Validators and full_clean()

Validators check whether field values meet specified rules. For example, MinValueValidator(1) requires a dimension to be at least 1.

Django does not automatically run full_clean() when calling save(). Therefore, API code must explicitly validate model instances or use equivalent validation before saving them.

6. ForeignKey Relationships

A ForeignKey connects one model to another.

In this project, each order item refers to an order and a product. The related_name="items" setting allows order items to be accessed using order.items.all().

7. on_delete Options

CASCADE: Deleting an order also deletes its related order items.

PROTECT: Prevents deleting a product that is referenced by an order item.

These options help control how related database records behave when something is deleted.

8. UniqueConstraint

The UniqueConstraint on order and product prevents the same product from being recorded in multiple order-item rows for one order. Its quantity should be increased instead.

9. Database Migrations

makemigrations creates migration files describing changes to Django models.

migrate applies those changes to the database.

Migration files help keep the database structure synchronized with the models.

10. Django Admin

Django Admin provides an interface for managing database records.

Registering Product, Box, Order, and OrderItem makes these models accessible through the admin interface. An inline allows order items to be managed directly on an order's page.

11. Packing Algorithm

The purpose of the packing algorithm is to find a suitable shipping box for an order.

It must consider product dimensions, rotations, quantities, combined fit, weight capacity, and box cost. Checking whether each product fits individually does not guarantee that all products fit together.

12. Testing and Verification

The project must be tested by running Django system checks and automated tests. I should record the actual commands, results, errors, and fixes rather than assuming the code works.


13. CSRF Protection

CSRF stands for Cross-Site Request Forgery. It is a security risk where an attacker attempts to make a user's browser send an unwanted request to a website where the user is authenticated.

Django provides CSRF protection to help prevent these attacks. In my project, I used `@csrf_exempt` on the order API endpoint to make testing requests from Postman easier. This disables CSRF protection for that view, so it should be used carefully. A real application should use appropriate authentication and security controls.

14. Model Validation Using `full_clean()`

The `full_clean()` method validates a Django model instance before it is saved. It checks field validation, model-level validation, and applicable uniqueness constraints.

In my project, calling `full_clean()` on an order item helps detect invalid data before saving it. Django does not automatically call `full_clean()` when using `save()`, so I must call it explicitly or use another suitable validation approach.

15. Database Transactions

A database transaction groups multiple database operations into one logical unit.

In my project, `transaction.atomic()` is used when creating an order and its order items. If an error occurs and the transaction rolls back, the database does not keep a partially created order. This helps maintain data consistency.

16. HTTP Status Codes

HTTP status codes communicate the result of an API request.

- 200 OK: The request succeeded.
- 201 Created: A new order was created successfully.
- 400 Bad Request: The request contains invalid data.
- 404 Not Found: The requested order does not exist.
- 405 Method Not Allowed: The endpoint does not support the HTTP method used.

In my project, these status codes help the client understand whether an order was created successfully or why a request failed.

17. API Testing Using Postman

Postman allows me to send HTTP requests to my Django API and inspect the responses.

I can use GET requests to retrieve orders and recommendations, and POST requests to create orders. I should test both valid requests and invalid inputs, including unknown product IDs, invalid quantities, and empty item lists.

I should record the actual HTTP status codes and response bodies rather than assuming the API behaves as expected.

18. Order Creation and Error Handling

When creating an order, the API first validates the request body and checks whether the requested products exist. It then creates the order and its items inside a database transaction.

If the request contains invalid data, the API returns an appropriate error response. This prevents invalid requests from being treated as successful order creations.

19. Box Recommendation and Weight Validation

The recommendation service calculates the total weight and volume of the products in an order. It checks whether a box has enough weight capacity and sufficient dimensions to hold the products.

The packing algorithm considers different orientations of products because rotating a product may allow it to fit. However, the combined products must fit together inside the same box.

Boxes are considered according to their cost, so the service attempts to select a low-cost suitable box. I must verify through tests that the selected box is genuinely feasible and that the algorithm does not miss a cheaper valid option.

20. Project Verification and Documentation

Before submitting the project, I should run Django system checks and automated tests, test the API using Postman, and inspect any errors.

I should maintain a README.md containing setup instructions and API usage examples. I should also document AI assistance accurately in AI_USAGE.md, preserve the actual AI chat transcript if required, and write my own learning reflection.

I should include only test results that I have actually obtained by running the project.