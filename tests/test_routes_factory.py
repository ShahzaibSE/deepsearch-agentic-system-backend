import pytest
from fastapi import APIRouter

# Import the function we want to test
from src.app.routes import create_main_router


def test_create_main_router_returns_router():
    """Test that create_main_router returns an APIRouter instance"""
    # Call the function
    router = create_main_router()
    
    # Check that it returns the right type
    assert isinstance(router, APIRouter)


def test_create_main_router_basic_functionality():
    """Test basic functionality - function runs without crashing"""
    # This test just makes sure the function doesn't crash
    # and returns something
    router = create_main_router()
    
    # Basic checks
    assert router is not None
    assert hasattr(router, 'routes')


if __name__ == "__main__":
    # Allow running the test directly
    test_create_main_router_returns_router()
    test_create_main_router_basic_functionality()
    print("All basic tests passed!") 
