# Box Selector

A small Django application that recommends the cheapest suitable shipping box for an order based on product dimensions, quantities, and weight limits.

## Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies and prepare the database:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open the Django admin at http://127.0.0.1:8000/admin/ to manage products and boxes.

## Running Tests

Run the complete automated test suite:

```bash
python manage.py test
```

The recorded output from the test run is available in `TEST_OUTPUT.md`.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/orders/` | Create an order |
| GET | `/api/orders/` | List orders |
| GET | `/api/orders/<id>/` | Retrieve an order |
| GET | `/api/orders/<id>/recommendation/` | Recommend a suitable box |

### Example: Create an Order

Request body:

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

The product must exist in the database.

### Error Responses

- `400 Bad Request`: Invalid input or an order that cannot be processed.
- `404 Not Found`: The requested order does not exist.
- `405 Method Not Allowed`: The HTTP method is not supported for the endpoint.

When no box can accommodate the order, the recommendation endpoint returns a response with `"box": null`.

## How the Packing Algorithm Works

The application checks whether the products in an order can fit inside a box without exceeding its maximum weight capacity.

The packing algorithm uses a heuristic approach:

1. **Sort products:** Process larger items first to make placement easier.
2. **Check rotations:** Try the six possible axis-aligned orientations of each item.
3. **Find a placement:** Choose a suitable available space using a tight-fit strategy.
4. **Split remaining space:** After placing an item, divide the unused space into three non-overlapping regions for subsequent items.
5. **Try alternative orders:** Evaluate three item orderings to improve the chance of finding a valid arrangement.
6. **Choose the box:** Among boxes that fit the entire order and satisfy the weight limit, select the cheapest one.

This is a heuristic rather than an exhaustive search. It can find valid arrangements, but it may not find every arrangement that is physically possible.

## Design Decisions and Assumptions

- Dimensions are stored as integer millimetres and weights as integer grams.
- Box cost is represented using a decimal field.
- The maximum box weight applies to the total product weight; packaging weight is excluded because it is not provided.
- Each order must fit inside a single box.
- Products may be rotated along the box axes, but diagonal placement is not supported.
- The same product cannot appear more than once as a separate line item in one order.
- The API limits item quantity to 1,000 per line.
- If no box fits, the recommendation endpoint returns HTTP 200 with `"box": null`.
- If multiple boxes have the same cost, the smaller-volume box is preferred, followed by the lower box ID.
- The order-creation endpoint is CSRF-exempt for this assignment. A production application should use an appropriate authentication and security strategy.

## Limitations

- The packing algorithm is heuristic. A reported fit should satisfy the implemented geometric checks, but a failed fit does not necessarily mean that no valid arrangement exists.
- Products are expanded into individual units during packing, so very large orders can take longer to process.
- The quantity limit is enforced by the API and may not be enforced when records are created through Django admin.
- The packing strategy does not guarantee a globally optimal arrangement.

## Project Verification

The automated test suite completed successfully with 31 tests passing in the recorded run. See `TEST_OUTPUT.md` for the corresponding output.
