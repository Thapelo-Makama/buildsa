from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models import db, MaterialPrice
from app.forms import MaterialForm

materials_bp = Blueprint('materials', __name__)


@materials_bp.route('/')
@login_required
def index():
    province = request.args.get('province', '')
    search = request.args.get('q', '')

    q = MaterialPrice.query
    if province:
        q = q.filter_by(province=province)
    if search:
        q = q.filter(MaterialPrice.material_name.ilike(f'%{search}%'))

    materials = q.order_by(MaterialPrice.created_at.desc()).all()

    # Aggregate: average price per material
    agg = db.session.query(
        MaterialPrice.material_name,
        func.avg(MaterialPrice.price).label('avg_price'),
        func.min(MaterialPrice.price).label('min_price'),
        func.max(MaterialPrice.price).label('max_price'),
        func.count(MaterialPrice.id).label('count')
    ).group_by(MaterialPrice.material_name).all()

    return render_template('feed/materials.html',
                           materials=materials, agg=agg,
                           province=province, search=search)


@materials_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = MaterialForm()
    if form.validate_on_submit():
        m = MaterialPrice(
            material_name=form.material_name.data,
            price=form.price.data,
            unit=form.unit.data,
            supplier=form.supplier.data,
            province=form.province.data,
            city=form.city.data,
            notes=form.notes.data,
            user_id=current_user.id,
        )
        db.session.add(m)
        db.session.commit()
        flash('Price submitted!', 'success')
        return redirect(url_for('materials.index'))
    return render_template('feed/add_material.html', form=form)


@materials_bp.route('/<int:mid>/delete', methods=['POST'])
@login_required
def delete(mid):
    m = MaterialPrice.query.get_or_404(mid)
    if m.user_id != current_user.id and not current_user.is_admin:
        flash('Permission denied.', 'danger')
        return redirect(url_for('materials.index'))
    db.session.delete(m)
    db.session.commit()
    flash('Removed.', 'info')
    return redirect(url_for('materials.index'))
