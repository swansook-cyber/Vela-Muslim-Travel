from app.routing import RoutingError


def test_routing_error_is_runtime_error() -> None:
    assert issubclass(RoutingError, RuntimeError)
