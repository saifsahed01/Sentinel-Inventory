"""
Inventory Routes Blueprint
Handles inventory display and operations.
"""
from flask import Blueprint, render_template, session, current_app, flash, redirect, url_for
from src.web.routes.auth import login_required
from src.logic.inventory import ProductNotFoundError, InvalidProductDataError

# Create blueprint
inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/inventory')
@login_required
def inventory_list():
    """
    Display all products in the inventory.
    Requires user to be logged in.
    """
    try:
        # Get managers from app config
        inventory_manager = current_app.config['INVENTORY_MANAGER']
        logger = current_app.config['LOGGER']
        
        # Get username from session
        username = session.get('username', 'User')
        
        # Get all products using InventoryManager
        products = inventory_manager.get_all_products()
        
        # Convert products to list of dicts for template rendering
        products_data = [product.to_dict() for product in products]
        
        logger.debug(f"Inventory page accessed", {
            'username': username,
            'product_count': len(products_data)
        })
        
        return render_template(
            'inventory.html',
            username=username,
            products=products_data
        )
        
    except Exception as e:
        logger = current_app.config['LOGGER']
        logger.error(f"Error loading inventory: {e}", exc_info=True)
        flash('An error occurred while loading the inventory.', 'danger')
        return redirect(url_for('auth.index'))

# Made with Bob
