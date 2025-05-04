# 📁 /docs/fastapi_entity_notes.md

---

# FastAPI Documentation Improvements (ParcoRTLS v0.1.4)

## ✨ Overview

This document summarizes the improvements made to the **FastAPI documentation** standards for ParcoRTLS, beginning with v0.1.4.

The goals were to:
- Improve Swagger/OpenAPI auto-documentation.
- Make every endpoint self-explanatory for future developers.
- Enhance usability for third-party SDK clients and maintainers.

Inspired by the improved `/maps.py` route file (v0P.3B.008).


## 🔖 Key Documentation Changes

- Every route now has a **full docstring** following a standardized template.
- Docstrings describe:
  - **Purpose** of the endpoint
  - **Parameters** (name, type, required/optional)
  - **Returns** structure
  - **Raises** (HTTPException codes)
  - **Example Usage** (example `curl` commands)
  - **Sample Response JSON**
  - **Use Case Scenarios**
  - **Developer Hints** (edge cases, validations)


## 📉 Example Improvements

### Before (old style)
```python
@router.get("/get_maps")
async def get_maps():
    """
    Retrieve maps.
    """
    # ...
```


### After (new enhanced style)
```python
@router.get("/get_maps")
async def get_maps():
    """
    Retrieves a list of all maps in the ParcoRTLS system.

    Parameters:
    - None

    Returns:
    - List[dict]: A list of maps with fields like `i_map` and `x_nm_map`.

    Raises:
    - HTTPException (404): If no maps are found.
    - HTTPException (500): On unexpected database errors.

    Example:
    ```bash
    curl -X GET "http://192.168.210.226:8000/api/get_maps"
    ```

    Use Case:
    - Populate frontend map dropdowns.

    Hint:
    - Verify database connection before calling.
    """
```


## 🔬 Advantages

- Swagger UI now displays:
  - Clear endpoint descriptions
  - Curl examples inline
  - Input/Output schemas clearly
- Reduces developer ramp-up time.
- Eases SDK auto-generation in future (e.g., for Python, Typescript clients).
- Ensures future maintainers understand *why* each endpoint exists, not just *how*.


## 🔍 FastAPI Coding Standard (v0.1.4+)

Going forward:
- **All** FastAPI endpoints must include a full descriptive docstring.
- **Route files** must have a `tags=["meaningful_tag"]` in APIRouter.
- **Stored procedures** used must be mentioned where appropriate.
- **Version bumps** and changelogs must be included in each route file header.


## 📆 Files Following This Standard

| Route File | Status |
|:---|:---|
| `/routes/entity.py` | ✅ Enhanced for v0.1.4 |
| `/routes/maps.py` | ✅ Enhanced for v0P.3B.008 |
| `/routes/device.py` | ❌ Needs Enhancement |
| `/routes/zone.py` | ❌ Needs Enhancement |
| `/routes/trigger.py` | ❌ Needs Enhancement |
| `/routes/vertex.py` | ❌ Needs Enhancement |

(We will progressively update older files.)


## 🔧 Next Steps

- Update `/routes/device.py`, `/routes/zone.py`, `/routes/vertex.py` to match new documentation style.
- When creating new route files, scaffold with full docstring templates.
- Optionally: Create a `docs/api_standards.md` with example boilerplate for developers.


---

# ✅ Summary

FastAPI documentation inside ParcoRTLS is now:
- Clearer
- More complete
- Easier to use
- Future-proof

This supports the project's mission of **developer-friendliness, open-source clarity, and modular RTLS evolution**.

---

# 📖 Reference: Example Route

See `/routes/maps.py` v0P.3B.008 for a model implementation.

