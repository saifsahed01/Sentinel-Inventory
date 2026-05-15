"""
Inventory Routes Blueprint
Handles inventory display and operations.
"""
from flask import Blueprint, render_template, session, current_app, flash, redirect, url_for, request
from src.web.routes.auth import login_required
from src.logic.inventory import ProductNotFoundError, InvalidProductDataError, DuplicateProductError

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


@inventory_bp.route('/inventory/add', methods=['POST'])
@login_required
def add_item():
    """
    Add a new product to the inventory.
    Requires user to be logged in.
    """
    try:
        # Get managers from app config
        inventory_manager = current_app.config['INVENTORY_MANAGER']
        logger = current_app.config['LOGGER']
        
        # Get username from session
        username = session.get('username', 'User')
        
        # Get form data
        name = request.form.get('name', '').strip()
        quantity = request.form.get('quantity', '').strip()
        price = request.form.get('price', '').strip()
        category = request.form.get('category', '').strip()
        
        # Validate required fields
        if not name:
            flash('Product name is required.', 'danger')
            return redirect(url_for('inventory.inventory_list'))
        
        if not quantity:
            flash('Quantity is required.', 'danger')
            return redirect(url_for('inventory.inventory_list'))
        
        if not price:
            flash('Price is required.', 'danger')
            return redirect(url_for('inventory.inventory_list'))
        
        # Add product using InventoryManager
        product = inventory_manager.add_product(
            name=name,
            quantity=quantity,
            price=price,
            category=category if category else None
        )
        
        logger.info(f"Product added successfully", {
            'username': username,
            'product_id': product.id,
            'product_name': product.name
        })
        
        flash(f'Product "{product.name}" added successfully!', 'success')
        return redirect(url_for('inventory.inventory_list'))
        
    except DuplicateProductError as e:
        logger = current_app.config['LOGGER']
        username = session.get('username', 'User')
        logger.warning(f"Duplicate product error: {e}", {'username': username})
        flash(str(e), 'warning')
        return redirect(url_for('inventory.inventory_list'))
        
    except InvalidProductDataError as e:
        logger = current_app.config['LOGGER']
        username = session.get('username', 'User')
        logger.warning(f"Invalid product data: {e}", {'username': username})
        flash(str(e), 'danger')
        return redirect(url_for('inventory.inventory_list'))
        
    except Exception as e:
        logger = current_app.config['LOGGER']
        username = session.get('username', 'User')
        logger.error(f"Error adding product: {e}", {'username': username}, exc_info=True)
        flash('An error occurred while adding the product. Please try again.', 'danger')
        return redirect(url_for('inventory.inventory_list'))


# Made with Bob
