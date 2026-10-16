 Box Selector

A Django application that recommends a suitable shipping box for an order based on product dimensions, quantities, weight limits, and box cost.

 Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependencies and prepare the database:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

To access Django Admin, create a superuser:

```bash
python manage.py createsuperuser
```

Open [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) to manage products, boxes, and orders.

 Running Tests

Run the automated test suite:

```bash
python manage.py test
```

Run Django's system checks:

```bash
python manage.py check
```

See `TEST_OUTPUT.md` for the recorded test results.

 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/orders/` | Create an order |
| GET | `/api/orders/` | List orders |
| GET | `/api/orders/<id>/` | Retrieve an order |
| GET | `/api/orders/<id>/recommendation/` | Get a box recommendation |

 Example: Create an Order

Send a POST request to `/api/orders/` with this JSON body:

```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

The product ID must refer to an existing product in the database.

 API Error Responses

- `400 Bad Request`: The input is invalid or the order cannot be processed.
- `404 Not Found`: The requested order does not exist.
- `405 Method Not Allowed`: The HTTP method is not supported.

If no suitable box is found, the recommendation endpoint returns `"box": null` with HTTP 200.

 How the Packing Algorithm Works

The application checks whether all products in an order can fit inside one box without exceeding its weight limit.

The algorithm follows these steps:

1. **Sort products:** Try different item orderings, including larger items first.
2. **Check rotations:** Try the unique orientations of each product by rotating it along the box axes.
3. **Find a placement:** Choose a fitting available space using a tight-fit approach.
4. **Split the remaining space:** Divide the unused space into up to three regions for the remaining products.
5. **Try alternative orders:** Test three item orderings to improve the chance of finding a valid arrangement.
6. **Recommend a box:** Select the lowest-cost box the algorithm finds suitable.

The algorithm uses a heuristic approach rather than checking every possible arrangement. It may not find a valid arrangement even when one is physically possible.

 Design Decisions and Assumptions

- Product and box dimensions are stored as positive integers in millimetres.
- Product weights and box weight limits are stored as positive integers in grams.
- Box cost uses a decimal field to represent monetary values.
- The total product weight must not exceed the box's maximum weight.
- Packaging weight is excluded because it is not provided.
- All products in an order must fit inside one box.
- Products can be rotated along the box axes, but diagonal placement is not supported.
- The same product cannot be added in multiple separate order-item rows for one order; its quantity should be updated instead.
- The API limits item quantity to 1,000 per line.
- If multiple suitable boxes have the same cost, the smaller-volume box is preferred, followed by the lower box ID.
- If no box is found, the recommendation endpoint returns HTTP 200 with `"box": null`.
- The order-creation endpoint is CSRF-exempt for this assignment. A production application should use suitable authentication and security controls.

 Limitations

- The packing algorithm does not guarantee that it will find every physically possible arrangement.
- Products are expanded into individual units during packing, so large quantities may take longer to process.
- The quantity limit is enforced by the API and may not apply when records are created through Django Admin.
- The algorithm does not guarantee a globally optimal packing arrangement.

 Project Verification

The test results are documented in `TEST_OUTPUT.md`. Please ensure the documented test count matches the output from the final test run.