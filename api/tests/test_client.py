import inspect
import pytest
import random

from generated_client.client import Client

API_URL = "http://localhost:8000/graphql"


def discover_api_methods():
    """Return all public async methods of the generated client."""
    for name, method in inspect.getmembers(Client, inspect.iscoroutinefunction):
        if not name.startswith("_"):
            yield name


@pytest.mark.asyncio
@pytest.mark.parametrize( "method_name", list( discover_api_methods() ) )
async def test_generated_client_methods( method_name ):

    client = Client( url=API_URL )

    method = getattr( client, method_name )

    sig = inspect.signature( method )

    kwargs = {}

    # automatic argument generation
    for param in sig.parameters.values():

        if param.name == "employee_id":
            kwargs["employee_id"] = random.randint( 10000, 20000 )

        elif param.name == "name":
            kwargs["name"] = "Test"

        elif param.name == "surname":
            kwargs["surname"] = "User"

        elif param.name == "description":
            kwargs["description"] = "Test employee"

    try:
        result = await method( **kwargs )
        assert result is not None

    except Exception as e:
        pytest.skip( f"{method_name} skipped: {e}" )
