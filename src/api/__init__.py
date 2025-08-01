"""
API routes and endpoints for the Children's Book Generator.

This module contains all the REST API endpoints organized by functionality
with proper error handling and request validation.
"""

from .routes import create_api_blueprint

__all__ = ["create_api_blueprint"]